from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import Medicine, Customer, Employee, Prescription, Sale, PrescriptionItem
from forms import MedicineForm, CustomerForm, EmployeeForm, PrescriptionForm, SaleForm
from extensions import db, limiter
from sqlalchemy import or_, desc
from datetime import datetime
# Import your other dependencies

main = Blueprint('main', __name__)

@main.route('/')
@login_required
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
@login_required
@limiter.limit("60 per minute")  # Adjust rate as needed
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
@login_required
def new_medicine():
    form = MedicineForm()
    if form.validate_on_submit():
        try:
            medicine = Medicine(
                name=form.name.data,
                description=form.description.data,
                manufacturer=form.manufacturer.data,
                category=form.category.data,
                price=form.price.data,
                stock_quantity=form.stock_quantity.data,
                reorder_level=form.reorder_level.data,
                expiry_date=form.expiry_date.data
            )
            db.session.add(medicine)
            db.session.commit()
            flash('Medicine added successfully!', 'success')
            return redirect(url_for('main.medicines'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding medicine: {str(e)}', 'danger')
            print(f"Error: {str(e)}")  # For debugging
    
    # If there are form errors, flash them
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return render_template('medicine_form.html', form=form, title='New Medicine')

@main.route('/medicines/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    form = MedicineForm(obj=medicine)
    
    if form.validate_on_submit():
        form.populate_obj(medicine)
        try:
            db.session.commit()
            flash('Medicine updated successfully!', 'success')
            return redirect(url_for('main.medicines'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the medicine.', 'danger')
    
    return render_template('medicine_form.html', form=form, title='Edit Medicine')

@main.route('/medicines/<int:id>/delete', methods=['POST'])
@login_required
def delete_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    try:
        db.session.delete(medicine)
        db.session.commit()
        flash('Medicine deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the medicine.', 'danger')
    
    return redirect(url_for('main.medicines'))

@main.route('/customers')
@login_required
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
    
    customers = query.order_by(Customer.name).paginate(page=page, per_page=10, error_out=False)
    return render_template('customers.html', customers=customers, search=search)

@main.route('/customers/new', methods=['GET', 'POST'])
@login_required
def new_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data
        )
        db.session.add(customer)
        try:
            db.session.commit()
            flash('Customer added successfully!', 'success')
            return redirect(url_for('main.customers'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the customer.', 'danger')
    
    return render_template('customer_form.html', form=form, title='New Customer')

@main.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
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
    
    return render_template('customer_form.html', form=form, title='Edit Customer')

@main.route('/customers/<int:id>/delete', methods=['POST'])
@login_required
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    try:
        db.session.delete(customer)
        db.session.commit()
        flash('Customer deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the customer.', 'danger')
    
    return redirect(url_for('main.customers'))

@main.route('/employees')
@login_required
def employees():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Employee.query
    if search:
        query = query.filter(
            or_(
                Employee.name.ilike(f'%{search}%'),
                Employee.email.ilike(f'%{search}%'),
                Employee.position.ilike(f'%{search}%')
            )
        )
    
    employees = query.order_by(Employee.name).paginate(page=page, per_page=10, error_out=False)
    return render_template('employees.html', employees=employees, search=search)

@main.route('/employees/new', methods=['GET', 'POST'])
@login_required
def new_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            position=form.position.data,
            hire_date=form.hire_date.data
        )
        db.session.add(employee)
        try:
            db.session.commit()
            flash('Employee added successfully!', 'success')
            return redirect(url_for('main.employees'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the employee.', 'danger')
    
    return render_template('employee_form.html', form=form, title='New Employee')

@main.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
@login_required
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
    
    return render_template('employee_form.html', form=form, title='Edit Employee')

@main.route('/employees/<int:id>/delete', methods=['POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('Employee deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the employee.', 'danger')
    
    return redirect(url_for('main.employees'))

@main.route('/prescriptions')
@login_required
def prescriptions():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Prescription.query
    if search:
        query = query.join(Customer).filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Prescription.doctor_name.ilike(f'%{search}%')
            )
        )
    
    prescriptions = query.order_by(desc(Prescription.prescription_date)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('prescriptions.html', prescriptions=prescriptions, search=search)

@main.route('/prescriptions/new', methods=['GET', 'POST'])
@login_required
def new_prescription():
    form = PrescriptionForm()
    # Populate customer choices
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    
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
            flash('Prescription added successfully!', 'success')
            return redirect(url_for('main.prescriptions'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the prescription.', 'danger')
    
    return render_template('prescription_form.html', form=form, title='New Prescription')

@main.route('/prescriptions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    form = PrescriptionForm(obj=prescription)
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    
    if form.validate_on_submit():
        form.populate_obj(prescription)
        try:
            db.session.commit()
            flash('Prescription updated successfully!', 'success')
            return redirect(url_for('main.prescriptions'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the prescription.', 'danger')
    
    return render_template('prescription_form.html', form=form, title='Edit Prescription')

@main.route('/prescriptions/<int:id>/delete', methods=['POST'])
@login_required
def delete_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    try:
        db.session.delete(prescription)
        db.session.commit()
        flash('Prescription deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the prescription.', 'danger')
    
    return redirect(url_for('main.prescriptions'))

@main.route('/prescriptions/<int:id>/view')
@login_required
def view_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    return render_template('prescription_view.html', prescription=prescription)

@main.route('/sales')
@login_required
def sales():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Sale.query
    if search:
        query = query.join(Customer).filter(
            or_(
                Customer.name.ilike(f'%{search}%'),
                Sale.invoice_number.ilike(f'%{search}%')
            )
        )
    
    sales = query.order_by(desc(Sale.sale_date)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template('sales.html', sales=sales, search=search)

@main.route('/sales/new', methods=['GET', 'POST'])
@login_required
def new_sale():
    form = SaleForm()
    
    # Populate form choices
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    form.medicine_id.choices = [(m.id, f"{m.name} - Stock: {m.stock_quantity}") 
                              for m in Medicine.query.filter(Medicine.stock_quantity > 0).order_by(Medicine.name).all()]
    form.employee_id.choices = [(e.id, e.name) for e in Employee.query.order_by(Employee.name).all()]

    if form.validate_on_submit():
        try:
            # Get the medicine to check stock and price
            medicine = Medicine.query.get_or_404(form.medicine_id.data)
            
            # Validate stock availability
            if medicine.stock_quantity < form.quantity.data:
                flash(f'Not enough stock. Only {medicine.stock_quantity} units available.', 'danger')
                return render_template('sale_form.html', form=form, title='New Sale')

            # Create new sale
            sale = Sale(
                customer_id=form.customer_id.data,
                medicine_id=form.medicine_id.data,
                employee_id=form.employee_id.data,
                quantity=form.quantity.data,
                unit_price=medicine.price,
                total_amount=medicine.price * form.quantity.data,
                sale_date=form.sale_date.data or datetime.now().date()
            )

            # Update medicine stock
            medicine.stock_quantity -= form.quantity.data

            # Save changes
            db.session.add(sale)
            db.session.commit()

            flash('Sale created successfully!', 'success')
            return redirect(url_for('main.sales'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sale: {str(e)}', 'danger')
            app.logger.error(f'Error creating sale: {str(e)}')

    return render_template('sale_form.html', form=form, title='New Sale')

@main.route('/sales/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sale(id):
    sale = Sale.query.get_or_404(id)
    form = SaleForm(obj=sale)
    
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.order_by(Customer.name).all()]
    form.medicine_id.choices = [(m.id, f"{m.name} (Stock: {m.stock_quantity})") 
                              for m in Medicine.query.order_by(Medicine.name).all()]
    
    if form.validate_on_submit():
        # Restore original stock
        original_medicine = Medicine.query.get(sale.medicine_id)
        original_medicine.stock_quantity += sale.quantity
        
        # Update with new values
        new_medicine = Medicine.query.get(form.medicine_id.data)
        if new_medicine.stock_quantity < form.quantity.data:
            flash('Not enough stock available.', 'danger')
            return render_template('sale_form.html', form=form, title='Edit Sale')
        
        sale.customer_id = form.customer_id.data
        sale.medicine_id = form.medicine_id.data
        sale.quantity = form.quantity.data
        sale.sale_date = form.sale_date.data
        sale.unit_price = new_medicine.price
        sale.total_amount = new_medicine.price * form.quantity.data
        
        # Update new medicine stock
        new_medicine.stock_quantity -= form.quantity.data
        
        try:
            db.session.commit()
            flash('Sale updated successfully!', 'success')
            return redirect(url_for('main.sales'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the sale.', 'danger')
    
    return render_template('sale_form.html', form=form, title='Edit Sale')

@main.route('/sales/<int:id>/delete', methods=['POST'])
@login_required
def delete_sale(id):
    sale = Sale.query.get_or_404(id)
    
    # Restore stock quantity
    medicine = Medicine.query.get(sale.medicine_id)
    medicine.stock_quantity += sale.quantity
    
    try:
        db.session.delete(sale)
        db.session.commit()
        flash('Sale deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the sale.', 'danger')
    
    return redirect(url_for('main.sales'))

@main.route('/sales/<int:id>/view')
@login_required
def view_sale(id):
    sale = Sale.query.get_or_404(id)
    return render_template('sale_view.html', sale=sale)

# Your other routes... 