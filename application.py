import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///journal.db")

@app.route("/")
def index():
    db.execute("""
    DELETE FROM entries
    WHERE user_id is null
    """)
    return render_template("home.html")

@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    db.execute("""
    UPDATE entries
    SET user_id = ?
    WHERE user_id is null
    """, session["user_id"])

    journal = db.execute("""
    SELECT * FROM entries
    WHERE user_id = ?
    ORDER BY time DESC
    """, session["user_id"])

    # Prepare to send relevant data to dashboard page
    entries = []
    for row in journal:
        entries.append({
            "entry": row['entry'][0:80],
            "title": row['title'][0:10],
            "time": row['time'],
            "id": row['id']
        })

    # Add ellipsis to shortened entries if there is at least 1 entry
    if entries:
        for row in entries:
            if len(row['entry']) > 79:
                row['entry'] += "..."
            if len(row['title']) > 9:
                row['title'] += "..."

    return render_template("dashboard.html", entries=entries)

#CREATE TABLE entries (id INTEGER, user_id INTEGER, entry TEXT, title TEXT, time DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')), PRIMARY KEY(id), FOREIGN KEY(user_id) REFERENCES users(id));

@app.route("/view", methods=["POST"])
def view():
    viewid = request.form.get("edit")
    delid = request.form.get("delete")

    if delid:
        db.execute("""
        DELETE
        FROM entries
        WHERE id = ?
        """, delid)

        flash("Entry deleted!", "success")

        return redirect("/dashboard")

    elif viewid:
        entry = db.execute("""
        SELECT entry, title
        FROM entries
        WHERE id = ?
        """, viewid)

        return render_template("edit.html", entry=entry, viewid=viewid)


@app.route("/entry", methods=["POST"])
def entry():
    jentry = request.form.get("entry")
    title = request.form.get("title")

    if not jentry:
        flash("Entry cannot be blank", "error")
        return redirect("/")

    db.execute("""
    INSERT INTO entries (entry)
    VALUES (?)
    """, jentry)

    tempid = db.execute("""
    SELECT id
    FROM entries
    WHERE entry = ?
    """, jentry)

    if not title:
        title = "Untitled"

    # Ensure only this entry is updated by using the most recent id if entries are duplicated
    db.execute("""
    UPDATE entries
    SET title = ?
    WHERE id = ?
    """, title, tempid[-1]['id'])


    if session.get("user_id") is None:
        return redirect("/login")

    else:
        flash("Entry added!", "success")
        return redirect("/dashboard")


@app.route("/edit", methods=["POST"])
def edit():
    delid = request.form.get("delete")
    updateid = request.form.get("update")

    if not updateid:
        db.execute("""
        DELETE
        FROM entries
        WHERE id = ?
        """, delid)

        flash("Entry deleted")

    else:
        entry = request.form.get("entry")
        title = request.form.get("title")
        db.execute("""
        UPDATE entries
        SET entry = ?, title = ?, time = CURRENT_TIMESTAMP
        WHERE id = ?
        """, entry, title, updateid)

        flash("Entry updated!", "success")

    return redirect("/dashboard")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", "error")
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", "error")
            return render_template("login.html")

        # Query database for username
        rows = db.execute("""
        SELECT * FROM users
        WHERE username = ?
        """, request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password", "error")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        temp = request.form.get("username")
        flash(f"Welcome back {temp}!")

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    """Register user"""

    # Ensure username was submitted
    if not request.form.get("username"):
        flash("Must provide username", "error")
        return render_template("login.html")

    # Ensure password was submitted
    elif not request.form.get("password"):
        flash("Must provide password", "error")
        return render_template("login.html")

    # Ensure password was entered twice for confirmation
    elif not request.form.get("confirmation"):
        flash("Please confirm password", "error")
        return render_template("login.html")

    # Ensure password inputs match each other
    elif not request.form.get("password") == request.form.get("confirmation"):
        flash("Passwords do not match", "error")
        return render_template("login.html")

    # Ensure username is unique. Query database for username input by user. If length of this returned row is >0 then username
    # already exists
    rows = db.execute("""
    SELECT * FROM users
    WHERE username = ?
    """, request.form.get("username"))
    if len(rows) != 0:
        flash("That username is already taken", "error")
        return render_template("login.html")

    # If all prerequisites are successful, update database with new username and password(hashed) and return user to login screen
    db.execute("""
    INSERT INTO users (username, hash)
    VALUES (?, ?)
    """, request.form.get("username"), generate_password_hash(request.form.get("password")))

    # Prepare for auto-login (get username that was just inserted into database and set this id to the session id)
    rows = db.execute("""
    SELECT * FROM users
    WHERE username = ?
    """, request.form.get("username"))

    # Remember which user is logged in
    session["user_id"] = rows[0]["id"]

    flash("Registered!", "success")

    # Send logged-in user to their index page
    return redirect("/dashboard")

@app.route("/password", methods=["GET", "POST"])
@login_required
def password():

    if request.method == "GET":
        return render_template("password.html")
    else:
        # Get current user's login data
        rows = db.execute("""
        SELECT * FROM users
        WHERE id = ?
        """, session["user_id"])

        # Ensure password was submitted
        if not request.form.get("currentpassword"):
            flash("Must provide password", "error")
            return render_template("password.html")

        # Ensure new password was entered twice for confirmation
        elif not request.form.get("newpassword") or not request.form.get("confirmation"):
            flash("Please confirm password", "error")
            return render_template("password.html")

        # Ensure current password is correct
        elif not check_password_hash(rows[0]["hash"], request.form.get("currentpassword")):
            flash("Password incorrect", "error")
            return render_template("password.html")

        # Ensure new password inputs match each other
        elif not request.form.get("newpassword") == request.form.get("confirmation"):
            flash("Passwords do not match", "error")
            return render_template("password.html")

        # Ensure new password is different from current password
        elif check_password_hash(rows[0]["hash"], request.form.get("newpassword")):
            flash("New password must be different from current password", "error")
            return render_template("password.html")

        # Update password
        db.execute("""
        UPDATE users
        SET hash = ?
        WHERE id = ?
        """, generate_password_hash(request.form.get("newpassword")), session["user_id"])

        flash("Password change successful", "success")

        return redirect("/dashboard")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("We hope to see you again soon!")

    # Redirect user to login form
    return redirect("/")