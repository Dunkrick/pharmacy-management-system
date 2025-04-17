from app import create_app
from extensions import db
from models import User
from datetime import datetime

def reset_database():
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("Creating all tables...")
        db.create_all()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@pharmacy.com',
            is_admin=True
        )
        admin.set_password('admin123')
        admin.save()
        
        print("Database has been reset and admin user created successfully!")

if __name__ == '__main__':
    reset_database() 