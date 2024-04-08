from datetime import datetime
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///entry.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    entries = db.execute("SELECT * FROM entry WHERE user_id = ?", session["user_id"])
    print(f"{entries}")
    return render_template("index.html",entries = entries)

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    id = request.form.get("entry")
    print
    db.execute("DELETE FROM entry WHERE entry_id = ?",id)
    return redirect("/")

@app.route("/view", methods=["GET", "POST"])
@login_required
def view():
    if request.method == "POST":
        id = request.form.get("entry")
        entry = db.execute("SELECT * FROM entry WHERE entry_id = ?",id)
        print(f"{entry}")
        return render_template("view.html",entry = entry[0])
    return redirect("/")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return redirect("/")

@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    id = request.form.get("entry")
    display = db.execute("SELECT * FROM entry WHERE entry_id = ?",id)
    print(f"{display}")
    return render_template("edit.html", entry = display[0])

@app.route("/edited", methods=["GET", "POST"])
@login_required
def edited():
    if request.method == "POST":
        id = request.form.get("id")
        print(f"{id}")
        if not id:
            return apology("You are a bad Person for messing with my html")
        title = request.form.get("title")
        print(f"{title}")

        if not title:
            return apology("Title Missing")
        entry = request.form.get("entry")
        print(f"{entry}")

        if not entry:
            return apology("Entry Missing")
        time = str(datetime.now().strftime('%Y-%m-%d %H:%M'))
        db.execute("UPDATE entry SET edit_time = ?, title = ?, entry = ? WHERE entry_id = ?", time, title, entry, id)
        return redirect("/")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # getting the form data
    if request.method == "POST":
        username = request.form.get("username")
        confirmation = request.form.get("confirmation")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = ?",username)
        print(f"{user}")
        # Checking for Error
        if not username:
            return apology("No Username was entered", 400)
        if user and username == user[0]["username"]:
            return apology("Username Exists", 400)
        if not password:
            return apology("No Password was entered", 400)
        if password != confirmation:
            return apology("Password and Confirmation password was not same", 400)

        # adding the user into the database
        hashedPassword = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashedPassword)
        return redirect("/login")

    return render_template("register.html")

@app.route("/new",methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        title = request.form.get("title")
        if not title:
            return apology("Empty Title",404)
        entry = request.form.get("entry")
        if not entry:
            return apology("Empty Entry",404)


        entry_time = str(datetime.now().strftime('%Y-%m-%d %H:%M'))

        db.execute("INSERT INTO entry (user_id, entry_time, edit_time, title, entry) VALUES (?, ?, ?, ?, ?)", session["user_id"], entry_time, entry_time, title, entry)
        return redirect("/")

    return render_template("new.html")

if __name__ == '__main__':
    app.run(debug=True)
