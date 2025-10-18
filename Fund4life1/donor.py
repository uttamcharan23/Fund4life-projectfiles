import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models.donor import Donor
from models.donation import Donation
from models.emergency_case import EmergencyCase

donor_bp = Blueprint('donor', __name__, url_prefix='/donor')

def donor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'donor_id' not in session:
            flash('Please log in as donor.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

@donor_bp.route('/dashboard')
@donor_required
def dashboard():
    donor = Donor.query.get(session['donor_id'])
    donations = Donation.query.filter_by(donor_id=donor.id).all()
    cases = EmergencyCase.query.filter_by(donor_id=donor.id).all()
    total_donated = sum([d.amount for d in donations])
    return render_template('donor/dashboard.html', donor=donor, donations=donations, cases=cases, total_donated=total_donated)

@donor_bp.route('/donate', methods=['POST'])
@donor_required
def donate():
    amount = float(request.form['amount'])
    donation = Donation(donor_id=session['donor_id'], amount=amount)
    db.session.add(donation)
    db.session.commit()
    flash('Thank you for your donation!', 'success')
    return redirect(url_for('donor.dashboard'))

@donor_bp.route('/emergency_request', methods=['POST'])
@donor_required
def emergency_request():
    description = request.form['description']
    amount_requested = float(request.form['amount_requested'])
    document = request.files.get('document')
    filename = None
    if document:
        filename = secure_filename(document.filename)
        doc_path = os.path.join(current_app.root_path, 'static', 'documents')
        os.makedirs(doc_path, exist_ok=True)
        document.save(os.path.join(doc_path, filename))
    case = EmergencyCase(
        donor_id=session['donor_id'],
        description=description,
        amount_requested=amount_requested,
        status='Pending',
        document_filename=filename
    )
    db.session.add(case)
    db.session.commit()
    flash('Emergency case submitted.', 'success')
    return redirect(url_for('donor.dashboard'))
