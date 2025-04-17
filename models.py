from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint, event, text
import re
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased length for hash
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

class Medicine(db.Model):
    __tablename__ = 'medicine'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    manufacturer = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    reorder_level = db.Column(db.Integer, nullable=False, default=10)
    expiry_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_positive_price'),
        CheckConstraint('stock_quantity >= 0', name='check_positive_stock'),
        db.UniqueConstraint('name', 'manufacturer', name='uq_medicine_name_manufacturer'),
        db.Index('idx_medicine_name_category', 'name', 'category'),
        db.Index('idx_medicine_expiry', 'expiry_date'),
    )
    
    # Define relationships without backrefs
    sales = db.relationship('Sale', back_populates='medicine', lazy='dynamic')
    prescription_items = db.relationship('PrescriptionItem', back_populates='medicine', lazy='dynamic')
    
    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price
    
    @validates('stock_quantity')
    def validate_stock(self, key, quantity):
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        return quantity
    
    @validates('expiry_date')
    def validate_expiry_date(self, key, value):
        if value and value < date.today():
            raise ValueError("Expiry date must be in the future")
        return value
    
    def __repr__(self):
        return f"<Medicine {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update_stock(self, quantity_change):
        self.stock_quantity += quantity_change
        db.session.commit()

class Customer(db.Model):
    __tablename__ = 'customer'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_customer_name', 'name'),
        db.Index('idx_customer_phone', 'phone'),
    )
    
    # Define relationships without backrefs
    sales = db.relationship('Sale', back_populates='customer', lazy='dynamic')
    prescriptions = db.relationship('Prescription', back_populates='customer', lazy='dynamic')
    
    @validates('email')
    def validate_email(self, key, email):
        if email:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                raise ValueError("Invalid email format")
        return email
    
    @validates('phone')
    def validate_phone(self, key, phone):
        if phone:
            pattern = r'^\+?1?\d{9,15}$'
            if not re.match(pattern, phone):
                raise ValueError("Invalid phone number format")
        return phone
    
    def __repr__(self):
        return f"<Customer {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Employee(db.Model):
    __tablename__ = 'employee'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_employee_name', 'name'),
        db.Index('idx_employee_position', 'position'),
    )
    
    # Define relationships without backrefs
    sales = db.relationship('Sale', back_populates='employee')
    
    @validates('email', 'phone')
    def validate_contact(self, key, value):
        if key == 'email' and value:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                raise ValueError("Invalid email format")
        elif key == 'phone' and value:
            pattern = r'^\+?1?\d{9,15}$'
            if not re.match(pattern, value):
                raise ValueError("Invalid phone number format")
        return value
    
    def __repr__(self):
        return f"<Employee {self.name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_supplier_name', 'name'),
    )
    
    @validates('email', 'phone')
    def validate_contact(self, key, value):
        if key == 'email' and value:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                raise ValueError("Invalid email format")
        elif key == 'phone' and value:
            pattern = r'^\+?1?\d{9,15}$'
            if not re.match(pattern, value):
                raise ValueError("Invalid phone number format")
        return value
    
    def __repr__(self):
        return f"<Supplier {self.name}>"

class Prescription(db.Model):
    __tablename__ = 'prescription'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    prescription_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_prescription_date', 'prescription_date'),
        db.Index('idx_prescription_doctor', 'doctor_name'),
    )
    
    # Define relationships without backrefs
    items = db.relationship('PrescriptionItem', back_populates='prescription')

    customer = db.relationship('Customer', back_populates='prescriptions')

    def __repr__(self):
        return f"<Prescription {self.id} for Customer {self.customer_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class PrescriptionItem(db.Model):
    __tablename__ = 'prescription_item'
    
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        db.Index('idx_prescription_item_medicine', 'medicine_id', 'prescription_id'),
    )
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        return quantity
    
    prescription = db.relationship('Prescription', back_populates='items')
    medicine = db.relationship('Medicine', back_populates='prescription_items')
    
    def __repr__(self):
        return f"<PrescriptionItem {self.id} for Prescription {self.prescription_id}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Sale(db.Model):
    __tablename__ = 'sale'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    customer = db.relationship('Customer', back_populates='sales')
    medicine = db.relationship('Medicine', back_populates='sales')
    employee = db.relationship('Employee', back_populates='sales')

    __table_args__ = (
        db.Index('idx_sale_date', 'sale_date'),
        db.Index('idx_sale_customer', 'customer_id'),
    )

    def __repr__(self):
        return f"<Sale {self.id} by {self.customer.name}>"

    def save(self):
        if not self.total_amount:
            self.total_amount = self.quantity * self.unit_price
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id', ondelete='CASCADE'), nullable=False, index=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id', ondelete='RESTRICT'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_positive_quantity'),
        CheckConstraint('price >= 0', name='check_positive_price'),
        db.Index('idx_sale_item_medicine', 'medicine_id', 'sale_id'),
    )
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        medicine = Medicine.query.get(self.medicine_id)
        if medicine and medicine.stock_quantity < quantity:
            raise ValueError(f"Not enough stock. Only {medicine.stock_quantity} units available.")
        return quantity
    
    @validates('price')
    def validate_price(self, key, price):
        if price < 0:
            raise ValueError("Price cannot be negative")
        return price
    
    sale = db.relationship('Sale')
    medicine = db.relationship('Medicine')
    
    def __repr__(self):
        return f"<SaleItem {self.id} for Sale {self.sale_id}>"

# Event listeners for automatic updates
@event.listens_for(Sale, 'before_insert')
@event.listens_for(Sale, 'before_update')
def update_sale_total(mapper, connection, target):
    target.total_amount = sum(item.price * item.quantity for item in target.items)

@event.listens_for(SaleItem, 'after_insert')
def update_stock_after_sale(mapper, connection, target):
    medicine = Medicine.query.get(target.medicine_id)
    if medicine:
        medicine.stock_quantity -= target.quantity

@event.listens_for(SaleItem, 'after_delete')
def restore_stock_after_delete(mapper, connection, target):
    medicine = Medicine.query.get(target.medicine_id)
    if medicine:
        medicine.stock_quantity += target.quantity 