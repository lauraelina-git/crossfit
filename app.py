"""Application to create and log Crossfit "Workouts of the Day" (WOD)"""

import sqlite3
from functools import wraps
from flask import Flask
from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import workouts
import logs

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

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
    user_workoutlist= workouts.list_workouts(user_id=session["user_id"])
    workout_list= workouts.list_workouts()
    user_logs=logs.list_logs(user_id=session["user_id"])

    wod_count, last_training = logs.log_summary(user_id=session["user_id"])
    if not last_training:
        last_training = "No logs yet"

    return render_template(
        "index.html",
        user_workouts = user_workoutlist,
        workouts = workout_list,
        logs=user_logs,
        wod_count=wod_count,
        last_training=last_training
        )

@app.route("/new_log", methods=["GET", "POST"])
@login_required
def new_log():
    """Create a new log"""
    all_wods = workouts.list_workouts()
    selected_wod = None

    if request.method == "POST":
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
    return render_template("new_log.html", wods=all_wods, selected_wod=selected_wod)

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
        log_date = request.form.get("log_date")
        log_text = request.form.get("log_notes")

        if log_date and log_text:
            logs.update_log(log_id, log_date, log_text, session["user_id"])
            return redirect(f"/log/{log_id}")

        return render_template("edit_log.html", log=training_log, error="All fields required")

    return render_template("edit_log.html", log=training_log)

@app.route("/remove_log/<int:log_id>", methods=["GET","POST"])
@login_required
def remove_log(log_id):
    """Remove a training log"""

    user_id = session["user_id"]

    if request.method == "GET":
        current_log=logs.list_log(log_id)
        return render_template("remove_log.html", log=current_log)

    if request.method =="POST":
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
        log_notes = request.form.get("log_notes")
        log_date = request.form.get("log_date")
        user_id = session["user_id"]

        if len(log_notes)>150:
            error = "Too much text added to notes"
            return render_template("add_log.html", selected_wod=selected_wod, error=error)

        if log_notes and log_date:
            log_id = logs.add_log(log_date, log_notes, user_id, workout_id)
            if log_id:
                return redirect("/")
        else:
            error = "Missing required fields."
            return render_template("add_log.html", selected_wod=selected_wod, error=error)

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
    wod_date=request.form["workout_date"]
    warmup_description=request.form["warmup_description"]
    wod_description=request.form["wod_description"]
    extras_description=request.form["extras_description"]
    user_id=session["user_id"]
    programming=request.form.get("week")

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
        programming)
    return redirect("/")

@app.route("/workout/<int:workout_id>", methods=["GET", "POST"])
@login_required
def show_workout(workout_id):
    """Showing the workout details"""
    wod = workouts.list_workout(int(workout_id))
    results=logs.list_results(workout_id, session.get("user_id"))
    comments = workouts.list_comments(workout_id)
    programming = workouts.get_programming(workout_id)
    if not wod:
        return "Workout not found", 404

    if request.method == "POST":
        comment_text = request.form.get("comment_text")
        if comment_text:
            workouts.add_comment(workout_id, session["user_id"], comment_text)
            flash("Comment added")
            return redirect(f"/workout/{workout_id}")

    return render_template(
            "show_workout.html",
            workout = wod,
            results = results,
            comments = comments,
            programming = programming
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
        wod_date=request.form.get("workout_date")
        warmup_description=request.form.get("warmup_description")
        wod_description=request.form.get("wod_description")
        extras_description=request.form.get("extras_description")

        if wod_date and wod_description:
            workouts.edit_workout(
                wod_date,
                warmup_description,
                wod_description,
                extras_description,
                workout_id
                )
            return redirect(f"/workout/{workout_id}")
        return render_template(
                "edit_workout.html",
                workout=wod,
                error="Date and workout description required"
                )
    return render_template("edit_workout.html", workout=wod)

@app.route("/find_workout")
@login_required
def find_workout():
    """Find workout"""

    results=[]
    query=request.args.get("query")
    if query:
        results=workouts.find_workouts(query)
    else:
        query=""

    return render_template(
        "find_workout.html",
        query=query,
        results=results
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

    if password1 != password2:
        return render_template("register.html", error="ERROR: The passwords must be the same")


    is_coach = 1 if request.form.get("is_coach") else 0
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash, is_coach) VALUES (?, ?, ?)"
        db.execute(sql, [username, password_hash, is_coach])
    except sqlite3.IntegrityError:
        return render_template("register.html", error="ERROR: The username is already in use")

    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    """Log in to the application"""
    if request.method == "GET":
        return render_template("login.html")

    if request.method=="POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash, is_coach FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if not result:
            return render_template("login.html", error="Wrong username or password")

        user=result[0]
        user_id = user["id"]
        password_hash = user["password_hash"]
        is_coach=user["is_coach"]

        if check_password_hash(password_hash, password):
            session["user_id"]= user_id
            session["username"] = username
            session["is_coach"] = is_coach
            return redirect("/")

        return render_template("login.html", error="Wrong username or password")

@app.route("/logout")
def logout():
    """Logout from the application and delete the session"""
    if "user_id" not in session:
        return redirect("/login")
    del session["user_id"]
    del session["username"]
    return redirect("/")
