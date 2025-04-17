from flask import Flask
from extensions import db
from models import User
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    app = Flask(__name__)
    
    # Database configuration
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'pharmacy.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database
    db.init_app(app)
    
    with app.app_context():
        try:
            # Create all tables
            logger.info("Creating database tables...")
            db.create_all()
            
            # Check if admin exists
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                logger.info("Creating admin user...")
                admin = User(
                    username='admin',
                    email='admin@pharmacy.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully!")
            else:
                logger.info("Admin user already exists")
                # Update admin password
                admin.set_password('admin123')
                db.session.commit()
                logger.info("Admin password updated")
            
            # Verify admin user
            admin = User.query.filter_by(username='admin').first()
            if admin and admin.check_password('admin123'):
                logger.info("Admin credentials verified successfully")
                logger.info(f"Admin user details: {admin.username}, {admin.email}")
            else:
                logger.error("Admin credentials verification failed")
                
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_database() 