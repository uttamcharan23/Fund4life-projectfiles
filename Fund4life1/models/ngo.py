from extensions import db

class NGO(db.Model):
    __tablename__ = 'ngo'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Password field for hashed password
    is_approved = db.Column(db.Boolean, default=False)
    assigned_cases = db.relationship('EmergencyCase', backref='assigned_ngo_obj', lazy=True, foreign_keys='EmergencyCase.assigned_ngo')
