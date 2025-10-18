from extensions import db

class Donor(db.Model):
    __tablename__ = 'donor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)  
    password = db.Column(db.String(200), nullable=False)

    donations = db.relationship('Donation', backref='donor', lazy=True)
    cases = db.relationship('EmergencyCase', backref='donor', lazy=True)
