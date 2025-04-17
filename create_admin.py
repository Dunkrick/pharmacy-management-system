from app import create_app
from extensions import db
from models import User

def create_admin_user(username, email, password):
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User {username} already exists!")
            return

        # Create new admin user
        try:
            admin = User(
                username=username,
                email=email,
                is_admin=True
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user {username} created successfully!")
        except Exception as e:
            print(f"Error creating admin user: {str(e)}")

if __name__ == '__main__':
    create_admin_user('admin', 'admin@example.com', 'admin123') 