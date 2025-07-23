from typing import TypedDict, Optional, List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import sqlite3
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class StudentGradeState(TypedDict):
    """State schema for the Student Grade Analyzer agent"""
    query: str                    # Original natural language question
    sql_query: Optional[str]      # Generated SQL query
    validation_result: Optional[bool]  # SQL validation status
    query_result: Optional[List[Dict[str, Any]]]  # Database query results
    response: Optional[str]       # Final human-readable response
    error: Optional[str]          # Error message if any

class StudentGradeAnalyzer:
    """SQL Agent that analyzes student grades using LangGraph"""
    
    def __init__(self, db_path: str = "student_grades.db"):
        self.db_path = db_path
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Database schema for context
        self.schema_info = """
        Database Schema:
        Table: students
        Columns:
        - id (INTEGER PRIMARY KEY): Unique student record ID
        - name (TEXT): Student name
        - subject (TEXT): Subject name (Math, Science, English)
        - grade (INTEGER): Grade score (0-100)
        
        Sample data:
        - Alice has grades: Math=85, Science=78, English=92
        - Bob has grades: Math=92, Science=88, English=79
        """
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(StudentGradeState)
        
        # Add nodes
        workflow.add_node("parse_query", self.parse_query)
        workflow.add_node("validate_sql", self.validate_sql)
        workflow.add_node("execute_query", self.execute_query)
        workflow.add_node("generate_response", self.generate_response)
        
        # Add edges
        workflow.add_edge(START, "parse_query")
        workflow.add_edge("parse_query", "validate_sql")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "validate_sql",
            self._validation_condition,
            {
                "valid": "execute_query",
                "invalid": "generate_response"  # Changed to go to response instead of infinite loop
            }
        )
        
        workflow.add_conditional_edges(
            "execute_query",
            self._execution_condition,
            {
                "success": "generate_response",
                "error": "generate_response"
            }
        )
        
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    def parse_query(self, state: StudentGradeState) -> StudentGradeState:
        """Node 1: Convert natural language to SQL"""
        
        prompt = f"""
        Convert the following natural language question into a SQL query for the student grades database.
        
        {self.schema_info}
        
        Question: {state['query']}
        
        Rules:
        1. Only use SELECT statements
        2. Use the exact table and column names provided
        3. Return only the SQL query without any explanation
        4. Use proper SQL syntax
        
        SQL Query:
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            sql_query = response.content.strip()
            
            # Clean up the SQL query
            sql_query = re.sub(r'^```sql\s*', '', sql_query)
            sql_query = re.sub(r'\s*```$', '', sql_query)
            sql_query = sql_query.strip()
            
            return {
                **state,
                "sql_query": sql_query,
                "error": None
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Error parsing query: {str(e)}"
            }
    
    def validate_sql(self, state: StudentGradeState) -> StudentGradeState:
        """Node 2: Validate SQL query syntax"""
        
        if state.get("error"):
            return state
        
        sql_query = state.get("sql_query", "").strip()
        
        try:
            # Basic validation
            if not sql_query:
                return {
                    **state,
                    "validation_result": False,
                    "error": "Empty SQL query generated"
                }
            
            # Remove trailing semicolon if present
            if sql_query.endswith(';'):
                sql_query = sql_query[:-1].strip()
            
            # Check if it's a SELECT statement
            if not sql_query.upper().strip().startswith("SELECT"):
                return {
                    **state,
                    "validation_result": False,
                    "error": "Only SELECT statements are allowed"
                }
            
            # Check for dangerous keywords
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            sql_upper = sql_query.upper()
            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    return {
                        **state,
                        "validation_result": False,
                        "error": f"Dangerous SQL keyword '{keyword}' detected"
                    }
            
            # Try to parse the SQL using sqlite3
            conn = sqlite3.connect(":memory:")
            cursor = conn.cursor()
            
            # Create a temporary table to test the query
            cursor.execute('''
                CREATE TABLE students (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    subject TEXT,
                    grade INTEGER
                )
            ''')
            
            # Insert a dummy row to test the query
            cursor.execute("INSERT INTO students (id, name, subject, grade) VALUES (1, 'Test', 'Math', 85)")
            
            # Try to execute the statement to test it
            try:
                cursor.execute(sql_query)
                cursor.fetchall()  # Actually fetch to ensure query works
            except Exception as exec_error:
                conn.close()
                return {
                    **state,
                    "validation_result": False,
                    "error": f"SQL execution test failed: {str(exec_error)}"
                }
            
            conn.close()
            
            # Update the state with the cleaned SQL query (without semicolon)
            return {
                **state,
                "sql_query": sql_query,
                "validation_result": True,
                "error": None
            }
            
        except Exception as e:
            return {
                **state,
                "validation_result": False,
                "error": f"SQL validation error: {str(e)}"
            }
    
    def execute_query(self, state: StudentGradeState) -> StudentGradeState:
        """Node 3: Execute SQL query on the database"""
        
        if state.get("error") or not state.get("validation_result"):
            return state
        
        sql_query = state.get("sql_query", "")
        
        try:
            # Check if database exists
            if not os.path.exists(self.db_path):
                return {
                    **state,
                    "error": f"Database not found: {self.db_path}. Please run create_database.py first."
                }
            
            # Execute the query
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to list of dictionaries
            query_result = []
            for row in results:
                query_result.append(dict(zip(column_names, row)))
            
            conn.close()
            
            return {
                **state,
                "query_result": query_result,
                "error": None
            }
            
        except Exception as e:
            return {
                **state,
                "error": f"Query execution error: {str(e)}"
            }
    
    def generate_response(self, state: StudentGradeState) -> StudentGradeState:
        """Node 4: Generate human-readable response"""
        
        if state.get("error"):
            return {
                **state,
                "response": f"Sorry, I encountered an error: {state['error']}"
            }
        
        query_result = state.get("query_result", [])
        original_query = state.get("query", "")
        
        if not query_result:
            return {
                **state,
                "response": "No results found for your query."
            }
        
        prompt = f"""
        Convert the following SQL query results into a natural, human-readable response.
        
        Original Question: {original_query}
        SQL Results: {query_result}
        
        Provide a clear, conversational response that directly answers the user's question.
        If there are multiple results, format them in a readable way.
        
        Response:
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            return {
                **state,
                "response": response.content.strip()
            }
            
        except Exception as e:
            return {
                **state,
                "response": f"Error generating response: {str(e)}"
            }
    
    def _validation_condition(self, state: StudentGradeState) -> str:
        """Conditional edge after validation"""
        if state.get("validation_result"):
            return "valid"
        else:
            return "invalid"
    
    def _execution_condition(self, state: StudentGradeState) -> str:
        """Conditional edge after execution"""
        if state.get("error"):
            return "error"
        else:
            return "success"
    
    def run(self, query: str) -> str:
        """Run the agent with a natural language query"""
        
        initial_state = StudentGradeState(
            query=query,
            sql_query=None,
            validation_result=None,
            query_result=None,
            response=None,
            error=None
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return result.get("response", "No response generated")
    
    def get_debug_info(self, query: str) -> Dict[str, Any]:
        """Run the agent and return debug information"""
        
        initial_state = StudentGradeState(
            query=query,
            sql_query=None,
            validation_result=None,
            query_result=None,
            response=None,
            error=None
        )
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "original_query": result.get("query"),
            "generated_sql": result.get("sql_query"),
            "validation_result": result.get("validation_result"),
            "query_results": result.get("query_result"),
            "final_response": result.get("response"),
            "error": result.get("error")
        }

if __name__ == "__main__":
    # Example usage
    analyzer = StudentGradeAnalyzer()
    
    # Test query
    test_query = "What grades did Alice get?"
    result = analyzer.run(test_query)
    print(f"Query: {test_query}")
    print(f"Response: {result}")
