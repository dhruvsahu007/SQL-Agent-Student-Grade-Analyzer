#!/bin/bash

echo "Setting up SQL Agent: Student Grade Analyzer"
echo

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating database..."
python create_database.py

echo
echo "Setup complete!"
echo
echo "To run the agent:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set your OpenAI API key in .env file"
echo "3. Run: python test_agent.py"
echo
echo "To run the web interface:"
echo "streamlit run streamlit_app.py"
echo
