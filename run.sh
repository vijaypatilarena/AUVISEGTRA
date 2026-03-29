#!/bin/bash
# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "💡 Activating project virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ Warning: 'venv' not found. Please run ./setup.sh first to install dependencies."
fi

# Run the Streamlit app
echo "🎯 Launching Streamlit..."
streamlit run app.py
