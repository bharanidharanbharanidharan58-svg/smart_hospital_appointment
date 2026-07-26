from flask import Flask

app = Flask(__name__)

from config import Config

app.config.from_object(Config)

@app.route("/")
def home():
    return "Step 1 OK"