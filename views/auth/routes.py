from flask import  render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from forms import RegistrationForm, LoginForm
from . import auth_bp
from utils import hash_password, verify_password
from werkzeug.security import generate_password_hash, check_password_hash



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Prevent duplicate registrations
        if User.query.filter_by(email=form.email.data).first():
            flash('User already exists, please login', 'warning')
            return redirect(url_for('auth.login'))

        # O(1) check: first_user is None only once
        is_first = User.query.first() is None
        role = 'Admin' if is_first else 'User'

        # Create and commit new user
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hash_password(form.password.data),
            is_active=True,
            role=role
        )
        db.session.add(user)
        db.session.commit()

        flash('Account created—check your email to confirm.', 'success')
        if is_first:
            flash('You have been granted Admin privileges.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)



@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login; redirect Admins to admin dashboard and Users to main dashboard.
    """
    if current_user.is_authenticated:
        return redirect(url_for('admin.list_groups') if current_user.role == 'Admin' else url_for('main.dashboard'))
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if  user.is_blacklisted:
            flash('Your account has been banned.', 'danger')

        if user and verify_password(user.password, form.password.data):
            flash('Logged in successfully', 'success')
            login_user(user, remember=form.remember.data)

            # Role-based redirect
            if user.role == 'Admin':
                return redirect(url_for('admin.list_groups'))
            return redirect(url_for('main.dashboard'))
            flash('Login unsuccessful. Check email and password.', 'danger')

    return render_template('auth/login.html', form=form)



@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))