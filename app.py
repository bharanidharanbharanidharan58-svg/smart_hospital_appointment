from flask import Flask
from config import Config

from models.db import init_db
from models.hospital import HospitalModel
from models.doctor import DoctorModel

from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp


app = Flask(__name__)

app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)


@app.route("/")
def home():
    return "Step 7 OK"


if __name__ == "__main__":
    app.run(debug=True)