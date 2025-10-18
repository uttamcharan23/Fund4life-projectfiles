from flask import Flask, render_template
from extensions import db
from models import donor, ngo, emergency_case, donation
from auth import auth_bp
from donor import donor_bp
from admin.routes import admin_bp
from ngo import ngo_bp
from volunteer_auth import volunteer_auth_bp
from volunteer import volunteer_bp

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'supersecretkey'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fund4life.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with app
    db.init_app(app)

    # Register blueprints for modular route management
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(ngo_bp)
    app.register_blueprint(volunteer_auth_bp)
    app.register_blueprint(volunteer_bp)

    # Root route for homepage
    @app.route('/')
    def index():
        return render_template('home.html')

    # Create tables if not exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
