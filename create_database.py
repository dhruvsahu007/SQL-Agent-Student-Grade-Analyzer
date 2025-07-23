import sqlite3
import os

def create_database():
    """Create and populate the student grades database"""
    
    # Create database file
    db_path = "student_grades.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            grade INTEGER NOT NULL
        )
    ''')
    
    # Insert sample data
    sample_data = [
        ('Alice', 'Math', 85),
        ('Alice', 'Science', 78),
        ('Alice', 'English', 92),
        ('Bob', 'Math', 92),
        ('Bob', 'Science', 88),
        ('Bob', 'English', 79),
        ('Charlie', 'Math', 76),
        ('Charlie', 'Science', 94),
        ('Charlie', 'English', 85),
        ('Diana', 'Math', 88),
        ('Diana', 'Science', 91),
        ('Diana', 'English', 87),
        ('Eve', 'Math', 79),
        ('Eve', 'Science', 82),
        ('Eve', 'English', 90),
        ('Frank', 'Math', 95),
        ('Frank', 'Science', 89),
        ('Frank', 'English', 83),
        ('Grace', 'Math', 82),
        ('Grace', 'Science', 86),
        ('Grace', 'English', 94),
        ('Henry', 'Math', 77),
        ('Henry', 'Science', 79),
        ('Henry', 'English', 81)
    ]
    
    cursor.executemany('''
        INSERT INTO students (name, subject, grade) VALUES (?, ?, ?)
    ''', sample_data)
    
    # Commit changes
    conn.commit()
    
    print("Database created successfully with sample data!")
    print("\nSample data preview:")
    cursor.execute("SELECT * FROM students LIMIT 10")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Name: {row[1]}, Subject: {row[2]}, Grade: {row[3]}")
    
    # Close connection
    conn.close()
    
    return db_path

if __name__ == "__main__":
    create_database()
