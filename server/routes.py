from flask import Blueprint, request, jsonify
from database import main

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/add", methods=["POST"])
def add_job():
    data = request.json
    if (
        not data
        or "job_url" not in data
        or "document_id" not in data
        or "sheet_name" not in data
    ):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        # Uncomment and use this if you have the main function in database.py
        main(data["job_url"], data["document_id"], data["sheet_name"])

        # For now, let's just print the received data
        print(f"Received data: {data}")
        return jsonify({"message": "Job added successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
