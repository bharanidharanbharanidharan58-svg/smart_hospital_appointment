from flask import Flask, render_template
from config import Config

from models.db import init_db
from models.doctor import DoctorModel

from routes.auth_routes import auth_bp
from routes.patient_routes import patient_bp
from routes.doctor_routes import doctor_bp
from routes.admin_routes import admin_bp
from routes.api_routes import api_bp
from routes.ai_routes import ai_bp


app = Flask(__name__)

app.config.from_object(Config)

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(ai_bp)


@app.route("/")
def index():
    doctors = DoctorModel.get_all()
    return render_template("index.html", doctors=doctors)


if __name__ == "__main__":
    app.run(debug=True)