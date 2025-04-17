import os
from datetime import timedelta

# Get the absolute path of the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Flask configuration
    SECRET_KEY = 'your-secret-key-here'
    
    # SQLAlchemy configuration
    # Use absolute path for the database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "pharmacy.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Flask-Limiter
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Security
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # Set to True in production with HTTPS
    REMEMBER_COOKIE_HTTPONLY = True 