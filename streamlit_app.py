"""
Streamlit web interface for the SQL Agent
"""

import streamlit as st
import pandas as pd
from sql_agent import StudentGradeAnalyzer
from create_database import create_database
import os
import sqlite3

def load_database_preview():
    """Load a preview of the database"""
    if not os.path.exists("student_grades.db"):
        return None
    
    conn = sqlite3.connect("student_grades.db")
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    return df

def main():
    st.set_page_config(
        page_title="SQL Agent: Student Grade Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 SQL Agent: Student Grade Analyzer")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.write("""
        This is a LangGraph-based SQL agent that converts natural language 
        questions about student grades into SQL queries.
        """)
        
        st.header("Sample Questions")
        st.write("""
        - What grades did Alice get?
        - Who got the highest grade in Math?
        - What is the average grade for Science?
        - List all students who got above 90
        - How many students are in each subject?
        """)
        
        if st.button("🔄 Reset Database"):
            if os.path.exists("student_grades.db"):
                os.remove("student_grades.db")
            create_database()
            st.success("Database reset successfully!")
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("Ask a Question")
        
        # Initialize agent
        if 'analyzer' not in st.session_state:
            try:
                if not os.path.exists("student_grades.db"):
                    with st.spinner("Creating database..."):
                        create_database()
                
                with st.spinner("Initializing SQL Agent..."):
                    st.session_state.analyzer = StudentGradeAnalyzer()
                st.success("Agent initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing agent: {e}")
                st.stop()
        
        # Query input
        query = st.text_input(
            "Enter your question about student grades:",
            placeholder="What grades did Alice get?",
            key="query_input"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            ask_button = st.button("🔍 Ask", type="primary")
        
        with col_btn2:
            debug_button = st.button("🐛 Debug")
        
        # Process query
        if ask_button and query:
            with st.spinner("Processing your question..."):
                try:
                    response = st.session_state.analyzer.run(query)
                    st.success("Response:")
                    st.write(response)
                except Exception as e:
                    st.error(f"Error: {e}")
        
        if debug_button and query:
            with st.spinner("Getting debug information..."):
                try:
                    debug_info = st.session_state.analyzer.get_debug_info(query)
                    
                    st.subheader("Debug Information")
                    
                    with st.expander("Generated SQL", expanded=True):
                        st.code(debug_info['generated_sql'], language='sql')
                    
                    with st.expander("Validation Result"):
                        if debug_info['validation_result']:
                            st.success("✅ SQL is valid")
                        else:
                            st.error("❌ SQL is invalid")
                    
                    if debug_info['error']:
                        with st.expander("Error"):
                            st.error(debug_info['error'])
                    
                    if debug_info['query_results']:
                        with st.expander("Raw Results"):
                            st.json(debug_info['query_results'])
                    
                    with st.expander("Final Response"):
                        st.write(debug_info['final_response'])
                        
                except Exception as e:
                    st.error(f"Error: {e}")
    
    with col2:
        st.header("Database Preview")
        
        # Show database preview
        df = load_database_preview()
        if df is not None:
            st.dataframe(df, use_container_width=True)
            
            # Basic statistics
            st.subheader("Quick Stats")
            st.metric("Total Records", len(df))
            st.metric("Unique Students", df['name'].nunique())
            st.metric("Subjects", df['subject'].nunique())
            st.metric("Average Grade", f"{df['grade'].mean():.1f}")
            
        else:
            st.warning("Database not found. Click 'Reset Database' to create it.")
    
    # Query history
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if query and ask_button:
        st.session_state.query_history.append(query)
        # Keep only last 10 queries
        st.session_state.query_history = st.session_state.query_history[-10:]
    
    if st.session_state.query_history:
        st.header("Recent Queries")
        for i, hist_query in enumerate(reversed(st.session_state.query_history), 1):
            if st.button(f"{i}. {hist_query}", key=f"hist_{i}"):
                st.session_state.query_input = hist_query
                st.rerun()

if __name__ == "__main__":
    main()
