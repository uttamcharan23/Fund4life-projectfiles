from extensions import db

class EmergencyCase(db.Model):
    __tablename__ = 'emergency_case'
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor.id'), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    amount_requested = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    assigned_ngo = db.Column(db.Integer, db.ForeignKey('ngo.id'), nullable=True)
    assigned_volunteer = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=True)  # Add this field
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    document_filename = db.Column(db.String(300), nullable=True)
