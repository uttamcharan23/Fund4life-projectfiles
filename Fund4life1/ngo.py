from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from extensions import db
from models.ngo import NGO
from werkzeug.security import generate_password_hash, check_password_hash
from models.volunteer import Volunteer
from models.verification_report import VerificationReport
from models.emergency_case import EmergencyCase

# Define the blueprint
ngo_bp = Blueprint('ngo', __name__, url_prefix='/ngo')

@ngo_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        description = request.form['description']
        password = request.form['password']

        if NGO.query.filter_by(email=email).first():
            flash("Email already registered", "danger")
            return render_template('ngo/register.html')

        hashed_password = generate_password_hash(password)
        ngo = NGO(name=name, email=email, description=description, password=hashed_password, is_approved=False)
        db.session.add(ngo)
        db.session.commit()
        flash("Registration successful! Please wait for admin approval.", "success")
        return redirect(url_for('ngo.login'))
    return render_template('ngo/register.html')


@ngo_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        ngo = NGO.query.filter_by(email=email).first()
        if ngo and check_password_hash(ngo.password, password):
            if not ngo.is_approved:
                flash("Your NGO registration is pending admin approval.", "warning")
                return redirect(url_for('ngo.login'))
            session['ngo_id'] = ngo.id
            flash("Login successful", "success")
            return redirect(url_for('ngo.dashboard'))
        flash("Invalid credentials", "danger")
    return render_template('ngo/login.html')


@ngo_bp.route('/dashboard')
def dashboard():
    if 'ngo_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('ngo.login'))
    ngo = NGO.query.get(session['ngo_id'])

    # Fetch emergency cases assigned to this NGO
    cases = EmergencyCase.query.filter_by(assigned_ngo=ngo.id).all()

    # Collect details for each case
    case_details = []
    for case in cases:
        volunteer = None
        if case.assigned_volunteer:
            volunteer = Volunteer.query.get(case.assigned_volunteer)

        verification_report = VerificationReport.query.filter_by(case_id=case.id).order_by(VerificationReport.submitted_at.desc()).first()

        verification_status = "Not Submitted"
        if verification_report:
            verification_status = "Submitted"

        case_details.append({
            'case': case,
            'volunteer': volunteer,
            'verification_status': verification_status,
            'verified': verification_report is not None,
            'verification_report': verification_report
        })

    return render_template('ngo/dashboard.html', ngo=ngo, case_details=case_details)


@ngo_bp.route('/update-case-status/<int:case_id>', methods=['GET', 'POST'])
def update_case_status(case_id):
    if 'ngo_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('ngo.login'))

    case = EmergencyCase.query.get_or_404(case_id)

    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status:
            case.status = new_status
            db.session.commit()
            flash("Case status updated.", "success")
            return redirect(url_for('ngo.dashboard'))
        else:
            flash("Please select a valid status.", "danger")

    return render_template('ngo/update_case_status.html', case=case)

@ngo_bp.route('/assign-volunteer/<int:case_id>', methods=['GET', 'POST'])
def assign_volunteer(case_id):
    if 'ngo_id' not in session:
        flash("Please login first", "danger")
        return redirect(url_for('ngo.login'))

    case = EmergencyCase.query.get_or_404(case_id)
    if request.method == 'POST':
        volunteer_id = request.form.get('volunteer_id')
        volunteer = Volunteer.query.get(volunteer_id)
        if volunteer:
            case.assigned_volunteer = volunteer.id
            db.session.commit()
            flash(f"Volunteer {volunteer.name} assigned successfully.", "success")
            return redirect(url_for('ngo.dashboard'))
        flash("Invalid volunteer selected.", "danger")

    volunteers = Volunteer.query.all()
    return render_template('ngo/assign_volunteer.html', case=case, volunteers=volunteers)


@ngo_bp.route('/logout')
def logout():
    session.pop('ngo_id', None)
    flash("Logged out", "info")
    return redirect(url_for('ngo.login'))
