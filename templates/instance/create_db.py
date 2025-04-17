from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

def init_db():
    app = Flask(__name__)
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    
    # Create instance directory if it doesn't exist
    instance_path = os.path.join(os.path.dirname(__file__), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    with app.app_context():
        # Import models
        from models import Medicine, Customer, Employee, Supplier
        from models import Prescription, PrescriptionItem, Sale, SaleItem
        
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
