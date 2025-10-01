import os
import hashlib
import json
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS
from pydantic import ValidationError
from models import SurveySubmission, StoredSurveyRecord
from storage import append_json_line

app = Flask(__name__)
# Allow cross-origin requests so the static HTML can POST from localhost or file://
CORS(app, resources={r"/v1/*": {"origins": "*"}})

@app.route("/ping", methods=["GET"])
def ping():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "API is alive",
        "utc_time": datetime.now(timezone.utc).isoformat()
    })

@app.post("/v1/survey")
def submit_survey():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid_json", "detail": "Body must be application/json"}), 400

    try:
        submission = SurveySubmission(**payload)
    except ValidationError as ve:
        return jsonify({"error": "validation_error", "detail": ve.errors()}), 422



    # Prepare data for storage

    data_to_store = submission.dict()

    # Hash email for storage only

    data_to_store["email"] = hashlib.sha256(data_to_store["email"].encode("utf-8")).hexdigest()

    # age stays as int for test compatibility

 

    data_dir = "data"

    os.makedirs(data_dir, exist_ok=True)  # creates folder if missing

 

    file_path = os.path.join(data_dir, "survey.ndjson")

    with open(file_path, "a") as f:

        f.write(json.dumps(data_to_store) + "\n")


    return jsonify({"status": "ok"}), 201

if __name__ == "__main__":
    app.run(port=5000, debug=True)