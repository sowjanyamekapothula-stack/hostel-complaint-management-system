from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
import re
import random

app = Flask(__name__)


# =========================================================
# MYSQL DATABASE CONNECTION
# =========================================================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3307,
        user="root",
        password="mysql@123",
        database="hostel_management"
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return redirect(url_for("login"))


# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    student_name = request.form.get("student_name", "").strip()
    student_id = request.form.get("student_id", "").strip()
    room_number = request.form.get("room_number", "").strip()
    password = request.form.get("password", "")

    if not student_name or not student_id or not room_number or not password:
        return """
        <h2>All fields are required ❌</h2>
        <a href="/register">Go Back</a>
        """

    if len(password) < 6:
        return """
        <h2>Password must contain at least 6 characters ❌</h2>
        <a href="/register">Go Back</a>
        """

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        existing_student = cursor.fetchone()

        if existing_student:
            return """
            <h2>Student ID already registered ❌</h2>
            <a href="/login">Go to Login</a>
            """

        cursor.execute(
            """
            INSERT INTO students
            (
                student_name,
                student_id,
                room_number,
                password
            )
            VALUES
            (%s, %s, %s, %s)
            """,
            (
                student_name,
                student_id,
                room_number,
                password
            )
        )

        connection.commit()

        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Account Created</title>
        </head>

        <body style="
            font-family:Arial;
            text-align:center;
            padding-top:80px;
        ">

            <h1>Account Created Successfully! ✅</h1>

            <p>Your hostel account has been created.</p>

            <br>

            <a href="/login"
               style="
               background:#1e3a8a;
               color:white;
               padding:12px 25px;
               text-decoration:none;
               border-radius:6px;
               ">
               Login Now
            </a>

        </body>
        </html>
        """

    except mysql.connector.Error as error:

        return f"""
        <h2>MySQL Database Error ❌</h2>
        <p>{error}</p>
        <a href="/register">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    student_id = request.form.get("student_id", "").strip()
    password = request.form.get("password", "")

    if not student_id or not password:
        return """
        <h2>Please enter Student ID and Password ❌</h2>
        <a href="/login">Try Again</a>
        """

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                student_name,
                student_id,
                room_number
            FROM students
            WHERE student_id = %s
            AND password = %s
            """,
            (
                student_id,
                password
            )
        )

        student = cursor.fetchone()

        if not student:

            return """
            <!DOCTYPE html>
            <html>

            <head>
                <title>Login Failed</title>
            </head>

            <body style="
                font-family:Arial;
                text-align:center;
                padding-top:80px;
            ">

                <h2>Invalid Student ID or Password ❌</h2>

                <br>

                <a href="/login">
                    Try Again
                </a>

                <br><br>

                <a href="/forgot_password">
                    Forgot Password?
                </a>

            </body>
            </html>
            """

        return render_template(
            "student_dashboard.html",
            student=student
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>MySQL Database Error ❌</h2>
        <p>{error}</p>
        <a href="/login">Go Back</a>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "GET":
        return render_template("forgot_password.html")

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    room_number = request.form.get(
        "room_number",
        ""
    ).strip()

    new_password = request.form.get(
        "new_password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )

    # Empty fields

    if (
        not student_id
        or not room_number
        or not new_password
        or not confirm_password
    ):

        return """
        <h2>Please fill all fields ❌</h2>

        <a href="/forgot_password">
            Try Again
        </a>
        """

    # Password matching

    if new_password != confirm_password:

        return """
        <h2>Passwords do not match ❌</h2>

        <a href="/forgot_password">
            Try Again
        </a>
        """

    # Password length

    if len(new_password) < 6:

        return """
        <h2>Password must contain at least 6 characters ❌</h2>

        <a href="/forgot_password">
            Try Again
        </a>
        """

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # Verify student

        cursor.execute(
            """
            SELECT id
            FROM students
            WHERE student_id = %s
            AND room_number = %s
            """,
            (
                student_id,
                room_number
            )
        )

        student = cursor.fetchone()

        if not student:

            return """
            <!DOCTYPE html>
            <html>

            <body style="
                font-family:Arial;
                text-align:center;
                padding-top:80px;
            ">

                <h2>Student Details Not Found ❌</h2>

                <p>
                    Student ID or Room Number is incorrect.
                </p>

                <br>

                <a href="/forgot_password">
                    Try Again
                </a>

            </body>
            </html>
            """

        # Update password

        cursor.execute(
            """
            UPDATE students
            SET password = %s
            WHERE student_id = %s
            """,
            (
                new_password,
                student_id
            )
        )

        connection.commit()

        return """
        <!DOCTYPE html>
        <html>

        <head>
            <title>Password Reset</title>
        </head>

        <body style="
            font-family:Arial;
            background:#f4f7fb;
            text-align:center;
            padding-top:80px;
        ">

            <div style="
                background:white;
                width:450px;
                max-width:90%;
                margin:auto;
                padding:40px;
                border-radius:12px;
                box-shadow:0 4px 15px rgba(0,0,0,0.1);
            ">

                <h1 style="color:#166534;">
                    Password Reset Successfully! ✅
                </h1>

                <p>
                    Your password has been changed successfully.
                </p>

                <br>

                <a href="/login"
                   style="
                   background:#1e3a8a;
                   color:white;
                   padding:12px 25px;
                   text-decoration:none;
                   border-radius:6px;
                   ">
                   Login Now
                </a>

            </div>

        </body>

        </html>
        """

    except mysql.connector.Error as error:

        return f"""
        <h2>MySQL Database Error ❌</h2>

        <p>{error}</p>

        <a href="/forgot_password">
            Go Back
        </a>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    student_id = request.args.get("student_id")

    if not student_id:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                id,
                student_name,
                student_id,
                room_number
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:

            return """
            <h2>Student Not Found ❌</h2>

            <a href="/login">
                Login
            </a>
            """

        return render_template(
            "student_dashboard.html",
            student=student
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>MySQL Database Error ❌</h2>
        <p>{error}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# SUBMIT COMPLAINT
# =========================================================

@app.route("/complaint", methods=["GET", "POST"])
def complaint():

    # Show complaint page

    if request.method == "GET":

        student_id = request.args.get("student_id")

        if not student_id:
            return redirect(url_for("login"))

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT
                    id,
                    student_name,
                    student_id,
                    room_number
                FROM students
                WHERE student_id = %s
                """,
                (student_id,)
            )

            student = cursor.fetchone()

            if not student:

                return """
                <h2>Student Not Found ❌</h2>
                <a href="/login">Login</a>
                """

            return render_template(
                "complaint.html",
                student=student
            )

        except mysql.connector.Error as error:

            return f"""
            <h2>MySQL Database Error ❌</h2>
            <p>{error}</p>
            """

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    # Form values

    student_name = request.form.get(
        "student_name",
        ""
    ).strip()

    student_id = request.form.get(
        "student_id",
        ""
    ).strip()

    room_number = request.form.get(
        "room_number",
        ""
    ).strip()

    category = request.form.get(
        "category",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    # Empty complaint

    if not category or not description:

        return invalid_complaint(student_id)

    # Convert description to lowercase

    description_lower = description.lower()

    clean_text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        description_lower
    )

    words = clean_text.split()

    # Valid hostel keywords

    valid_words = {
        "hostel",
        "room",
        "water",
        "food",
        "mess",
        "electricity",
        "electric",
        "current",
        "power",
        "light",
        "fan",
        "wifi",
        "internet",
        "bathroom",
        "washroom",
        "toilet",
        "clean",
        "cleaning",
        "garbage",
        "waste",
        "bed",
        "chair",
        "table",
        "cupboard",
        "door",
        "window",
        "maintenance",
        "repair",
        "leak",
        "leakage",
        "security",
        "warden",
        "staff",
        "drinking",
        "supply",
        "mosquito",
        "pest",
        "canteen",
        "laundry",
        "geyser",
        "shower",
        "drainage",
        "pipe",
        "tap",
        "lock",
        "camera",
        "bulb"
    }

    # Clearly invalid topics

    invalid_words = {
        "mobile",
        "phone",
        "iphone",
        "laptop",
        "computer",
        "bike",
        "car",
        "money",
        "salary",
        "movie",
        "movies",
        "game",
        "games",
        "birthday",
        "shopping",
        "dress",
        "clothes",
        "relationship",
        "boyfriend",
        "girlfriend",
        "friend",
        "vacation",
        "holiday",
        "trip",
        "love",
        "personal",
        "watch",
        "headphone",
        "headphones",
        "charger"
    }

    # Reject clearly invalid complaint

    if any(
        word in invalid_words
        for word in words
    ):

        return invalid_complaint(student_id)

    # Must contain hostel-related word

    if not any(
        word in valid_words
        for word in words
    ):

        return invalid_complaint(student_id)

    # Generate complaint ID

    complaint_id = (
        "HC"
        + str(random.randint(1000, 9999))
    )

    complaint_date = datetime.now()

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO complaints
            (
                complaint_id,
                student_id,
                student_name,
                room_number,
                category,
                description,
                complaint_date,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            """,
            (
                complaint_id,
                student_id,
                student_name,
                room_number,
                category,
                description,
                complaint_date,
                "Submitted"
            )
        )

        connection.commit()

        return complaint_success(
            complaint_id,
            student_id
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>MySQL Database Error ❌</h2>

        <p>{error}</p>

        <a href="/complaint?student_id={student_id}">
            Go Back
        </a>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# INVALID COMPLAINT
# =========================================================

def invalid_complaint(student_id):

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Invalid Complaint</title>

        <style>

            body {{
                font-family:Arial;
                background:#f4f7fb;
                text-align:center;
                padding-top:70px;
            }}

            .box {{
                background:white;
                width:550px;
                max-width:90%;
                margin:auto;
                padding:40px;
                border-radius:12px;
                box-shadow:0 4px 15px rgba(0,0,0,0.1);
            }}

            h1 {{
                color:#dc2626;
            }}

            a {{
                display:inline-block;
                margin-top:20px;
                padding:12px 25px;
                background:#1e3a8a;
                color:white;
                text-decoration:none;
                border-radius:6px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>
                ❌ Invalid Hostel Complaint
            </h1>

            <p>
                This is not a valid hostel-related complaint.
            </p>

            <p>
                Please enter a genuine hostel problem such as:
            </p>

            <p>
                Water • Food • Electricity • Room Maintenance
                • Bathroom • Cleaning • Wi-Fi • Security
            </p>

            <a href="/complaint?student_id={student_id}">
                Try Again
            </a>

        </div>

    </body>

    </html>
    """


# =========================================================
# COMPLAINT SUCCESS
# =========================================================

def complaint_success(
    complaint_id,
    student_id
):

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Complaint Submitted</title>

        <style>

            body {{
                font-family:Arial;
                background:#f4f7fb;
                text-align:center;
                padding-top:70px;
            }}

            .box {{
                background:white;
                width:550px;
                max-width:90%;
                margin:auto;
                padding:40px;
                border-radius:12px;
                box-shadow:0 4px 15px rgba(0,0,0,0.1);
            }}

            h1 {{
                color:#166534;
            }}

            .id {{
                font-size:28px;
                font-weight:bold;
                color:#1e3a8a;
                margin:20px;
            }}

            a {{
                display:inline-block;
                margin:7px;
                padding:12px 20px;
                background:#1e3a8a;
                color:white;
                text-decoration:none;
                border-radius:6px;
            }}

        </style>

    </head>

    <body>

        <div class="box">

            <h1>
                Complaint Submitted Successfully! ✅
            </h1>

            <p>
                Your valid hostel complaint has been submitted.
            </p>

            <p>
                Complaint ID
            </p>

            <div class="id">
                {complaint_id}
            </div>

            <p>
                Status:
                <strong>Submitted</strong>
            </p>

            <br>

            <a href="/my_complaints?student_id={student_id}">
                My Complaints
            </a>

            <a href="/complaint?student_id={student_id}">
                Submit Another
            </a>

        </div>

    </body>

    </html>
    """


# =========================================================
# MY COMPLAINTS
# =========================================================

@app.route("/my_complaints")
def my_complaints():

    student_id = request.args.get("student_id")

    if not student_id:
        return redirect(url_for("login"))

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                complaint_id,
                student_id,
                student_name,
                room_number,
                category,
                description,
                complaint_date,
                status
            FROM complaints
            WHERE student_id = %s
            ORDER BY complaint_date DESC
            """,
            (student_id,)
        )

        complaints = cursor.fetchall()

        return render_template(
            "my_complaints.html",
            complaints=complaints
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>MySQL Database Error ❌</h2>

        <p>{error}</p>
        """

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# =========================================================
# START FLASK SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("======================================")
    print(" HOSTEL COMPLAINT MANAGEMENT SYSTEM")
    print("======================================")
    print("Server is starting...")
    print("FLASK STARTING NOW...")
    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
