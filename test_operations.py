from app import create_app
from extensions import db
from models import Medicine, Customer, Employee, Prescription, Sale
from datetime import datetime, date, timedelta
import unittest

class TestDatabaseOperations(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_medicine_crud(self):
        # Create with future expiry date
        future_date = date.today() + timedelta(days=365)
        medicine = Medicine(
            name='Test Medicine',
            description='Test Description',
            manufacturer='Test Manufacturer',
            category='Test Category',
            price=10.0,
            stock_quantity=100,
            reorder_level=10,
            expiry_date=future_date
        )
        db.session.add(medicine)
        db.session.commit()
        
        # Read
        saved_medicine = Medicine.query.filter_by(name='Test Medicine').first()
        self.assertIsNotNone(saved_medicine)
        self.assertEqual(saved_medicine.price, 10.0)
        
        # Update
        saved_medicine.price = 15.0
        db.session.commit()
        updated_medicine = Medicine.query.get(saved_medicine.id)
        self.assertEqual(updated_medicine.price, 15.0)
        
        # Delete
        db.session.delete(saved_medicine)
        db.session.commit()
        deleted_medicine = Medicine.query.get(saved_medicine.id)
        self.assertIsNone(deleted_medicine)

    def test_customer_crud(self):
        # Create
        customer = Customer(
            name='Test Customer',
            email='test@example.com',
            phone='1234567890',
            address='Test Address'
        )
        db.session.add(customer)
        db.session.commit()
        
        # Read
        saved_customer = Customer.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(saved_customer)
        
        # Update
        saved_customer.phone = '0987654321'
        db.session.commit()
        updated_customer = Customer.query.get(saved_customer.id)
        self.assertEqual(updated_customer.phone, '0987654321')
        
        # Delete
        db.session.delete(saved_customer)
        db.session.commit()
        deleted_customer = Customer.query.get(saved_customer.id)
        self.assertIsNone(deleted_customer)

    def test_sale_creation(self):
        # Create test data
        medicine = Medicine(
            name='Test Medicine',
            manufacturer='Test Manufacturer',
            category='Test Category',
            price=10.0,
            stock_quantity=100,
            reorder_level=10,
            expiry_date=date(2025, 1, 1)
        )
        customer = Customer(
            name='Test Customer',
            email='test@example.com',
            phone='1234567890',
            address='Test Address'
        )
        employee = Employee(
            name='Test Employee',
            email='employee@example.com',
            phone='1234567890',
            position='Pharmacist',
            hire_date=date(2023, 1, 1)
        )
        
        db.session.add_all([medicine, customer, employee])
        db.session.commit()
        
        # Create sale
        sale = Sale(
            customer_id=customer.id,
            medicine_id=medicine.id,
            employee_id=employee.id,
            quantity=5,
            unit_price=10.0,
            total_amount=50.0,
            sale_date=date.today()
        )
        
        db.session.add(sale)
        db.session.commit()
        
        # Verify sale
        saved_sale = Sale.query.get(sale.id)
        self.assertIsNotNone(saved_sale)
        self.assertEqual(saved_sale.total_amount, 50.0)

if __name__ == '__main__':
    unittest.main() 