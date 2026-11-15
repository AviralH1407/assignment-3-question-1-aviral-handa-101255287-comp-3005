import os
import psycopg2
from psycopg2 import Error
from flask import Flask, request, jsonify, render_template

# Initialize the Flask application
app = Flask(__name__)

# Database connection configuration (update password/dbname to match the setup)
DB_CONFIG = {
    "dbname": os.environ.get("DB_NAME", "university_db"),
    "user": os.environ.get("DB_USER", "postgres"),
    "password": os.environ.get("DB_PASSWORD", "root"),
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": os.environ.get("DB_PORT", "5432")
}


def get_db_connection():
    """Creates and returns a new PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)


# =====================================================================
# Required Assignment CRUD Functions
# =====================================================================

def getAllStudents():
    """
    Retrieves and displays all records from the students table.
    Returns a list of student dictionaries ordered by student_id.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT student_id, first_name, last_name, email, enrollment_date "
                "FROM students ORDER BY student_id ASC;"
            )
            rows = cur.fetchall()

            # Format rows into a list of dictionaries for display and JSON serialization
            students = []
            for row in rows:
                students.append({
                    "student_id": row[0],
                    "first_name": row[1],
                    "last_name": row[2],
                    "email": row[3],
                    "enrollment_date": str(row[4]) if row[4] else None
                })
            print("Retrieved all students:", students)
            return students
    except Error as e:
        print(f"Database error in getAllStudents: {e}")
        raise
    finally:
        if conn:
            conn.close()


def addStudent(first_name, last_name, email, enrollment_date):
    """
    Inserts a new student record into the students table.
    Returns the newly created student's ID.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            # Use parameterized query (%s) to prevent SQL injection
            query = """
                INSERT INTO students (first_name, last_name, email, enrollment_date)
                VALUES (%s, %s, %s, %s)
                RETURNING student_id;
            """
            # Convert empty date string to None (SQL NULL) if omitted
            date_val = enrollment_date if enrollment_date else None
            cur.execute(query, (first_name, last_name, email, date_val))
            new_id = cur.fetchone()[0]
            conn.commit()
            print(f"Added student with ID: {new_id}")
            return new_id
    except Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in addStudent: {e}")
        raise
    finally:
        if conn:
            conn.close()


def updateStudentEmail(student_id, new_email):
    """
    Updates the email address for a student with the specified student_id.
    Returns True if a record was updated, False if student_id was not found.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = "UPDATE students SET email = %s WHERE student_id = %s;"
            cur.execute(query, (new_email, student_id))
            updated_rows = cur.rowcount
            conn.commit()
            print(f"Updated email for student_id {student_id}. Rows affected: {updated_rows}")
            return updated_rows > 0
    except Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in updateStudentEmail: {e}")
        raise
    finally:
        if conn:
            conn.close()


def deleteStudent(student_id):
    """
    Deletes the record of the student with the specified student_id.
    Returns True if a record was deleted, False if student_id was not found.
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = "DELETE FROM students WHERE student_id = %s;"
            cur.execute(query, (student_id,))
            deleted_rows = cur.rowcount
            conn.commit()
            print(f"Deleted student_id {student_id}. Rows affected: {deleted_rows}")
            return deleted_rows > 0
    except Error as e:
        if conn:
            conn.rollback()
        print(f"Database error in deleteStudent: {e}")
        raise
    finally:
        if conn:
            conn.close()


# =====================================================================
# Flask Routes (Connecting Frontend JS to Backend CRUD Functions)
# =====================================================================

@app.route("/")
def index():
    """Serves the plain HTML frontend page."""
    return render_template("index.html")


@app.route("/api/students", methods=["GET"])
def api_get_students():
    """API endpoint that calls getAllStudents() and returns JSON."""
    try:
        students = getAllStudents()
        return jsonify({"status": "success", "students": students}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/students", methods=["POST"])
def api_add_student():
    """API endpoint that reads form JSON and calls addStudent()."""
    data = request.get_json()
    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    email = data.get("email", "").strip()
    enrollment_date = data.get("enrollment_date", "").strip()

    # Validate required NOT NULL fields before querying the database
    if not first_name or not last_name or not email:
        return jsonify({"status": "error", "message": "First name, last name, and email are required."}), 400

    try:
        new_id = addStudent(first_name, last_name, email, enrollment_date)
        return jsonify({"status": "success", "message": f"Student added with ID {new_id}."}), 201
    except psycopg2.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists (must be unique)."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/students/<int:student_id>", methods=["PUT"])
def api_update_student_email(student_id):
    """API endpoint that calls updateStudentEmail() for a specific student_id."""
    data = request.get_json()
    new_email = data.get("new_email", "").strip()

    if not new_email:
        return jsonify({"status": "error", "message": "New email is required."}), 400

    try:
        updated = updateStudentEmail(student_id, new_email)
        if not updated:
            return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404
        return jsonify({"status": "success", "message": f"Email updated for student ID {student_id}."}), 200
    except psycopg2.IntegrityError:
        return jsonify({"status": "error", "message": "Email already exists (must be unique)."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def api_delete_student(student_id):
    """API endpoint that calls deleteStudent() for a specific student_id."""
    try:
        deleted = deleteStudent(student_id)
        if not deleted:
            return jsonify({"status": "error", "message": f"Student ID {student_id} not found."}), 404
        return jsonify({"status": "success", "message": f"Student ID {student_id} deleted."}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    # Make sure the university_db database and students table exist (see setup_db.py)
    try:
        from setup_db import main as setup_database
        setup_database()
    except Exception as e:
        print(f"Database setup failed: {e}")

    # Run the Flask development server
    app.run(debug=True, port=5001)
