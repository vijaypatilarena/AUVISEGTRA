#!/bin/bash
echo "🚀 Initializing AUVISEGTRA Setup..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📑 Installing dependencies from requirements.txt..."
echo "Note: This may take a few minutes as it includes heavy libraries (torch, ultralytics)..."
pip install -r requirements.txt

echo "✅ Setup complete! You can now run the app using ./run.sh"
