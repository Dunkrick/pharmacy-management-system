from app import create_app
from extensions import db
from models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    app = create_app()
    
    with app.app_context():
        try:
            # Check if admin exists
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                logger.info("Admin user already exists")
                # Update admin password
                admin.set_password('admin123')
                db.session.commit()
                logger.info("Admin password updated")
            else:
                # Create new admin user
                admin = User(
                    username='admin',
                    email='admin@pharmacy.com',
                    is_admin=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                logger.info("Admin user created successfully")
            
            # Verify admin user
            admin = User.query.filter_by(username='admin').first()
            if admin and admin.check_password('admin123'):
                logger.info("Admin credentials verified successfully")
            else:
                logger.error("Admin credentials verification failed")
                
        except Exception as e:
            logger.error(f"Error creating admin user: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_admin_user() 