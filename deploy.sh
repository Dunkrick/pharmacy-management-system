#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init || true
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
python reset_admin.py

# Start the application
gunicorn wsgi:app 