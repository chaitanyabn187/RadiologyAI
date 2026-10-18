import os
import sqlite3
import uuid
import json
import math
import hashlib

from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    url_for,
    redirect,
    send_from_directory
)

from werkzeug.utils import secure_filename
from ai_model import analyze_xray


# --------------------------------------------------
# FLASK CONFIGURATION
# --------------------------------------------------

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "radiology.db")

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

app.jinja_env.filters["from_json"] = json.loads

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------
# DATABASE CONNECTION
# --------------------------------------------------

def get_db_connection():

    connection = sqlite3.connect(
        DATABASE,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    return connection


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def init_db():

    connection = get_db_connection()

    try:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                patient_id TEXT UNIQUE NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT,
                image_filename TEXT,
                priority TEXT DEFAULT 'Pending',
                ai_findings TEXT,
                image_hash TEXT
            )
        """)

        columns = [
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(patients)"
            ).fetchall()
        ]

        if "image_hash" not in columns:

            connection.execute("""
                ALTER TABLE patients
                ADD COLUMN image_hash TEXT
            """)

        # Add a location column without deleting old records.
        if "diagnosis_location" not in columns:

            connection.execute("""
                ALTER TABLE patients
                ADD COLUMN diagnosis_location TEXT
                    DEFAULT 'Not localized'
            """)

        # Calculate hashes for older uploaded images.
        existing_cases = connection.execute("""
            SELECT id, image_filename
            FROM patients
            WHERE image_hash IS NULL
              AND image_filename IS NOT NULL
            ORDER BY id
        """).fetchall()

        for case in existing_cases:

            filename = os.path.basename(
                case["image_filename"]
            )

            image_path = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            if not os.path.isfile(image_path):
                continue

            try:

                with open(image_path, "rb") as image_file:
                    image_bytes = image_file.read()

                image_hash = hashlib.sha256(
                    image_bytes
                ).hexdigest()

                existing_hash = connection.execute("""
                    SELECT id
                    FROM patients
                    WHERE image_hash = ?
                    LIMIT 1
                """, (image_hash,)).fetchone()

                if existing_hash is None:

                    connection.execute("""
                        UPDATE patients
                        SET image_hash = ?
                        WHERE id = ?
                    """, (
                        image_hash,
                        case["id"]
                    ))

            except OSError:

                app.logger.exception(
                    "Could not calculate the hash of an existing image."
                )

        connection.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_patients_image_hash
            ON patients(image_hash)
            WHERE image_hash IS NOT NULL
        """)

        connection.commit()

    finally:
        connection.close()


init_db()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def safe_delete_image(filename):
    """Delete an image only from the configured uploads directory."""

    if not filename:
        return

    safe_name = os.path.basename(filename)

    image_path = os.path.join(
        UPLOAD_FOLDER,
        safe_name
    )

    if os.path.isfile(image_path):

        try:
            os.remove(image_path)

        except OSError:

            app.logger.exception(
                "Could not delete uploaded image."
            )


def get_valid_findings(findings_json):
    """Return findings with finite numerical model scores."""

    try:

        findings = json.loads(
            findings_json or "[]"
        )

        if not isinstance(findings, list):
            return []

        valid_findings = []

        for finding in findings:

            if not isinstance(finding, dict):
                continue

            try:

                score = float(
                    finding.get("score")
                )

            except (TypeError, ValueError):
                continue

            if not math.isfinite(score):
                continue

            valid_findings.append({
                "name": str(
                    finding.get("name", "Unknown")
                ),
                "score": score
            })

        valid_findings.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return valid_findings

    except (ValueError, TypeError, json.JSONDecodeError):

        return []


# --------------------------------------------------
# SERVE UPLOADED IMAGES
# --------------------------------------------------

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    safe_name = os.path.basename(filename)

    if safe_name != filename:
        return "Invalid filename", 400

    image_path = os.path.join(
        UPLOAD_FOLDER,
        safe_name
    )

    if not os.path.isfile(image_path):
        return "Image not found", 404

    return send_from_directory(
        UPLOAD_FOLDER,
        safe_name
    )


# --------------------------------------------------
# HOME PAGE
# --------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# --------------------------------------------------
# UPLOAD PAGE
# --------------------------------------------------

@app.route("/upload")
def upload():

    return render_template("upload.html")


# --------------------------------------------------
# SAVE PATIENT CASE
# --------------------------------------------------

@app.route("/save_case", methods=["POST"])
def save_case():

    image_filename = None
    connection = None

    try:

        patient_name = request.form.get(
            "patientName", ""
        ).strip()

        patient_id = request.form.get(
            "patientId", ""
        ).strip()

        age_text = request.form.get(
            "age", ""
        ).strip()

        gender = request.form.get(
            "gender", ""
        ).strip()

        body_part = request.form.get(
            "bodyPart", "chest"
        ).strip().lower()

        # Validate patient details.
        if not patient_name or not patient_id or not age_text:

            return jsonify({
                "success": False,
                "message": (
                    "Please fill in all required patient details."
                )
            }), 400

        try:
            age = int(age_text)

        except ValueError:

            return jsonify({
                "success": False,
                "message": "Age must be a valid whole number."
            }), 400

        if not 0 <= age <= 120:

            return jsonify({
                "success": False,
                "message": "Please enter a valid age."
            }), 400

        if body_part != "chest":

            return jsonify({
                "success": False,
                "message": (
                    "This prototype supports chest X-rays only."
                )
            }), 400

        # Validate the uploaded image.
        if "xrayImage" not in request.files:

            return jsonify({
                "success": False,
                "message": "Please select a chest X-ray image."
            }), 400

        image = request.files["xrayImage"]

        if not image or not image.filename:

            return jsonify({
                "success": False,
                "message": "Please select an image."
            }), 400

        if not allowed_file(image.filename):

            return jsonify({
                "success": False,
                "message": "Upload a PNG, JPG, or JPEG image."
            }), 400

        image_bytes = image.read()

        if not image_bytes:

            return jsonify({
                "success": False,
                "message": "The selected image is empty."
            }), 400

        image_hash = hashlib.sha256(
            image_bytes
        ).hexdigest()

        connection = get_db_connection()

        # Check duplicate image.
        existing_case = connection.execute("""
            SELECT id
            FROM patients
            WHERE image_hash = ?
            LIMIT 1
        """, (image_hash,)).fetchone()

        if existing_case:

            return jsonify({
                "success": False,
                "duplicate": True,
                "message": (
                    "Duplicate image detected! This exact image "
                    f"already exists in case {existing_case['id']}."
                )
            }), 409

        # Check duplicate patient ID.
        existing_patient = connection.execute("""
            SELECT id
            FROM patients
            WHERE patient_id = ?
            LIMIT 1
        """, (patient_id,)).fetchone()

        if existing_patient:

            return jsonify({
                "success": False,
                "message": (
                    "This patient ID already exists. "
                    "Please use a unique ID."
                )
            }), 400

        original_filename = secure_filename(
            image.filename
        )

        if not original_filename or "." not in original_filename:

            return jsonify({
                "success": False,
                "message": "Please select a valid image filename."
            }), 400

        extension = original_filename.rsplit(
            ".", 1
        )[1].lower()

        image_filename = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        image_path = os.path.join(
            UPLOAD_FOLDER,
            image_filename
        )

        with open(image_path, "wb") as image_file:
            image_file.write(image_bytes)

        # Run experimental AI analysis.
        analysis = analyze_xray(
            image_path,
            body_part="chest"
        )

        findings = []

        if isinstance(analysis, dict) and analysis.get("success"):

            findings = get_valid_findings(
                json.dumps(
                    analysis.get("findings", [])
                )
            )

        # The existing model does not provide validated localization.
        diagnosis_location = "Not localized"

        try:

            cursor = connection.execute("""
                INSERT INTO patients (
                    patient_name,
                    patient_id,
                    age,
                    gender,
                    image_filename,
                    priority,
                    ai_findings,
                    image_hash,
                    diagnosis_location
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                patient_name,
                patient_id,
                age,
                gender,
                image_filename,
                "Pending",
                json.dumps(findings),
                image_hash,
                diagnosis_location
            ))

            connection.commit()

            case_id = cursor.lastrowid

        except sqlite3.IntegrityError:

            connection.rollback()

            duplicate_image = connection.execute("""
                SELECT id
                FROM patients
                WHERE image_hash = ?
                LIMIT 1
            """, (image_hash,)).fetchone()

            if duplicate_image:

                return jsonify({
                    "success": False,
                    "duplicate": True,
                    "message": (
                        "Duplicate image detected! This exact image "
                        f"already exists in case {duplicate_image['id']}."
                    )
                }), 409

            return jsonify({
                "success": False,
                "message": "This patient ID already exists."
            }), 400

        return jsonify({
            "success": True,
            "message": "Chest X-ray case saved successfully.",
            "case_id": case_id,
            "image_url": url_for(
                "uploaded_file",
                filename=image_filename
            ),
            "analysis": analysis
        }), 200

    except Exception:

        app.logger.exception(
            "Failed to save patient case."
        )

        return jsonify({
            "success": False,
            "message": (
                "An error occurred while saving the case. "
                "Please check the application terminal."
            )
        }), 500

    finally:

        if connection is not None:
            connection.close()

        # Remove an uploaded image only if no database record uses it.
        if image_filename:

            try:

                check_connection = get_db_connection()

                saved_case = check_connection.execute("""
                    SELECT id
                    FROM patients
                    WHERE image_filename = ?
                """, (image_filename,)).fetchone()

                check_connection.close()

                if saved_case is None:
                    safe_delete_image(image_filename)

            except Exception:

                app.logger.exception(
                    "Could not verify whether the image was saved."
                )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    connection = get_db_connection()

    try:

        patients = connection.execute("""
            SELECT *
            FROM patients
        """).fetchall()

    finally:
        connection.close()

    case_list = []

    for patient in patients:

        patient_data = dict(patient)

        findings = get_valid_findings(
            patient_data.get("ai_findings")
        )

        patient_data["ai_findings"] = findings

        if findings:

            patient_data["experimental_score"] = max(
                finding["score"]
                for finding in findings
            )

        else:
            patient_data["experimental_score"] = None

        # Backward-compatible fallback for older rows.
        patient_data["diagnosis_location"] = (
            patient_data.get("diagnosis_location")
            or "Not localized"
        )

        case_list.append(patient_data)

    # Sort cases by highest experimental model score.
    # Cases without valid scores appear last.
    case_list.sort(
        key=lambda patient: (
            patient["experimental_score"] is None,
            -patient["experimental_score"]
            if patient["experimental_score"] is not None
            else 0,
            patient["id"]
        )
    )

    # Assign sequential review ranks.
    for rank, patient in enumerate(case_list, start=1):
        patient["review_rank"] = rank

    return render_template(
        "dashboard.html",
        patients=case_list
    )


# --------------------------------------------------
# DELETE ONE CASE
# --------------------------------------------------

@app.route(
    "/delete_case/<int:case_id>",
    methods=["POST"]
)
def delete_case(case_id):

    connection = get_db_connection()

    try:

        patient = connection.execute("""
            SELECT image_filename
            FROM patients
            WHERE id = ?
        """, (case_id,)).fetchone()

        if patient is None:
            return redirect(url_for("dashboard"))

        image_filename = patient["image_filename"]

        connection.execute("""
            DELETE FROM patients
            WHERE id = ?
        """, (case_id,))

        connection.commit()

    finally:
        connection.close()

    safe_delete_image(image_filename)

    return redirect(url_for("dashboard"))


# --------------------------------------------------
# CLEAR ALL CASES
# --------------------------------------------------

@app.route(
    "/clear_cases",
    methods=["POST"]
)
def clear_cases():

    connection = get_db_connection()

    try:

        patients = connection.execute("""
            SELECT image_filename
            FROM patients
        """).fetchall()

        connection.execute("""
            DELETE FROM patients
        """)

        connection.commit()

    finally:
        connection.close()

    for patient in patients:

        safe_delete_image(
            patient["image_filename"]
        )

    return redirect(url_for("dashboard"))


# --------------------------------------------------
# FILE SIZE ERROR
# --------------------------------------------------

@app.errorhandler(413)
def file_too_large(error):

    return jsonify({
        "success": False,
        "message": (
            "The image is too large. "
            "Maximum upload size is 10 MB."
        )
    }), 413


# --------------------------------------------------
# RUN APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )