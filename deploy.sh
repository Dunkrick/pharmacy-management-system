#!/bin/bash

echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create instance directory if it doesn't exist
echo "Creating instance directory..."
mkdir -p instance

# Initialize database
echo "Initializing database..."
export FLASK_APP=app.py
flask db init || true
flask db migrate -m "Initial migration"
flask db upgrade

# Start the application
echo "Starting application..."
gunicorn wsgi:app --log-level debug 