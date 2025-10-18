import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.volunteer import Volunteer
from models.emergency_case import EmergencyCase
from models.verification_report import VerificationReport

volunteer_bp = Blueprint('volunteer', __name__, url_prefix='/volunteer')

def volunteer_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'volunteer_id' not in session:
            flash('Please log in as volunteer.', 'danger')
            return redirect(url_for('volunteer_auth.login'))
        return f(*args, **kwargs)
    return decorated

@volunteer_bp.route('/dashboard')
@volunteer_required
def dashboard():
    volunteer = Volunteer.query.get(session['volunteer_id'])
    assigned_cases = EmergencyCase.query.filter_by(assigned_volunteer=volunteer.id).all()

    case_details = []
    for case in assigned_cases:
        # Fetch related verification report if any
        verification_report = VerificationReport.query.filter_by(case_id=case.id, volunteer_id=volunteer.id).order_by(VerificationReport.submitted_at.desc()).first()
        verification_status = "Not Submitted"
        if verification_report:
            verification_status = "Submitted"
        case_details.append({
            'case': case,
            'verification_status': verification_status,
            'verification_report': verification_report
        })

    return render_template('volunteer/dashboard.html', volunteer=volunteer, case_details=case_details)

@volunteer_bp.route('/case/<int:case_id>', methods=['GET', 'POST'])
@volunteer_required
def submit_verification(case_id):
    volunteer = Volunteer.query.get(session['volunteer_id'])
    case = EmergencyCase.query.get_or_404(case_id)

    if case.assigned_volunteer != volunteer.id:
        flash('Unauthorized access to case.', 'danger')
        return redirect(url_for('volunteer.dashboard'))

    if request.method == 'POST':
        live_photo = request.files.get('live_photo')
        verified_docs = request.files.get('verified_docs')
        comments = request.form.get('comments')

        upload_folder = os.path.join(current_app.root_path, 'static', 'verification_uploads')
        os.makedirs(upload_folder, exist_ok=True)

        live_photo_filename = None
        verified_docs_filename = None

        if live_photo:
            live_photo_filename = secure_filename(live_photo.filename)
            live_photo.save(os.path.join(upload_folder, live_photo_filename))

        if verified_docs:
            verified_docs_filename = secure_filename(verified_docs.filename)
            verified_docs.save(os.path.join(upload_folder, verified_docs_filename))

        report = VerificationReport(
            case_id=case.id,
            volunteer_id=volunteer.id,
            live_photo_filename=live_photo_filename,
            verified_docs_filename=verified_docs_filename,
            comments=comments
        )
        db.session.add(report)
        case.status = 'Verified by Volunteer'
        db.session.commit()

        flash('Verification report submitted.', 'success')
        return redirect(url_for('volunteer.dashboard'))

    return render_template('volunteer/submit_verification.html', case=case)
