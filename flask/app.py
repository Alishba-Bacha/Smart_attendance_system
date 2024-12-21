from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from ultralytics import YOLO
import os
import sqlite3
from datetime import datetime

# Initialize Flask App
app = Flask(_name_)
app.secret_key = "secretkey"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# YOLO model
model = YOLO('yolo11n.pt')

DATABASE = "attendance_system.db"

# Initialize database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                day TEXT NOT NULL,
                class_name TEXT NOT NULL,
                registration_number TEXT NOT NULL
            )
        """)
        conn.commit()

# User Authentication
class User(UserMixin):
    def _init_(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return User(*row)
    return None

# Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
                conn.commit()
                flash("Signup successful! You can now login.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username already exists. Please choose another.")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
            row = cursor.fetchone()
            if row:
                user = User(*row)
                login_user(user)
                return redirect(url_for("teacher_dashboard" if user.role == "teacher" else "student_dashboard"))
            else:
                flash("Invalid username or password.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/teacher", methods=["GET", "POST"])
@login_required
def teacher_dashboard():
    if current_user.role != "teacher":
        return redirect(url_for("home"))

    if request.method == "POST":
        # Handle file upload
        file = request.files["group_photo"]
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Detect students
            results = model.predict(source=filepath, save=True)
            detected_students = [result.label for result in results[0].boxes.data]

            # Mark attendance
            mark_attendance(detected_students)
            flash(f"Attendance marked for {len(detected_students)} students.")
            return redirect(url_for("teacher_dashboard"))

    return render_template("teacher.html")

@app.route("/student")
@login_required
def student_dashboard():
    if current_user.role != "student":
        return redirect(url_for("home"))

    # Fetch attendance records
    attendance_records = []
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT date, day, class_name FROM attendance WHERE registration_number = ?", (current_user.username,))
        attendance_records = cursor.fetchall()

    return render_template("student.html", attendance_records=attendance_records)

# Helper Function
def mark_attendance(detected_students):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        for regno in detected_students:
            cursor.execute("INSERT INTO attendance (date, day, class_name, registration_number) VALUES (?, ?, ?, ?)",
                           (current_date, current_day, "Class A", regno))
        conn.commit()

if _name_ == "_main_":
    init_db()
    app.run(debug=True)