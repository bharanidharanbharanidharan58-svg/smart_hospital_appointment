from flask import Flask
from config import Config

from models.db import init_db
from models.hospital import HospitalModel
from models.doctor import DoctorModel

app = Flask(__name__)
app.config.from_object(Config)

@app.route("/")
def home():
    return "Step 2 OK"