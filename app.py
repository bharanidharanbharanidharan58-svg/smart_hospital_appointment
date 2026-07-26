from flask import Flask
from config import Config

from models.db import init_db
from models.hospital import HospitalModel
from models.doctor import DoctorModel

from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp

app = Flask(__name__)

app.config.from_object(Config)

app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)


@app.route("/")
def home():
    return "Step 4 OK"


if __name__ == "__main__":
    app.run(debug=True)