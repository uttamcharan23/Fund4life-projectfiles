from flask import Blueprint, render_template, session, redirect, url_for, request
from extensions import db
from models.volunteer import Volunteer
from models.emergency_case import EmergencyCase

volunteer_bp = Blueprint('volunteer_bp', __name__, template_folder='../templates')

# Volunteer dashboard
@volunteer_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('user_role') != 'volunteer':
        return redirect(url_for('volunteer_bp.login'))
    
    cases = EmergencyCase.query.filter_by(status='NGO_Approved').all()
    return render_template('volunteer_dashboard.html', cases=cases)

# Volunteer login
@volunteer_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        volunteer = Volunteer.query.filter_by(email=email).first()
        if volunteer and volunteer.password == password:  # Simplified password check
            session['logged_in'] = True
            session['user_role'] = 'volunteer'
            session['user_id'] = volunteer.id
            return redirect(url_for('volunteer_bp.dashboard'))
    return render_template('volunteer_login.html')

# Volunteer confirms a case
@volunteer_bp.route('/confirm_case/<int:case_id>')
def confirm_case(case_id):
    if not session.get('logged_in') or session.get('user_role') != 'volunteer':
        return redirect(url_for('volunteer_bp.login'))

    case = EmergencyCase.query.get(case_id)
    if case and case.status == 'NGO_Approved':
        case.status = 'Volunteer_Confirmed'
        db.session.commit()
    return redirect(url_for('volunteer_bp.dashboard'))
