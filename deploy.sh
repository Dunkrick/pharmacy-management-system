#!/bin/bash

echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create instance directory if it doesn't exist
mkdir -p instance

# Clean up unnecessary files
echo "Cleaning up unnecessary files..."
python cleanup.py

# Initialize database and create admin user
echo "Initializing database and creating admin user..."
python init_db.py

# Start the application
echo "Starting application..."
gunicorn wsgi:app --log-level debug 