from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.volunteer import Volunteer

volunteer_auth_bp = Blueprint('volunteer_auth', __name__, url_prefix='/volunteer/auth')

@volunteer_auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        existing = Volunteer.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('volunteer/register.html')
        
        hashed_password = generate_password_hash(password)
        volunteer = Volunteer(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password
        )
        db.session.add(volunteer)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('volunteer_auth.login'))
    return render_template('volunteer/register.html')

@volunteer_auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        volunteer = Volunteer.query.filter_by(email=email).first()
        if volunteer and check_password_hash(volunteer.password, password):
            session['volunteer_id'] = volunteer.id
            flash('Login successful.', 'success')
            return redirect(url_for('volunteer.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('volunteer/login.html')

@volunteer_auth_bp.route('/logout')
def logout():
    session.pop('volunteer_id', None)
    flash('Logged out.', 'info')
    return redirect(url_for('volunteer_auth.login'))
