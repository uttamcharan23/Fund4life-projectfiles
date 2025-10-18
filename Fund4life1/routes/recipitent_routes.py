from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from extensions import db
from models.recipitent import Recipient

recipient_bp = Blueprint('recipient_bp', __name__, template_folder='../templates')

# Recipient Dashboard
@recipient_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('user_role') != 'recipient':
        return redirect(url_for('recipient_bp.login'))
    
    recipient_id = session.get('user_id')
    recipient = Recipient.query.get(recipient_id)
    return render_template('recipient_dashboard.html', recipient=recipient)

# Recipient Registration
@recipient_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Check if email already exists
        existing = Recipient.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered.")
            return redirect(url_for('recipient_bp.register'))

        recipient = Recipient(name=name, email=email)
        recipient.set_password(password)
        db.session.add(recipient)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for('recipient_bp.login'))

    return render_template('recipient_register.html')

# Recipient Login
@recipient_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        recipient = Recipient.query.filter_by(email=email).first()
        if recipient and recipient.check_password(password):
            session['logged_in'] = True
            session['user_role'] = 'recipient'
            session['user_id'] = recipient.id
            return redirect(url_for('recipient_bp.dashboard'))
        else:
            flash("Invalid email or password.")
            return redirect(url_for('recipient_bp.login'))

    return render_template('recipient_login.html')
