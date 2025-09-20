"""This is an application used to create and log "Workouts of the Day" (WOD) in a crossfit trainning center"""

import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
import config
import db
import workouts

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    """Front-page view"""
    if "user_id" not in session:
        return redirect("/login")
    workout_list = workouts.list_workouts(user_id=session["user_id"])
    return render_template("index.html", workouts=workout_list)

@app.route("/new_log", methods=["GET", "POST"])
def new_log():
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
                sql = """INSERT INTO achievements 
                         (achievement_date, achievement_text, user_id, workout_id) 
                         VALUES (?, ?, ?, ?)"""
                db.execute(sql, [log_date, log_notes, user_id, int(wod_id)])
                return redirect("/")

    return render_template("new_log.html", wods=all_wods, selected_wod=selected_wod)

@app.route("/new_workout")
def new_workout():
    """register a new workout log"""
    return render_template("new_workout.html")

@app.route("/create_workout", methods=["POST"])
def create_workout():
    """create workout"""
    workout_date=request.form["workout_date"]
    warmup_description=request.form["warmup_description"]
    wod_description=request.form["wod_description"]
    extras_description=request.form["extras_description"]
    user_id=session["user_id"]

    workouts.add_workout(workout_date,warmup_description,wod_description,extras_description,user_id)

    return redirect("/")

@app.route("/register")
def register():
    """register a new user"""
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    """create a new user profile"""
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
    """log in to the application"""
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
    """logout from the application and delete the session"""
    del session["user_id"]
    del session["username"]
    return redirect("/")
