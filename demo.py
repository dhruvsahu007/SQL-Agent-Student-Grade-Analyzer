"""
Demonstration script for the SQL Agent: Student Grade Analyzer
"""

from sql_agent import StudentGradeAnalyzer
import json

def demonstrate_sql_agent():
    """Comprehensive demonstration of the SQL Agent capabilities"""
    
    print("🎓 SQL Agent: Student Grade Analyzer - Demonstration")
    print("=" * 60)
    
    # Initialize the agent
    print("\n📚 Initializing the SQL Agent...")
    try:
        agent = StudentGradeAnalyzer()
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Demonstration queries with expected outcomes
    demo_queries = [
        {
            "category": "🔍 Individual Student Queries",
            "queries": [
                "What grades did Alice get?",
                "Show me all of Bob's scores",
                "How did Charlie perform in Science?"
            ]
        },
        {
            "category": "📊 Statistical Queries", 
            "queries": [
                "What is the average grade in Math?",
                "Who got the highest grade overall?",
                "What's the lowest score in English?"
            ]
        },
        {
            "category": "🎯 Filtering Queries",
            "queries": [
                "List all students who scored above 90",
                "Show me students who failed any subject (below 60)",
                "Which students got exactly 85 points?"
            ]
        },
        {
            "category": "🔢 Aggregation Queries",
            "queries": [
                "How many students are in each subject?",
                "What subjects are available?",
                "Count total number of grades recorded"
            ]
        }
    ]
    
    # Run demonstrations
    for category_info in demo_queries:
        print(f"\n{category_info['category']}")
        print("-" * 50)
        
        for query in category_info["queries"]:
            print(f"\n💭 Question: '{query}'")
            
            try:
                # Get debug info for detailed view
                debug_info = agent.get_debug_info(query)
                
                print(f"🔧 Generated SQL: {debug_info['generated_sql']}")
                print(f"✅ Validation: {'Valid' if debug_info['validation_result'] else 'Invalid'}")
                
                if debug_info['error']:
                    print(f"❌ Error: {debug_info['error']}")
                else:
                    print(f"📋 Results: {len(debug_info['query_results'])} record(s) found")
                
                print(f"💬 Response: {debug_info['final_response']}")
                
            except Exception as e:
                print(f"❌ Exception: {e}")
            
            print()
    
    # Test error handling
    print("\n🛡️ Error Handling Demonstration")
    print("-" * 50)
    
    error_test_queries = [
        "DROP TABLE students",  # Dangerous SQL
        "INSERT INTO students VALUES (100, 'Hacker', 'Math', 100)",  # Insert attempt
        "What grades did XYZ get?",  # Non-existent student
        "",  # Empty query
    ]
    
    for query in error_test_queries:
        print(f"\n🧪 Testing: '{query}'")
        try:
            result = agent.run(query)
            print(f"🔄 Response: {result}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    # Performance test
    print(f"\n⚡ Performance Test")
    print("-" * 50)
    
    import time
    test_query = "What grades did Alice get?"
    
    start_time = time.time()
    result = agent.run(test_query)
    end_time = time.time()
    
    print(f"⏱️ Query: '{test_query}'")
    print(f"🏃 Response Time: {(end_time - start_time):.2f} seconds")
    print(f"📝 Result: {result}")
    
    # Architecture summary
    print(f"\n🏗️ Architecture Summary")
    print("-" * 50)
    print("📋 State Components:")
    print("   • query: Original natural language question")
    print("   • sql_query: Generated SQL query")
    print("   • validation_result: SQL validation status")
    print("   • query_result: Database query results")
    print("   • response: Final human-readable response")
    print("   • error: Error message if any")
    
    print("\n🔄 Processing Nodes:")
    print("   1. Parse Query: Convert natural language to SQL")
    print("   2. Validate SQL: Check query syntax and safety")
    print("   3. Execute Query: Run SQL on database")
    print("   4. Generate Response: Convert results to natural language")
    
    print("\n🛤️ Graph Flow:")
    print("   START → Parse Query → Validate SQL → Execute Query → Generate Response → END")
    print("   • Conditional: Invalid SQL → Generate Response (error)")
    print("   • Conditional: Query Error → Generate Response (error)")
    
    print(f"\n🎉 Demonstration Complete!")
    print("🌐 To try the web interface, run: streamlit run streamlit_app.py")
    print("🧪 To run comprehensive tests, run: python advanced_tests.py")

if __name__ == "__main__":
    demonstrate_sql_agent()
