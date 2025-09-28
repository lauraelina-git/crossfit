"""Application to create and log Crossfit "Workouts of the Day" (WOD)"""

import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import workouts
import logs

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.route("/")
def index():
    """Front-page view"""
    if "user_id" not in session:
        return redirect("/login")
    user_workoutlist= workouts.list_workouts(user_id=session["user_id"])
    workout_list= workouts.list_workouts()
    user_logs=logs.list_logs(user_id=session["user_id"])
    return render_template(
        "index.html",
        user_workouts = user_workoutlist,
        workouts = workout_list,
        logs=user_logs
        )

@app.route("/new_log", methods=["GET", "POST"])
def new_log():
    """Create a new log"""
    if "user_id" not in session:
        return redirect("/login")

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
def show_log(log_id):
    """Showing the user's trainging logs"""
    if "user_id" not in session:
        return redirect("/login")

    training_log = logs.list_log(int(log_id))
    if not training_log:
        return "training log not found", 404

    return render_template("show_log.html", log=training_log)

@app.route("/edit_log/<int:log_id>", methods=["GET","POST"])
def edit_log(log_id):
    """Editing the user's logs"""
    if "user_id" not in session:
        return redirect("/login")

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

@app.route("/new_workout")
def new_workout():
    """Register a new workout"""
    return render_template("new_workout.html")

@app.route("/create_workout", methods=["POST"])
def create_workout():
    """Create workout"""
    wod_date=request.form["workout_date"]
    warmup_description=request.form["warmup_description"]
    wod_description=request.form["wod_description"]
    extras_description=request.form["extras_description"]
    user_id=session["user_id"]

    if not wod_date or not wod_description:
        return render_template(
            "new_workout.html", 
            error="WOD date and description of the WOD are mandatory")

    workouts.add_workout(wod_date,warmup_description,wod_description,extras_description,user_id)
    return redirect("/")

@app.route("/workout/<int:workout_id>")
def show_workout(workout_id):
    """Showing the workout details"""
    if "user_id" not in session:
        return redirect("/login")

    wod = workouts.list_workout(int(workout_id))
    if not wod:
        return "Workout not found", 404

    return render_template("show_workout.html", workout=wod)

@app.route("/edit_workout/<int:workout_id>", methods=["GET","POST"])
def edit_workout(workout_id):
    """Edit an existing workout (coaches only)"""

    if "user_id" not in session:
        return redirect("/login")

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

        return render_template(
            "edit_workout.html",
            workout=wod,
            error="Date and workout description required"
            )

    return render_template("edit_workout.html", workout=wod)


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
    del session["user_id"]
    del session["username"]
    return redirect("/")
