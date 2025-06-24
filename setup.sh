#!/bin/bash

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3 before proceeding." >&2
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment." >&2
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment." >&2
    exit 1
fi

# Check for requirements file
if [ ! -f "requirements.txt" ]; then
    echo "WARNING: requirements.txt not found. No dependencies will be installed." >&2
else
    # Install dependencies
    echo "Installing dependencies from requirements.txt..."
    pip install -q --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies." >&2
        exit 1
    fi
fi

echo -e "\nEnvironment setup completed successfully!"
echo "To start the application:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Run the application: ./run.sh"
