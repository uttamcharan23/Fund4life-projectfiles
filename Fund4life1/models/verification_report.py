from extensions import db
from datetime import datetime

class VerificationReport(db.Model):
    __tablename__ = 'verification_report'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('emergency_case.id'), nullable=False)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    live_photo_filename = db.Column(db.String(300), nullable=True)
    verified_docs_filename = db.Column(db.String(300), nullable=True)
    comments = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    case = db.relationship('EmergencyCase', backref=db.backref('verification_reports', lazy=True))
    volunteer = db.relationship('Volunteer', backref=db.backref('verification_reports_submitted', lazy=True))
