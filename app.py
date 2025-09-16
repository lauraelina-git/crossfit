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
    if "user_id" not in session: #if the user is not logged in... we shall go to login
        return redirect("/login")
    workout_list = workouts.list_workouts(user_id=session["user_id"])
    return render_template("index.html", workouts=workout_list)

@app.route("/workout/<int:workout_id>")
def show_workout(workout_id):
    workout=workouts.list_workout(workout_id)
    return render_template("show_workout.html", workout=workout)

@app.route("/new_workout")
def new_workout():
  return render_template("new_workout.html")

@app.route("/create_workout", methods=["POST"])
def create_workout():
    workout_date=request.form["workout_date"]
    warmup_description=request.form["warmup_description"]
    wod_description=request.form["wod_description"]
    extras_description=request.form["extras_description"]
    user_id=session["user_id"]

    workouts.add_workout(workout_date, warmup_description, wod_description, extras_description, user_id)    

    return redirect("/") #for now let's go to the frontpage, but figure out something better later

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        return "ERROR: The passwords must be the same" #this should be re-routed to a sign_in/sign_up page with a note

    is_coach = 1 if request.form.get("is_coach") else 0
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash, is_coach) VALUES (?, ?, ?)"
        db.execute(sql, [username, password_hash, is_coach])
    except sqlite3.IntegrityError:
        return "ERROR: The username is already in use" #this should be re-routed to a sign_in/sign_up page with note

    return redirect("/login") #return to login

@app.route("/login", methods=["GET","POST"])
def login():
    error=None
    if request.method == "GET":
      return render_template("login.html")

    if request.method=="POST":
      username = request.form["username"]
      password = request.form["password"]

      sql = "SELECT id, password_hash FROM users WHERE username = ?"
      result = db.query(sql, [username])[0]
      user_id = result["id"]
      password_hash = result["password_hash"]

      if check_password_hash(password_hash, password):
          session["user_id"]= user_id
          session["username"] = username
          return redirect("/")
      else:
          return "ERROR: wrong username or password"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
