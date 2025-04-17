from flask import Flask
from config import Config
from extensions import db, migrate, limiter
from datetime import datetime

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Add template filters
    @app.template_filter('current_year')
    def current_year_filter(text):
        return datetime.now().year

    with app.app_context():
        # Import routes
        from routes import main as main_blueprint
        app.register_blueprint(main_blueprint)
        
        # Create tables if they don't exist
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 