from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.urls import url_parse
from models import User
from forms import LoginForm, RegistrationForm
from extensions import db
import logging

auth = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        logger.info(f"Login attempt for user: {form.username.data}")
        
        user = User.query.filter_by(username=form.username.data).first()
        
        # Log all users in database for debugging
        all_users = User.query.all()
        logger.info(f"All users in database: {[u.username for u in all_users]}")
        
        if user is None:
            logger.warning(f"User not found: {form.username.data}")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
            
        if not user.check_password(form.password.data):
            logger.warning(f"Invalid password for user: {form.username.data}")
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        logger.info(f"Successful login for user: {user.username}")
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login')) 