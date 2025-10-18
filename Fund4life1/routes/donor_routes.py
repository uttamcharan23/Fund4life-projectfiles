from flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import db
from models.donor import Donor
from models.emergency_case import EmergencyCase
from models.donation import Donation

donor_bp = Blueprint('donor_bp', __name__, template_folder='../templates')

# Donor dashboard
@donor_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('user_role') != 'donor':
        return redirect(url_for('home'))
    donor_id = session.get('user_id')
    donations = Donation.query.filter_by(donor_id=donor_id).all()
    emergencies = EmergencyCase.query.filter_by(donor_id=donor_id).all()
    return render_template('donor_dashboard.html', donations=donations, emergencies=emergencies)

# Donor register
@donor_bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        donor = Donor(name=name, email=email)
        donor.set_password(password)
        db.session.add(donor)
        db.session.commit()
        return redirect(url_for('donor_bp.login'))
    return render_template('donor_register.html')

# Donor login
@donor_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        donor = Donor.query.filter_by(email=email).first()
        if donor and donor.check_password(password):
            session['logged_in'] = True
            session['user_role'] = 'donor'
            session['user_id'] = donor.id
            return redirect(url_for('donor_bp.dashboard'))
    return render_template('donor_login.html')

# Submit emergency case
@donor_bp.route('/submit_emergency', methods=['GET','POST'])
def submit_emergency():
    if not session.get('logged_in') or session.get('user_role') != 'donor':
        return redirect(url_for('home'))
    if request.method == 'POST':
        amount = float(request.form['amount'])
        description = request.form['description']
        donor_id = session['user_id']
        case = EmergencyCase(donor_id=donor_id, amount_required=amount, description=description, status='Pending')
        db.session.add(case)
        db.session.commit()
        return redirect(url_for('donor_bp.dashboard'))
    return render_template('submit_emergency.html')
