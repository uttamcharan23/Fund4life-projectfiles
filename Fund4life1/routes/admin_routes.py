from flask import Blueprint, render_template, session, redirect, url_for, request
from extensions import db
from models.emergency_case import EmergencyCase

admin_bp = Blueprint('admin_bp', __name__, template_folder='../templates')

# Admin dashboard
@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('user_role') != 'admin':
        return redirect(url_for('admin_bp.login'))

    pending_cases = EmergencyCase.query.filter_by(status='Pending').all()
    return render_template('admin_dashboard.html', pending_cases=pending_cases)

# Admin login
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # For demo, we can hardcode admin credentials
        if email == 'admin@fund4life.com' and password == 'admin123':
            session['logged_in'] = True
            session['user_role'] = 'admin'
            session['user_id'] = 1
            return redirect(url_for('admin_bp.dashboard'))
    return render_template('admin_login.html')

# Approve NGO for a case
@admin_bp.route('/approve_ngo/<int:case_id>/<int:ngo_id>')
def approve_ngo(case_id, ngo_id):
    case = EmergencyCase.query.get(case_id)
    case.ngo_id = ngo_id
    case.status = 'NGO_Approved'
    db.session.commit()
    return redirect(url_for('admin_bp.dashboard'))

# Release fund
@admin_bp.route('/release_fund/<int:case_id>')
def release_fund(case_id):
    case = EmergencyCase.query.get(case_id)
    if case.status == 'Volunteer_Confirmed':
        case.status = 'Fund_Released'
        db.session.commit()
    return redirect(url_for('admin_bp.dashboard'))
