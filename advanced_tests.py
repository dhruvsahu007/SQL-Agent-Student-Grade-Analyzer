"""
Advanced test cases for the SQL Agent
"""

from sql_agent import StudentGradeAnalyzer
from create_database import create_database
import os
import json

def run_advanced_tests():
    """Run comprehensive tests for the SQL Agent"""
    
    print("=== Advanced SQL Agent Tests ===\n")
    
    # Ensure database exists
    if not os.path.exists("student_grades.db"):
        create_database()
    
    # Initialize agent
    try:
        analyzer = StudentGradeAnalyzer()
        print("Agent initialized successfully!\n")
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test categories
    test_categories = {
        "Basic Queries": [
            "What grades did Alice get?",
            "Show me Bob's scores",
            "List all students"
        ],
        
        "Aggregation Queries": [
            "What is the average grade in Math?",
            "Who has the highest grade overall?",
            "What's the minimum grade in Science?",
            "Count how many students got above 85"
        ],
        
        "Complex Queries": [
            "Which student has the best average grade?",
            "Show me students who failed any subject (below 60)",
            "What's the grade distribution in English?",
            "Who improved the most from Math to Science?"
        ],
        
        "Edge Cases": [
            "Show me students named XYZ",  # Non-existent student
            "What grades did everyone get in History?",  # Non-existent subject
            "List all grades above 100",  # Impossible grade
            ""  # Empty query
        ],
        
        "Ambiguous Queries": [
            "Who is the best student?",
            "Show me bad grades",
            "What about Alice?",
            "Give me some statistics"
        ]
    }
    
    # Run tests by category
    total_tests = 0
    successful_tests = 0
    
    for category, queries in test_categories.items():
        print(f"\n{'='*50}")
        print(f"Category: {category}")
        print('='*50)
        
        for query in queries:
            total_tests += 1
            print(f"\nQuery: '{query}'")
            print("-" * 30)
            
            try:
                debug_info = analyzer.get_debug_info(query)
                
                print(f"SQL Generated: {debug_info['generated_sql']}")
                print(f"Valid: {debug_info['validation_result']}")
                
                if debug_info['error']:
                    print(f"Error: {debug_info['error']}")
                else:
                    print(f"Results Count: {len(debug_info['query_results']) if debug_info['query_results'] else 0}")
                    successful_tests += 1
                
                print(f"Response: {debug_info['final_response']}")
                
            except Exception as e:
                print(f"Exception: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("Test Summary")
    print('='*50)
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")

def test_error_handling():
    """Test error handling and recovery"""
    
    print("\n=== Error Handling Tests ===\n")
    
    # Test with invalid database path
    print("Testing with invalid database path...")
    invalid_analyzer = StudentGradeAnalyzer(db_path="nonexistent.db")
    result = invalid_analyzer.run("What grades did Alice get?")
    print(f"Result: {result}")
    
    # Test with malformed queries
    print("\nTesting malformed queries...")
    analyzer = StudentGradeAnalyzer()
    
    malformed_queries = [
        "DROP TABLE students;",  # Dangerous query
        "INSERT INTO students VALUES (1, 'Hacker', 'Math', 100);",  # Insert attempt
        "SELECT * FROM nonexistent_table;",  # Non-existent table
        "SELET * FORM students;",  # Typos in SQL
    ]
    
    for query in malformed_queries:
        print(f"\nTesting: '{query}'")
        result = analyzer.run(query)
        print(f"Response: {result}")

def benchmark_performance():
    """Simple performance benchmark"""
    
    print("\n=== Performance Benchmark ===\n")
    
    import time
    
    analyzer = StudentGradeAnalyzer()
    test_query = "What grades did Alice get?"
    
    # Warm up
    analyzer.run(test_query)
    
    # Benchmark
    num_runs = 5
    start_time = time.time()
    
    for i in range(num_runs):
        result = analyzer.run(test_query)
    
    end_time = time.time()
    
    avg_time = (end_time - start_time) / num_runs
    print(f"Average response time: {avg_time:.2f} seconds")
    print(f"Queries per minute: {60/avg_time:.1f}")

if __name__ == "__main__":
    run_advanced_tests()
    test_error_handling()
    benchmark_performance()
