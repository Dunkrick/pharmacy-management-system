from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError, Regexp
from wtforms.fields import DateField, DateTimeField
from datetime import date, datetime
import re
from bleach import clean

def sanitize_string(value):
    """Sanitize string input to prevent XSS"""
    if value:
        return clean(value, strip=True)
    return value

class BaseForm(FlaskForm):
    """Base form class with CSRF protection and common methods"""
    class Meta:
        csrf = True  # Enable CSRF protection by default
        csrf_time_limit = 3600  # 1 hour

    def _sanitize_data(self):
        """Sanitize form data before validation"""
        for field in self._fields.values():
            if isinstance(field.data, str):
                field.data = sanitize_string(field.data)

    def validate(self):
        """Override validate to include sanitization"""
        self._sanitize_data()
        return super().validate()

class LoginForm(BaseForm):
    username = StringField('Username', 
        validators=[
            DataRequired(),
            Length(min=4, max=80),
            Regexp(r'^[\w.@+-]+$', message="Username can only contain letters, numbers, and @/./+/-/_ characters")
        ])
    password = PasswordField('Password', 
        validators=[
            DataRequired(),
            Length(min=8, max=128),
            Regexp(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])',
                message="Password must contain at least one uppercase letter, one lowercase letter, one number and one special character")
        ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')

class MedicineForm(BaseForm):
    name = StringField('Medicine Name', 
        validators=[
            DataRequired(),
            Length(max=100),
            Regexp(r'^[\w\s\-\']+$', message="Medicine name can only contain letters, numbers, spaces, hyphens and apostrophes")
        ])
    description = TextAreaField('Description',
        validators=[Length(max=500)])
    manufacturer = StringField('Manufacturer', 
        validators=[
            DataRequired(),
            Length(max=100),
            Regexp(r'^[\w\s\-\'&]+$', message="Manufacturer name can only contain letters, numbers, spaces, hyphens, ampersands and apostrophes")
        ])
    category = SelectField('Category',
        choices=[
            ('antibiotics', 'Antibiotics'),
            ('analgesics', 'Analgesics'),
            ('antiviral', 'Antiviral'),
            ('antihistamine', 'Antihistamine'),
            ('cardiovascular', 'Cardiovascular'),
            ('diabetes', 'Diabetes'),
            ('supplements', 'Supplements'),
            ('other', 'Other')
        ],
        validators=[DataRequired()])
    price = DecimalField('Price',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=999999.99, message="Price must be between 0 and 999,999.99")
        ],
        places=2)
    expiry_date = DateField('Expiry Date',
        validators=[DataRequired()])
    stock_quantity = IntegerField('Stock Quantity',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=999999, message="Stock quantity must be between 0 and 999,999")
        ],
        default=0)
    reorder_level = IntegerField('Reorder Level',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=999999, message="Reorder level must be between 0 and 999,999")
        ],
        default=10)

    def validate_expiry_date(self, field):
        if field.data <= date.today():
            raise ValidationError('Expiry date must be in the future')

class CustomerForm(BaseForm):
    name = StringField('Customer Name', 
        validators=[
            DataRequired(),
            Length(max=100),
            Regexp(r'^[\w\s\-\']+$', message="Name can only contain letters, numbers, spaces, hyphens and apostrophes")
        ])
    address = TextAreaField('Address',
        validators=[
            Optional(),
            Length(max=200)
        ])
    phone = StringField('Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            Regexp(r'^\+?[\d\s\-()]+$', message="Invalid phone number format")
        ])
    email = StringField('Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=100)
        ])

    def validate_phone(self, field):
        # Remove all non-digit characters for validation
        digits = re.sub(r'\D', '', field.data)
        if not 8 <= len(digits) <= 15:
            raise ValidationError('Phone number must be between 8 and 15 digits')

class EmployeeForm(BaseForm):
    name = StringField('Employee Name',
        validators=[
            DataRequired(),
            Length(max=100),
            Regexp(r'^[\w\s\-\']+$', message="Name can only contain letters, numbers, spaces, hyphens and apostrophes")
        ])
    position = SelectField('Position',
        choices=[
            ('pharmacist', 'Pharmacist'),
            ('technician', 'Pharmacy Technician'),
            ('cashier', 'Cashier'),
            ('manager', 'Manager'),
            ('assistant', 'Assistant'),
            ('intern', 'Intern')
        ],
        validators=[DataRequired()])
    phone = StringField('Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            Regexp(r'^\+?[\d\s\-()]+$', message="Invalid phone number format")
        ])
    email = StringField('Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=100)
        ])
    submit = SubmitField('Save')

    def validate_phone(self, field):
        # Remove all non-digit characters for validation
        digits = re.sub(r'\D', '', field.data)
        if not 8 <= len(digits) <= 15:
            raise ValidationError('Phone number must be between 8 and 15 digits')

class SupplierForm(BaseForm):
    name = StringField('Supplier Name',
        validators=[
            DataRequired(),
            Length(max=100),
            Regexp(r'^[\w\s\-\'&]+$', message="Name can only contain letters, numbers, spaces, hyphens, ampersands and apostrophes")
        ])
    address = TextAreaField('Address',
        validators=[
            Optional(),
            Length(max=200)
        ])
    phone = StringField('Phone Number',
        validators=[
            DataRequired(),
            Length(max=20),
            Regexp(r'^\+?[\d\s\-()]+$', message="Invalid phone number format")
        ])
    email = StringField('Email',
        validators=[
            DataRequired(),
            Email(),
            Length(max=100)
        ])

    def validate_phone(self, field):
        # Remove all non-digit characters for validation
        digits = re.sub(r'\D', '', field.data)
        if not 8 <= len(digits) <= 15:
            raise ValidationError('Phone number must be between 8 and 15 digits')

class PrescriptionForm(BaseForm):
    customer_id = SelectField('Customer', 
        coerce=int,
        validators=[DataRequired()])
    doctor_name = StringField('Doctor Name',
        validators=[
            DataRequired(),
            Length(max=100),
            Regexp(r'^[Dr\.\s]*[\w\s\-\']+$', message="Doctor name can only contain letters, spaces, hyphens and apostrophes, optionally prefixed with 'Dr.'")
        ])
    prescription_date = DateField('Prescription Date',
        validators=[DataRequired()],
        default=date.today)
    notes = TextAreaField('Notes',
        validators=[
            Optional(),
            Length(max=500)
        ])

    def validate_prescription_date(self, field):
        if field.data > date.today():
            raise ValidationError('Prescription date cannot be in the future')

    def set_customer_choices(self, customers):
        self.customer_id.choices = [(c.id, c.name) for c in customers]

class PrescriptionItemForm(BaseForm):
    medicine_id = SelectField('Medicine',
        coerce=int,
        validators=[DataRequired()])
    quantity = IntegerField('Quantity',
        validators=[
            DataRequired(),
            NumberRange(min=1, max=9999, message="Quantity must be between 1 and 9,999")
        ],
        default=1)
    instructions = TextAreaField('Instructions',
        validators=[
            DataRequired(),
            Length(max=500)
        ])

    def set_medicine_choices(self, medicines):
        self.medicine_id.choices = [(m.id, f"{m.name} ({m.manufacturer})") for m in medicines]

    def validate_quantity(self, field):
        if hasattr(self, 'medicine') and self.medicine and field.data > self.medicine.stock_quantity:
            raise ValidationError(f'Quantity exceeds available stock ({self.medicine.stock_quantity})')

class SaleForm(BaseForm):
    customer_id = SelectField('Customer',
        coerce=int,
        validators=[DataRequired()])
    employee_id = SelectField('Employee',
        coerce=int,
        validators=[DataRequired()])
    prescription_id = SelectField('Prescription',
        coerce=str,
        validators=[Optional()],
        default='')
    sale_date = DateTimeField('Sale Date',
        validators=[DataRequired()],
        default=datetime.now)

    def validate_sale_date(self, field):
        if field.data > datetime.now():
            raise ValidationError('Sale date cannot be in the future')

    def set_customer_choices(self, customers):
        self.customer_id.choices = [(c.id, c.name) for c in customers]

    def set_employee_choices(self, employees):
        self.employee_id.choices = [(e.id, f"{e.name} ({e.position})") for e in employees]

    def set_prescription_choices(self, prescriptions):
        self.prescription_id.choices = [('', 'No Prescription')] + \
            [(str(p.id), f"#{p.id} - {p.customer.name} ({p.prescription_date.strftime('%Y-%m-%d')})") 
             for p in prescriptions]

class SaleItemForm(BaseForm):
    medicine_id = SelectField('Medicine',
        coerce=int,
        validators=[DataRequired()])
    quantity = IntegerField('Quantity',
        validators=[
            DataRequired(),
            NumberRange(min=1, max=9999, message="Quantity must be between 1 and 9,999")
        ],
        default=1)
    price = DecimalField('Price per Unit',
        validators=[
            DataRequired(),
            NumberRange(min=0, max=999999.99, message="Price must be between 0 and 999,999.99")
        ],
        places=2)

    def set_medicine_choices(self, medicines):
        self.medicine_id.choices = [(m.id, f"{m.name} (Stock: {m.stock_quantity})") for m in medicines]

    def set_default_price(self, medicine):
        if medicine:
            self.price.data = medicine.price

    def validate_quantity(self, field):
        if hasattr(self, 'medicine') and self.medicine and field.data > self.medicine.stock_quantity:
            raise ValidationError(f'Quantity exceeds available stock ({self.medicine.stock_quantity})') 