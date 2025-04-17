from flask import Flask
from extensions import db, login_manager, migrate, csrf
from flask_migrate import Migrate
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from commands import create_admin
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    
    # Database configuration
    if os.environ.get('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    else:
        # Local SQLite database
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'pharmacy.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import models to ensure they're known to Flask-SQLAlchemy
        from models import User
        
        # Import routes here to avoid circular imports
        from routes.main import main as main_blueprint
        from routes.auth import auth as auth_blueprint
        
        # Register blueprints
        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint)
        
        # Create database tables
        db.create_all()
    
    # Template filters
    @app.template_filter('current_year')
    def current_year_filter(text):
        return datetime.now().year
        
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.now()
        return dict(now=now)
    
    # Register the command
    app.cli.add_command(create_admin)
    
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/pharmacy.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Pharmacy startup')
    
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run() 