from flask import Flask
from extensions import db, login_manager, migrate, csrf
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev')
    # Update the database path to be explicit
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'pharmacy.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
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
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 