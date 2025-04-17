from app import create_app
from extensions import db
from models import User
from datetime import datetime

def reset_admin():
    app = create_app()
    
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@pharmacy.com',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")

if __name__ == '__main__':
    reset_admin() 