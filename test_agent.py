from sql_agent import StudentGradeAnalyzer
from create_database import create_database
import os

def test_sql_agent():
    """Test the SQL Agent with various queries"""
    
    print("=== SQL Agent: Student Grade Analyzer Test ===\n")
    
    # Create database if it doesn't exist
    if not os.path.exists("student_grades.db"):
        print("Creating database...")
        create_database()
        print()
    
    # Initialize the agent
    print("Initializing SQL Agent...")
    try:
        analyzer = StudentGradeAnalyzer()
        print("Agent initialized successfully!\n")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Please make sure you have set up your OpenAI API key in .env file")
        return
    
    # Test queries
    test_queries = [
        "What grades did Alice get?",
        "Who got the highest grade in Math?",
        "What is the average grade for Science?",
        "List all students who got above 90",
        "How many students are in the database?",
        "What subjects are available?",
        "Who got the lowest grade in English?",
        "Show me all grades for Bob"
    ]
    
    print("Testing various queries...\n")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            # Get debug information
            debug_info = analyzer.get_debug_info(query)
            
            print(f"Generated SQL: {debug_info['generated_sql']}")
            print(f"Validation: {'✓ Valid' if debug_info['validation_result'] else '✗ Invalid'}")
            
            if debug_info['error']:
                print(f"Error: {debug_info['error']}")
            else:
                print(f"Query Results: {debug_info['query_results']}")
            
            print(f"Response: {debug_info['final_response']}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("Testing completed!")
    
    # Interactive mode
    print("\nEntering interactive mode. Type 'quit' to exit.")
    while True:
        user_query = input("\nEnter your question about student grades: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_query:
            continue
        
        try:
            response = analyzer.run(user_query)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("Goodbye!")

if __name__ == "__main__":
    test_sql_agent()
