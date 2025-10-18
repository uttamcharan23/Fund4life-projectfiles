from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.donor import Donor

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']  # Capture phone from form
        password = request.form['password']
        
        existing = Donor.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html')
        
        donor = Donor(
            name=name, 
            email=email, 
            phone=phone,  # Store phone
            password=generate_password_hash(password)
        )
        db.session.add(donor)
        db.session.commit()
        
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        donor = Donor.query.filter_by(email=email).first()
        if donor and check_password_hash(donor.password, password):
            session['donor_id'] = donor.id
            flash('Login successful.', 'success')
            return redirect(url_for('donor.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('donor_id', None)
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))
