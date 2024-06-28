from flask import Flask
from flask_cors import CORS
from routes import jobs_bp

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.register_blueprint(jobs_bp, url_prefix="/jobs")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
