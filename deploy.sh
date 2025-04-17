#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init || true
flask db migrate -m "Initial migration"
flask db upgrade

# Start the application
gunicorn wsgi:app 