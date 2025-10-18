from flask import Blueprint, render_template, session, redirect, url_for, request
from extensions import db
from models.ngo import NGO

ngo_bp = Blueprint('ngo_bp', __name__, template_folder='../templates')

# NGO dashboard
@ngo_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in') or session.get('user_role') != 'ngo':
        return redirect(url_for('ngo_bp.login'))
    
    ngos = NGO.query.all()
    return render_template('ngo_dashboard.html', ngos=ngos)

# NGO login
@ngo_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        ngo = NGO.query.filter_by(email=email).first()
        if ngo and ngo.is_approved and ngo.password == password:  # Simplified password check
            session['logged_in'] = True
            session['user_role'] = 'ngo'
            session['user_id'] = ngo.id
            return redirect(url_for('ngo_bp.dashboard'))
    return render_template('ngo_login.html')
