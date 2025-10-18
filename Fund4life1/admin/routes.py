from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from extensions import db
from models.ngo import NGO
from models.emergency_case import EmergencyCase
from models.donor import Donor
from models.donation import Donation
from models.verification_report import VerificationReport
import os
from flask import send_from_directory

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ADMIN_EMAIL = 'admin@fund4life.com'
ADMIN_PASSWORD = 'admin123'

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Admin login required.', 'danger')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin login successful.', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Invalid admin credentials.', 'danger')
    return render_template('admin/admin_login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logged out.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_donations = db.session.query(db.func.sum(Donation.amount)).scalar() or 0
    donors = Donor.query.count()
    ngos = NGO.query.count()
    cases = EmergencyCase.query.count()
    return render_template('admin/dashboard.html', total_donations=total_donations, donors=donors, ngos=ngos, cases=cases)

@admin_bp.route('/ngo_approvals', methods=['GET', 'POST'])
@admin_required
def ngo_approvals():
    ngos = NGO.query.all()
    if request.method == 'POST':
        ngo_id = request.form['ngo_id']
        action = request.form['action']
        ngo = NGO.query.get(ngo_id)
        if ngo:
            ngo.is_approved = (action == 'approve')
            db.session.commit()
            flash(f"NGO {'approved' if action == 'approve' else 'rejected'}.", 'success')
    return render_template('admin/ngo_approvals.html', ngos=ngos)

@admin_bp.route('/cases', methods=['GET', 'POST'])
@admin_required
def cases():
    all_cases = EmergencyCase.query.all()
    ngos = NGO.query.filter_by(is_approved=True).all()
    if request.method == 'POST':
        case_id = request.form['case_id']
        assigned_ngo = request.form.get('assigned_ngo')
        action = request.form['action']
        case = EmergencyCase.query.get(case_id)
        if case:
            if action == 'assign' and assigned_ngo:
                case.assigned_ngo = int(assigned_ngo)
                case.status = 'Assigned'
            elif action == 'approve':
                case.status = 'Approved'
            elif action == 'reject':
                case.status = 'Rejected'
            db.session.commit()
            flash('Case updated.', 'success')
    return render_template('admin/cases.html', cases=all_cases, ngos=ngos)

@admin_bp.route('/approve_funds/<int:case_id>', methods=['POST'])
@admin_required
def approve_funds(case_id):
    case = EmergencyCase.query.get_or_404(case_id)
    amount = request.form.get('amount', type=float)
    if amount is None or amount <= 0:
        flash('Please enter a valid amount.', 'danger')
        return redirect(url_for('admin.cases'))
    # Update case amount and mark funds as released
    case.amount = amount
    case.status = 'Funds Released'
    db.session.commit()
    flash('Funds approved and successfully sent to recipient.', 'success')
    return redirect(url_for('admin.cases'))

@admin_bp.route('/verification_reports')
@admin_required
def verification_reports():
    reports = VerificationReport.query.all()
    return render_template('admin/verification_reports.html', reports=reports)

@admin_bp.route('/verification_report/<int:report_id>')
@admin_required
def verification_report_details(report_id):
    report = VerificationReport.query.get_or_404(report_id)
    return render_template('admin/verification_report_details.html', report=report)

@admin_bp.route('/uploads/<path:filename>')
@admin_required
def uploaded_file(filename):
    uploads = os.path.join(current_app.root_path, 'static', 'verification_uploads')
    return send_from_directory(uploads, filename)
