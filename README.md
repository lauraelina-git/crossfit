# Crossfit diary
This application is a webtool that an athlete can use to log his/her crossfit workouts. In crossfit, the workouts are called "Workout-of-the-Days", or with the accronym "WOD", carrying the date on which they are planned to be done. Usually all crossfit centers in the world follow a quasi-similar programming, varying only slightly. Usually all training centers have a programming cycle of 4-6 weeks, where the first week is lighter, and the second-last week hardest, and the last week is then called "deload", which again is a very light training week in order to make sure the athletes recover before the next round starts. This tool uses a 4-week programming.

## Users:
* A user can be created by using the Sign Up-functionality on the frontpage
* User can sign in to the application from the frontpage (login)
* When a user is created, the user can also be given "coach"-rights by ticking a box in the registration form.
* The username and password have limitations that are described on the registration page

## Workouts:
* Only Coaches can create WODs (workouts).
* In a workout, it is mandatory to add the date on which the WOD is planned to be done and the description of the workout.
* There are also fields called "warm-up" and "extras". These are not mandatory to be done when doing the WOD, and they are not mandatory to be filled in a workout when workout is created
* There are 4 levels of the workouts (programming weeks 1/2/3 and deload), and assigning a programming week is also mandatory.
* All coaches can edit workouts, both the ones they have created and the ones other coaches have created
* Workouts cannot be deleted.
* All workouts have their own page, on which there may be image of the workout and where the workout can be commented
* The users that have completed the WOD are listed on the WOD's page with their results. Their results can be liked or a like given can be removed (double likes not possible!)
* Also an image can be added/edited to the workout by the coaches.

## Logging the trainings and other application functions for all users (both athletes with and without coach-rights):
* Users can choose any WOD created and add their own training log with the date they did the WOD (this does not have to be the same as the WOD date, altough in following the programming it is adviced to do the workouts on the day they are planned to be done)
* A training log can be added from the users own diary from the link "Create a new training log"
* A training log can also be added from the workout's page using "Add this workout to the training log"-link
* Users can edit and remove their own training logs.
* User can search for the WODs created using keywords in the WOD description, but not in the warmup or extras, because they are not parts of the official programming of workouts.
* When a user completes a training, it is listed to the users diary
* There is a user page (Diary) where the athelete can review his accomplishments
* The total amount of workouts done by the user and the date of the last workout done is mentioned in the diary

## Testing the application

Install `flask`:

```
$ pip install flask
```

To test the application, there are two options:
1) to start with an empty database, just start the application, it will create the required database automatically.
```
$ flask run
```
2) or to create a test database. The current values in the seed.py are:
* create_users(1000) --> creates 1000 users
* create_workouts(2000) --> create 2000 workouts
* create_logs(5000) --> create 5000 logs
It will take some time to create the database, and therefore these can be modified in the seed.py file.
Creating the test database can be done by running first seed.py with command
```
$ python3 seed.py
```
and then starting the application using
```
$ flask run
```
Then the application can be tested over a browser on 127.0.0.1:5000.
