#!/bin/bash

echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Remove existing database and migrations
echo "Cleaning up existing database..."
rm -f instance/pharmacy.db
rm -rf migrations

# Initialize database
echo "Initializing database..."
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
echo "Creating admin user..."
python create_admin.py

# Start the application
echo "Starting application..."
gunicorn wsgi:app 