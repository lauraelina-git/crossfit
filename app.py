"""Application to create and log Crossfit "Workouts of the Day" (WOD)"""

import sqlite3
from functools import wraps
import secrets
import os
import re
from flask import Flask
from flask import redirect, render_template, request, session, url_for
from flask import abort
from werkzeug.security import check_password_hash, generate_password_hash
import markupsafe
import config
import db
import workouts
import logs

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

IS_INITIALIZED = False

if not IS_INITIALIZED:
    db.initialize_db()
    IS_INITIALIZED = True

def check_csrf():
    """check csrf token validity"""
    if "csrf_token" not in request.form:
        print("csrf token missing")
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        print("csrf token mismatch")
        abort(403)

@app.template_filter('show_lines')
def show_lines(text):
    """Split text into lines for display."""
    return markupsafe.Markup('<br>'.join(text.splitlines()))

def login_required(f):
    """check whether the user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    """Front-page (Diary) view"""
    page_workouts = request.args.get('page_workouts', 1, type=int)
    page_logs = request.args.get('page_logs', 1, type=int)
    per_page = 10

    user_workoutlist = workouts.list_workouts(
        page=page_workouts, per_page=per_page, user_id=session["user_id"])
    workout_list = workouts.list_workouts(page=page_workouts, per_page=per_page)
    user_logs = logs.list_logs(user_id=session["user_id"], page=page_logs, per_page=per_page)

    total_logs = logs.count_logs(user_id=session["user_id"])
    total_workouts = workouts.count_workouts()

    wod_count, last_training = logs.log_summary(user_id=session["user_id"])
    if not last_training:
        last_training = "No logs yet"

    return render_template(
        "index.html",
        user_workouts=user_workoutlist,
        workouts=workout_list,
        logs=user_logs,
        total_logs=total_logs,
        total_workouts=total_workouts,
        wod_count=wod_count,
        last_training=last_training,
        page_workouts=page_workouts,
        page_logs=page_logs,
        per_page=per_page
    )

@app.route("/new_log", methods=["GET", "POST"])
@login_required
def new_log():
    """Create a new log"""
    all_wods = workouts.list_workouts(page=1, per_page=30)
    selected_wod = None

    if request.method == "POST":
        check_csrf()
        if "select_wod" in request.form:
            wod_id = request.form.get("workout_id")
            if wod_id:
                selected_wod = workouts.list_workout(int(wod_id))

        elif "save_log" in request.form:
            wod_id = request.form.get("workout_id")
            log_notes = request.form.get("log_notes")
            log_date = request.form.get("log_date")
            user_id = session["user_id"]

            if wod_id and log_notes and log_date:
                log_id = logs.add_log(log_date, log_notes, user_id, int(wod_id))
                if log_id:
                    return redirect("/")
            else:
                print("Missing required fields.")
    return render_template(
        "new_log.html", wods=all_wods, selected_wod=selected_wod)

@app.route("/log/<int:log_id>")
@login_required
def show_log(log_id):
    """Showing the user's trainging logs"""

    training_log = logs.list_log(int(log_id))
    if not training_log:
        return "training log not found", 404

    return render_template("show_log.html", log=training_log)

@app.route("/edit_log/<int:log_id>", methods=["GET","POST"])
@login_required
def edit_log(log_id):
    """Editing the user's logs"""
    training_log = logs.list_log(log_id)
    if not training_log:
        return "Log not found", 404

    if training_log["user_id"] != session["user_id"]:
        return "Unauthorized to change the log", 403

    if request.method == "POST":
        check_csrf()
        log_date = request.form.get("log_date")
        log_text = request.form.get("log_notes")

        if log_date and log_text:
            logs.update_log(log_id, log_date, log_text, session["user_id"])
            return redirect(f"/log/{log_id}")

        return render_template(
            "edit_log.html", log=training_log, error="All fields required")

    return render_template("edit_log.html", log=training_log)

@app.route("/remove_log/<int:log_id>", methods=["GET","POST"])
@login_required
def remove_log(log_id):
    """Remove a training log"""
    user_id = session["user_id"]

    if request.method == "GET":
        current_log = logs.list_log(log_id)
        return render_template("remove_log.html", log=current_log)

    if request.method == "POST":
        check_csrf()
        logs.remove_log(log_id, user_id)

    return redirect("/")

@app.route("/add_log/<int:workout_id>", methods=["GET", "POST"])
@login_required
def add_log(workout_id):
    """Add a training log directly from the workout description"""
    selected_wod = workouts.list_workout(workout_id)
    if not selected_wod:
        return "Workout not found", 404

    if request.method == "POST":
        check_csrf()
        log_notes = request.form.get("log_notes")
        log_date = request.form.get("log_date")
        user_id = session["user_id"]

        if len(log_notes)>150:
            error = "Too much text added to notes"
            return render_template(
                "add_log.html", selected_wod=selected_wod, error=error)

        if log_notes and log_date:
            log_id = logs.add_log(log_date, log_notes, user_id, workout_id)
            if log_id:
                return redirect("/")
        else:
            error = "Missing required fields."
            return render_template(
                "add_log.html", selected_wod=selected_wod, error=error)

    return render_template("add_log.html", selected_wod=selected_wod)

@app.route("/new_workout")
@login_required
def new_workout():
    """Register a new workout"""
    return render_template("new_workout.html")

@app.route("/create_workout", methods=["GET","POST"])
@login_required
def create_workout():
    """Create workout"""
    if request.method == "GET":
        return render_template("new_workout.html")

    check_csrf()

    wod_date = request.form["workout_date"]
    warmup_description = request.form["warmup_description"]
    wod_description = request.form["wod_description"]
    extras_description = request.form["extras_description"]
    user_id = session["user_id"]
    programming = request.form.get("week")
    workout_image_file = None

    if 'workout_image' in request.files:
        file = request.files['workout_image']
        if file and file.filename != '':
            workout_image_file = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], workout_image_file))

    if len(warmup_description)>300 or len(wod_description)>300 or len(extras_description)>300:
        return render_template(
            "new_workout.html", 
            error="Too long description in one of the fields")

    if not wod_date or not wod_description or not programming:
        return render_template(
            "new_workout.html", 
            error="WOD date, description and programming week of the WOD are mandatory")

    workouts.add_workout(
        wod_date,
        warmup_description,
        wod_description,
        extras_description,
        user_id,
        programming,
        workout_image_file
        )
    return redirect("/")

@app.route("/workout/<int:workout_id>", methods=["GET", "POST"])
@login_required
def show_workout(workout_id):
    """Showing the workout details"""
    wod = workouts.list_workout(int(workout_id))
    programming = workouts.get_programming(workout_id)

    comments = workouts.list_comments(workout_id, page=1, per_page=10)

    page_results = request.args.get('page_results', 1, type=int)
    results = logs.list_results(workout_id, session.get("user_id"), page=page_results)
    total_results = logs.count_results(workout_id)

    if request.method == "POST":
        check_csrf()
        comment_text = request.form.get("comment_text")
        user_id = session["user_id"]

        if comment_text:
            workouts.add_comment(workout_id, user_id, comment_text)
            return redirect(url_for('show_workout', workout_id=workout_id))
        print("Comment text is missing.")

    if not wod:
        return "Workout not found", 404

    return render_template(
        "show_workout.html",
        workout=wod,
        results=results,
        comments=comments,
        programming=programming,
        page_results=page_results,
        total_results=total_results,
        per_page=10
    )

@app.route("/edit_workout/<int:workout_id>", methods=["GET","POST"])
@login_required
def edit_workout(workout_id):
    """Edit an existing workout (coaches only)"""
    if session.get("is_coach") != 1:
        return "Unauthorized: only coaches can edit workouts", 403

    wod = workouts.list_workout(workout_id)
    if not wod:
        return "Workout not found", 404

    if request.method == "POST":
        check_csrf()
        wod_date = request.form.get("workout_date")
        warmup_description = request.form.get("warmup_description")
        wod_description = request.form.get("wod_description")
        extras_description = request.form.get("extras_description")
        programming = request.form.get("week")
        workout_image_file = wod['workout_image']

        if 'workout_image' in request.files:
            file = request.files['workout_image']
            if file and file.filename != '':
                workout_image_file = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], workout_image_file))

        if wod_date and wod_description and programming:
            workouts.edit_workout(
                wod_date,
                warmup_description,
                wod_description,
                extras_description,
                workout_image_file,
                workout_id,
                programming
                )
            return redirect(f"/workout/{workout_id}")
        return render_template(
                "edit_workout.html",
                workout=wod,
                error="Date workout description and programming required"
                )
    return render_template("edit_workout.html", workout=wod)

@app.route("/find_workout")
@login_required
def find_workout():
    """Find workout"""

    results = []
    query = request.args.get("query")
    page = request.args.get('page', 1, type=int)
    per_page = 10
    error = None

    if query:
        results = workouts.find_workouts(query, page, per_page)
        total_results = workouts.count_workouts()
        if not results:
            error = "No workout found"
    else:
        total_results = 0

    return render_template(
        "find_workout.html",
        query=query,
        results=results,
        error=error,
        page=page,
        total_results=total_results,
        per_page=per_page
    )
@app.route("/like_result/<int:log_id>", methods=["POST"])
@login_required
def like_result(log_id):
    """Like or unlike a log entry"""
    user_id = session["user_id"]
    existing_like = logs.check_likes(log_id, user_id)

    if existing_like:
        logs.unlike_log(log_id, user_id)
    else:
        logs.like_log(log_id, user_id)
    return redirect(request.referrer)

@app.route("/register")
def register():
    """Register a new user"""
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    """Create a new user profile"""
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if not validate_username(username):
        return render_template(
            "register.html",
            error="ERROR: Username must be between 3 and 20 characters long "
            "and can only contain alphanumeric characters and underscores.")

    if password1 != password2:
        return render_template(
            "register.html",
            error="ERROR: The passwords must be the same")

    if not validate_password(password1):
        return render_template(
            "register.html",
            error="ERROR: Password must be at least 8 characters long and contain "
            "at least one uppercase letter, one lowercase letter, "
            "one number, and one special character.")

    is_coach = 1 if request.form.get("is_coach") else 0
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash, is_coach) VALUES (?, ?, ?)"
        db.execute(sql, [username, password_hash, is_coach])
    except sqlite3.IntegrityError:
        return render_template(
            "register.html",
            error="ERROR: The username is already in use")

    return redirect("/login")

def validate_username(username):
    """Validate username according to specified rules."""
    if len(username) < 3 or len(username) > 20:
        return False
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False
    return True

def validate_password(password):
    """Validate password according to specified rules."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

@app.route("/login", methods=["GET","POST"])
def login():
    """Log in to the application"""
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash, is_coach FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if not result:
            return render_template(
                "login.html", error="Wrong username or password")

        user = result[0]
        user_id = user["id"]
        password_hash = user["password_hash"]
        is_coach = user["is_coach"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["csrf_token"] = secrets.token_hex(16)
            session["username"] = username
            session["is_coach"] = is_coach
            return redirect("/")

        return render_template(
            "login.html", error="Wrong username or password")

@app.route("/logout")
def logout():
    """Logout from the application and delete the session"""
    if "user_id" not in session:
        return redirect("/login")
    del session["user_id"]
    del session["username"]
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
