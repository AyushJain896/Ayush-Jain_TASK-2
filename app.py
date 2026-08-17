"""
BMI Calculator & Health Tracker - Localhost Web Application
============================================================
A modern Flask web server providing a localhost web interface accessible at http://localhost:5000.
Supports single user operations and multi-user BMI comparison graphs on the same chart.
"""

import os
import sys
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify

# Import core modules
from bmi import calculate_bmi, get_bmi_category, validate_inputs
from database import (
    init_db,
    save_record,
    get_user_history,
    get_all_users,
    delete_record,
    clear_user_history,
    DEFAULT_DB_PATH
)

app = Flask(__name__)

# Initialize database schema on server startup
init_db(DEFAULT_DB_PATH)


@app.route("/")
def index():
    """Renders the main dashboard HTML page."""
    return render_template("index.html")


@app.route("/api/users", methods=["GET"])
def api_users():
    """Returns a list of all unique usernames stored in the database."""
    try:
        users = get_all_users(DEFAULT_DB_PATH)
        return jsonify({"success": True, "users": users})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """Validates user inputs and calculates BMI."""
    data = request.get_json() or {}
    username_str = data.get("username", "")
    weight_str = str(data.get("weight", ""))
    height_str = str(data.get("height", ""))

    is_valid, error_msg, username, weight, height = validate_inputs(
        username_str, weight_str, height_str
    )

    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    bmi_val = calculate_bmi(weight, height)
    category_info = get_bmi_category(bmi_val)

    return jsonify({
        "success": True,
        "data": {
            "username": username,
            "weight": weight,
            "height": height,
            "bmi": bmi_val,
            "category": category_info["category"],
            "color": category_info["color"],
            "message": category_info["message"]
        }
    })


@app.route("/api/save", methods=["POST"])
def api_save():
    """Saves a calculated BMI entry to the SQLite database."""
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    weight = data.get("weight")
    height = data.get("height")
    bmi = data.get("bmi")
    category = data.get("category", "").strip()

    if not username or weight is None or height is None or bmi is None or not category:
        return jsonify({"success": False, "error": "Missing required record parameters."}), 400

    try:
        row_id = save_record(
            username=username,
            weight=float(weight),
            height=float(height),
            bmi=float(bmi),
            category=category,
            db_path=DEFAULT_DB_PATH
        )
        return jsonify({"success": True, "id": row_id, "message": f"Saved record #{row_id} for user '{username}'"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history/<username>", methods=["GET"])
def api_history(username):
    """Retrieves all historical BMI entries for a single user."""
    clean_username = username.strip()
    if not clean_username:
        return jsonify({"success": False, "error": "Username is required."}), 400

    try:
        records = get_user_history(clean_username, db_path=DEFAULT_DB_PATH)
        return jsonify({"success": True, "username": clean_username, "records": records})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/multi-history", methods=["POST"])
def api_multi_history():
    """Retrieves historical BMI entries for multiple users for comparative graphing."""
    data = request.get_json() or {}
    usernames = data.get("usernames", [])
    clean_usernames = [u.strip() for u in usernames if u and u.strip()]

    if not clean_usernames:
        return jsonify({"success": False, "error": "At least one username must be provided."}), 400

    results = {}
    try:
        for u in clean_usernames:
            results[u] = get_user_history(u, db_path=DEFAULT_DB_PATH)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/record/<int:record_id>", methods=["DELETE"])
def api_delete_record(record_id):
    """Deletes a specific record entry by ID."""
    try:
        deleted = delete_record(record_id, db_path=DEFAULT_DB_PATH)
        if deleted:
            return jsonify({"success": True, "message": f"Deleted record ID #{record_id}"})
        else:
            return jsonify({"success": False, "error": "Record ID not found."}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/user-history/<username>", methods=["DELETE"])
def api_clear_user_history(username):
    """Clears all records for a given user."""
    clean_username = username.strip()
    try:
        count = clear_user_history(clean_username, db_path=DEFAULT_DB_PATH)
        return jsonify({"success": True, "count": count, "message": f"Deleted {count} record(s) for '{clean_username}'"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def open_browser():
    """Automatically launches the user's web browser to http://localhost:5000."""
    webbrowser.open_new("http://localhost:5000/")


if __name__ == "__main__":
    print("\n========================================================")
    print(" ⚖️ BMI Calculator & Health Tracker - Localhost Web Server")
    print(" Running on: http://localhost:5000/")
    print("========================================================\n")

    Timer(1.2, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
