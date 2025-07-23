# SQL Agent: Student Grade Analyzer

A LangGraph-based SQL agent that converts natural language questions about student grades into SQL queries and returns human-readable responses.

## Features

- Natural language to SQL conversion
- SQL query validation
- Database query execution
- Error handling with conditional edges
- Human-readable response generation

## Database Schema

The agent works with a simple student grades database:

```sql
students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    subject TEXT,
    grade INTEGER
)
```

## Architecture

### State
- `query`: Original natural language question
- `sql_query`: Generated SQL query
- `validation_result`: SQL validation status
- `query_result`: Database query results
- `response`: Final human-readable response
- `error`: Error message if any

### Nodes
1. **Parse Query** - Convert natural language to SQL
2. **Validate SQL** - Check query syntax
3. **Execute Query** - Run SQL on the database
4. **Generate Response** - Convert results to natural language

### Edges
- START → Parse Query → Validate SQL → Execute Query → Generate Response → END
- Conditional edges for error handling

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

```python
from sql_agent import StudentGradeAnalyzer

# Initialize the agent
agent = StudentGradeAnalyzer()

# Ask questions
result = agent.run("What grades did Alice get?")
print(result)
```

## Example Queries

- "What grades did Alice get?"
- "Who got the highest grade in Math?"
- "What is the average grade for Science?"
- "List all students who got above 80"

## Testing

Run the test file to see the agent in action:

```bash
python test_agent.py
```
