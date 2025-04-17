from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from extensions import db
from models import Medicine, Customer, Employee, Supplier, Prescription, PrescriptionItem, Sale, SaleItem
from forms import (MedicineForm, CustomerForm, EmployeeForm, SupplierForm,
                   PrescriptionForm, PrescriptionItemForm, SaleForm, SaleItemForm)
from datetime import datetime
from decimal import Decimal

main = Blueprint('main', __name__)

@main.route('/')
def index():
    medicine_count = Medicine.query.count()
    customer_count = Customer.query.count()
    employee_count = Employee.query.count()
    prescription_count = Prescription.query.count()
    sale_count = Sale.query.count()
    
    return render_template('index.html',
                         medicine_count=medicine_count,
                         customer_count=customer_count,
                         employee_count=employee_count,
                         prescription_count=prescription_count,
                         sale_count=sale_count)

@main.route('/medicines')
def medicines():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Medicine.query
    
    if search:
        query = query.filter(
            or_(
                Medicine.name.ilike(f'%{search}%'),
                Medicine.manufacturer.ilike(f'%{search}%'),
                Medicine.category.ilike(f'%{search}%')
            )
        )
    if category:
        query = query.filter(Medicine.category == category)
    
    # Get unique categories for filter dropdown
    categories = db.session.query(Medicine.category).distinct().all()
    
    medicines = query.order_by(Medicine.name).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    return render_template('medicines.html',
                         medicines=medicines,
                         search=search,
                         category=category,
                         categories=categories)

@main.route('/medicines/new', methods=['GET', 'POST'])
def new_medicine():
    form = MedicineForm()
    if form.validate_on_submit():
        medicine = Medicine(
            name=form.name.data,
            description=form.description.data,
            manufacturer=form.manufacturer.data,
            category=form.category.data,
            price=form.price.data,
            expiry_date=form.expiry_date.data,
            stock_quantity=form.stock_quantity.data
        )
        db.session.add(medicine)
        try:
            db.session.commit()
            flash('Medicine added successfully!', 'success')
            return redirect(url_for('main.medicines'))
        except IntegrityError as e:
            db.session.rollback()
            if 'unique' in str(e.orig).lower():
                flash('A medicine with this name and manufacturer already exists.', 'danger')
            else:
                flash('An error occurred while adding the medicine.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the medicine.', 'danger')
    return render_template('medicine_form.html', form=form, title='New Medicine')

@main.route('/medicines/<int:id>', methods=['GET', 'POST'])
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    form = MedicineForm(obj=medicine)
    
    if form.validate_on_submit():
        form.populate_obj(medicine)
        try:
            db.session.commit()
            flash('Medicine updated successfully!', 'success')
            return redirect(url_for('main.medicines'))
        except IntegrityError as e:
            db.session.rollback()
            if 'unique' in str(e.orig).lower():
                flash('A medicine with this name and manufacturer already exists.', 'danger')
            else:
                flash('An error occurred while updating the medicine.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the medicine.', 'danger')
    
    return render_template('medicine_form.html', form=form, title='Edit Medicine')

@main.route('/medicines/<int:id>/delete', methods=['GET', 'POST'])
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    
    # Check if medicine is used in any prescriptions or sales
    if medicine.prescription_items or medicine.sale_items:
        flash('Cannot delete medicine as it is used in prescriptions or sales.', 'danger')
        return redirect(url_for('main.medicines'))
    
    if request.method == 'POST':
        try:
            db.session.delete(medicine)
            db.session.commit()
            flash('Medicine deleted successfully!', 'success')
            return redirect(url_for('main.medicines'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the medicine.', 'danger')
    
    return render_template('delete_confirm.html', 
                         item=medicine,
                         title='Delete Medicine',
                         message=f'Are you sure you want to delete the medicine "{medicine.name}"?')

@main.route('/customers')
def customers():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Customer.query
    
    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Customer.email.ilike(f'%{search}%'),
                Customer.phone.ilike(f'%{search}%')
            )
        )
    
    customers = query.order_by(Customer.name).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    
    return render_template('customers.html',
                         customers=customers,
                         search=search)

@main.route('/customers/new', methods=['GET', 'POST'])
def new_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data
        )
        db.session.add(customer)
        try:
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('main.customers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the customer.', 'danger')
    return render_template('form.html', form=form, title='New Customer')

@main.route('/customers/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    form = CustomerForm(obj=customer)
    
    if form.validate_on_submit():
        form.populate_obj(customer)
        try:
            db.session.commit()
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('main.customers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the customer.', 'danger')
    
    return render_template('form.html', form=form, title='Edit Customer')

@main.route('/customers/<int:id>/delete', methods=['GET', 'POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            db.session.delete(customer)
            db.session.commit()
            flash('Customer deleted successfully!', 'success')
            return redirect(url_for('main.customers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the customer.', 'danger')
    
    return render_template('delete_confirm.html', 
                         item=customer,
                         title='Delete Customer',
                         message=f'Are you sure you want to delete the customer "{customer.name}"?')

@main.route('/employees')
def employees():
    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)

@main.route('/employees/new', methods=['GET', 'POST'])
def new_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            name=form.name.data,
            position=form.position.data,
            phone=form.phone.data,
            email=form.email.data
        )
        db.session.add(employee)
        try:
            db.session.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('main.employees'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the employee.', 'danger')
    return render_template('form.html', form=form, title='New Employee')

@main.route('/employees/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    form = EmployeeForm(obj=employee)
    
    if form.validate_on_submit():
        form.populate_obj(employee)
        try:
            db.session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('main.employees'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the employee.', 'danger')
    
    return render_template('form.html', form=form, title='Edit Employee')

@main.route('/employees/<int:id>/delete', methods=['GET', 'POST'])
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            db.session.delete(employee)
            db.session.commit()
            flash('Employee deleted successfully!', 'success')
            return redirect(url_for('main.employees'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the employee.', 'danger')
    
    return render_template('delete_confirm.html', 
                         item=employee,
                         title='Delete Employee',
                         message=f'Are you sure you want to delete the employee "{employee.name}"?')

@main.route('/prescriptions')
def prescriptions():
    prescriptions = Prescription.query.order_by(Prescription.prescription_date.desc()).all()
    return render_template('prescriptions.html', prescriptions=prescriptions)

@main.route('/prescriptions/new', methods=['GET', 'POST'])
def new_prescription():
    form = PrescriptionForm()
    form.set_customer_choices(Customer.query.order_by(Customer.name).all())
    
    if form.validate_on_submit():
        prescription = Prescription(
            customer_id=form.customer_id.data,
            doctor_name=form.doctor_name.data,
            prescription_date=form.prescription_date.data,
            notes=form.notes.data
        )
        db.session.add(prescription)
        try:
            db.session.commit()
            flash('Prescription created successfully!', 'success')
            return redirect(url_for('main.add_prescription_item', id=prescription.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the prescription.', 'danger')
    
    return render_template('form.html', form=form, title='New Prescription')

@main.route('/prescriptions/<int:id>')
def view_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescription_detail.html', prescription=prescription)

@main.route('/prescriptions/<int:id>/add_item', methods=['GET', 'POST'])
def add_prescription_item(id):
    prescription = Prescription.query.get_or_404(id)
    form = PrescriptionItemForm()
    form.set_medicine_choices(Medicine.query.order_by(Medicine.name).all())
    
    if form.validate_on_submit():
        item = PrescriptionItem(
            prescription_id=prescription.id,
            medicine_id=form.medicine_id.data,
            quantity=form.quantity.data,
            instructions=form.instructions.data
        )
        db.session.add(item)
        try:
            db.session.commit()
            flash('Medicine added to prescription successfully!', 'success')
            return redirect(url_for('main.view_prescription', id=prescription.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the medicine.', 'danger')
    
    return render_template('prescription_item_form.html', 
                         form=form, 
                         prescription=prescription)

@main.route('/prescriptions/<int:id>/item/<int:item_id>/delete', methods=['POST'])
def delete_prescription_item(id, item_id):
    item = PrescriptionItem.query.get_or_404(item_id)
    if item.prescription_id != id:
        flash('Invalid prescription item.', 'danger')
        return redirect(url_for('main.prescriptions'))
    
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Medicine removed from prescription successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while removing the medicine.', 'danger')
    
    return redirect(url_for('main.view_prescription', id=id))

@main.route('/prescriptions/<int:id>/delete', methods=['GET', 'POST'])
def delete_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    if request.method == 'POST':
        try:
            db.session.delete(prescription)
            db.session.commit()
            flash('Prescription deleted successfully!', 'success')
            return redirect(url_for('main.prescriptions'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the prescription.', 'danger')
    
    return render_template('delete_confirm.html',
                         item=prescription,
                         title='Delete Prescription',
                         message=f'Are you sure you want to delete prescription #{prescription.id}?')

@main.route('/sales')
def sales():
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('sales.html', sales=sales)

@main.route('/sales/new', methods=['GET', 'POST'])
def new_sale():
    form = SaleForm()
    form.set_customer_choices(Customer.query.order_by(Customer.name).all())
    form.set_employee_choices(Employee.query.order_by(Employee.name).all())
    form.set_prescription_choices(Prescription.query.order_by(Prescription.prescription_date.desc()).all())
    
    if form.validate_on_submit():
        sale = Sale(
            customer_id=form.customer_id.data,
            employee_id=form.employee_id.data,
            prescription_id=int(form.prescription_id.data) if form.prescription_id.data else None,
            sale_date=form.sale_date.data,
            total_amount=Decimal('0.00')
        )
        db.session.add(sale)
        try:
            db.session.commit()
            flash('Sale created successfully!', 'success')
            return redirect(url_for('main.add_sale_item', id=sale.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while creating the sale.', 'danger')
            print(f"Error creating sale: {str(e)}")
    
    return render_template('form.html', form=form, title='New Sale')

@main.route('/sales/<int:id>')
def view_sale(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sale_detail.html', sale=sale)

@main.route('/sales/<int:id>/add_item', methods=['GET', 'POST'])
def add_sale_item(id):
    sale = Sale.query.get_or_404(id)
    form = SaleItemForm()
    form.set_medicine_choices(Medicine.query.filter(Medicine.stock_quantity > 0).order_by(Medicine.name).all())
    
    if request.method == 'GET' and request.args.get('medicine_id'):
        medicine = Medicine.query.get(request.args.get('medicine_id'))
        if medicine:
            form.set_default_price(medicine)
    
    if form.validate_on_submit():
        medicine = Medicine.query.get(form.medicine_id.data)
        if medicine.stock_quantity < form.quantity.data:
            flash(f'Not enough stock. Only {medicine.stock_quantity} units available.', 'danger')
            return render_template('sale_item_form.html', form=form, sale=sale)
        
        item = SaleItem(
            sale_id=sale.id,
            medicine_id=form.medicine_id.data,
            quantity=form.quantity.data,
            price=form.price.data
        )
        
        # Update medicine stock
        medicine.stock_quantity -= form.quantity.data
        
        # Update sale total
        sale.total_amount += Decimal(str(form.price.data * form.quantity.data))
        
        db.session.add(item)
        try:
            db.session.commit()
            flash('Item added to sale successfully!', 'success')
            return redirect(url_for('main.view_sale', id=sale.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the item.', 'danger')
    
    return render_template('sale_item_form.html', form=form, sale=sale)

@main.route('/sales/<int:id>/item/<int:item_id>/delete', methods=['POST'])
def delete_sale_item(id, item_id):
    item = SaleItem.query.get_or_404(item_id)
    if item.sale_id != id:
        flash('Invalid sale item.', 'danger')
        return redirect(url_for('main.sales'))
    
    try:
        # Restore medicine stock
        medicine = item.medicine
        medicine.stock_quantity += item.quantity
        
        # Update sale total
        sale = item.sale
        sale.total_amount -= Decimal(str(item.price * item.quantity))
        
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from sale successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while removing the item.', 'danger')
    
    return redirect(url_for('main.view_sale', id=id))

@main.route('/sales/<int:id>/delete', methods=['GET', 'POST'])
def delete_sale(id):
    sale = Sale.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # Restore medicine stock for all items
            for item in sale.items:
                item.medicine.stock_quantity += item.quantity
            
            db.session.delete(sale)
            db.session.commit()
            flash('Sale deleted successfully!', 'success')
            return redirect(url_for('main.sales'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the sale.', 'danger')
    
    return render_template('delete_confirm.html',
                         item=sale,
                         title='Delete Sale',
                         message=f'Are you sure you want to delete sale #{sale.id}?')

@main.route('/prescriptions/<int:id>/edit', methods=['GET', 'POST'])
def edit_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    form = PrescriptionForm(obj=prescription)
    form.set_customer_choices(Customer.query.order_by(Customer.name).all())
    
    if form.validate_on_submit():
        form.populate_obj(prescription)
        try:
            db.session.commit()
            flash('Prescription updated successfully!', 'success')
            return redirect(url_for('main.view_prescription', id=prescription.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the prescription.', 'danger')
    
    return render_template('form.html', form=form, title='Edit Prescription')

@main.route('/sales/<int:id>/edit', methods=['GET', 'POST'])
def edit_sale(id):
    sale = Sale.query.get_or_404(id)
    
    # Don't allow editing completed sales
    if sale.items:
        flash('Cannot edit sale with existing items.', 'danger')
        return redirect(url_for('main.view_sale', id=sale.id))
    
    form = SaleForm(obj=sale)
    form.set_customer_choices(Customer.query.order_by(Customer.name).all())
    form.set_employee_choices(Employee.query.order_by(Employee.name).all())
    form.set_prescription_choices(Prescription.query.order_by(Prescription.prescription_date.desc()).all())
    
    if form.validate_on_submit():
        form.populate_obj(sale)
        try:
            db.session.commit()
            flash('Sale updated successfully!', 'success')
            return redirect(url_for('main.view_sale', id=sale.id))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the sale.', 'danger')
    
    return render_template('form.html', form=form, title='Edit Sale')

@main.route('/api/medicines/<int:id>/price')
def get_medicine_price(id):
    medicine = Medicine.query.get_or_404(id)
    return jsonify({
        'price': float(medicine.price),
        'stock_quantity': medicine.stock_quantity
    })

@main.route('/api/medicines/search')
def search_medicines():
    query = request.args.get('q', '')
    medicines = Medicine.query.filter(
        Medicine.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'price': float(m.price),
        'stock_quantity': m.stock_quantity
    } for m in medicines])

@main.route('/suppliers')
def suppliers():
    suppliers = Supplier.query.all()
    return render_template('suppliers.html', suppliers=suppliers)

@main.route('/suppliers/new', methods=['GET', 'POST'])
def new_supplier():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data
        )
        db.session.add(supplier)
        try:
            db.session.commit()
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('main.suppliers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the supplier.', 'danger')
    return render_template('form.html', form=form, title='New Supplier')

@main.route('/suppliers/<int:id>', methods=['GET', 'POST'])
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    form = SupplierForm(obj=supplier)
    
    if form.validate_on_submit():
        form.populate_obj(supplier)
        try:
            db.session.commit()
            flash('Supplier updated successfully!', 'success')
            return redirect(url_for('main.suppliers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the supplier.', 'danger')
    
    return render_template('form.html', form=form, title='Edit Supplier')

@main.route('/suppliers/<int:id>/delete', methods=['GET', 'POST'])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            db.session.delete(supplier)
            db.session.commit()
            flash('Supplier deleted successfully!', 'success')
            return redirect(url_for('main.suppliers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the supplier.', 'danger')
    
    return render_template('delete_confirm.html', 
                         item=supplier,
                         title='Delete Supplier',
                         message=f'Are you sure you want to delete the supplier "{supplier.name}"?') 