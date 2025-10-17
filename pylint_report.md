#Pylint report

Pylint gives the following report about the application:

```
************* Module app
app.py:426:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
************* Module workouts
workouts.py:5:0: R0913: Too many arguments (7/5) (too-many-arguments)
workouts.py:5:0: R0917: Too many positional arguments (7/5) (too-many-positional-arguments)
workouts.py:84:0: R0913: Too many arguments (7/5) (too-many-arguments)
workouts.py:84:0: R0917: Too many positional arguments (7/5) (too-many-positional-arguments)
workouts.py:1:0: R0801: Similar lines in 2 files
==seed:[33:38]
==workouts:[12:17]
    sql = """INSERT INTO workouts (
                workout_date,
                warmup_description,
                wod_description,
                extras_description, (duplicate-code)

------------------------------------------------------------------
Your code has been rated at 9.88/10 (previous run: 9.86/10, +0.02)

```
Let's review these notifications by category:

## Inconsistent return statments

```
app.py:426:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
```
This is related to the login-funktion. If everything is not ok in the login (username, password etc), the login page is rendered with an appropriate error message included. If everything is ok, the user is routed to the application main page. The author of the application has decided that this is an acceptable functionality.

## Too many positional arguments/Too many arguments:
```
workouts.py:5:0: R0913: Too many arguments (7/5) (too-many-arguments)
workouts.py:5:0: R0917: Too many positional arguments (7/5) (too-many-positional-arguments)
```
It is usually considered that 5 arguments is a maximum limit for one function, but in this application the author decided to use at maximum 7 on two functions where it was needed due to the nature of the function defined.


## Similar lines in 2 files:
```
workouts.py:1:0: R0801: Similar lines in 2 files
```
This is a remark that seed.py and workouts.py have similar lines. Seed.py is not part of the application itself, it is just external tool to create a test database and therefore this warning can be ignored.

