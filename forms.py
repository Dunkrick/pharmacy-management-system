from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DecimalField, IntegerField, SelectField, BooleanField, FloatField, EmailField, TelField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, ValidationError, Regexp, EqualTo
from wtforms.fields import DateField, DateTimeField
from datetime import date, datetime
import re

def clean_data(data):
    if data:
        # Simple HTML tag removal
        return str(data).replace('<', '&lt;').replace('>', '&gt;')
    return data

class BaseForm(FlaskForm):
    """Base form class with CSRF protection and common methods"""
    class Meta:
        csrf = True  # Enable CSRF protection by default
        csrf_time_limit = 3600  # 1 hour

    def _sanitize_data(self):
        """Sanitize form data before validation"""
        for field in self._fields.values():
            if isinstance(field.data, str):
                field.data = clean_data(field.data)

    def validate(self):
        """Override validate to include sanitization"""
        self._sanitize_data()
        return super().validate()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def clean_data(self, field_data):
        # Simple cleaning without bleach
        return str(field_data).strip()

class MedicineForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description')
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    category = StringField('Category', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    reorder_level = IntegerField('Reorder Level', validators=[DataRequired(), NumberRange(min=0)])
    expiry_date = DateField('Expiry Date', validators=[DataRequired()])

    def validate_expiry_date(self, field):
        if field.data < date.today():
            raise ValidationError('Expiry date must be in the future')

class CustomerForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    address = TextAreaField('Address', validators=[DataRequired()])

class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    hire_date = DateField('Hire Date', validators=[DataRequired()])

class PrescriptionForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    doctor_name = StringField('Doctor Name', validators=[DataRequired()])
    prescription_date = DateField('Prescription Date', validators=[DataRequired()])
    notes = TextAreaField('Notes')

class SaleForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    medicine_id = SelectField('Medicine', coerce=int, validators=[DataRequired()])
    employee_id = SelectField('Employee', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, message='Quantity must be at least 1')
    ])
    sale_date = DateField('Sale Date', default=date.today, validators=[DataRequired()])

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