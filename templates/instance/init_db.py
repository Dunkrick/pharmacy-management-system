from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

def init_db():
    # Create instance directory if it doesn't exist
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    with app.app_context():
        # Import models to ensure they are known to SQLAlchemy
        from models import Medicine, Customer, Employee, Supplier
        from models import Prescription, PrescriptionItem, Sale, SaleItem
        
        # Create all tables
        db.create_all()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
