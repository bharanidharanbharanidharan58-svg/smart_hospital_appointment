from flask import Flask, render_template, session
from config import Config
from models.db import init_db
from models.hospital import HospitalModel
from models.doctor import DoctorModel
from seed_data import seed_database

# Blueprints
from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.api_routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)

# Initialize and Seed Database
# with app.app_context():
#     init_db()
#     seed_database()

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(ai_bp)
app.register_blueprint(api_bp)

@app.context_processor
def inject_global_vars():
    return {
        'app_name': Config.APP_NAME,
        'app_version': Config.VERSION,
        'user_name': session.get('name'),
        'user_role': session.get('role')
    }

@app.route('/')
def index():
    hospitals = HospitalModel.get_all()
    doctors = DoctorModel.get_all()
    return render_template('index.html', hospitals=hospitals, doctors=doctors)

if __name__ == '__main__':
    print(f"Starting {Config.APP_NAME} Enterprise Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
