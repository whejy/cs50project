import os

from os.path import basename
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_file, after_this_request
from flask_session import Session
from tempfile import mkdtemp
from zipfile import ZipFile
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, downloadEntries

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

# Global variable for temporary download files
save_path = "static/temp/"

# Background image options
PAPER = [
    "Classic",
    "Crumpled",
    "Old",
    "Stained",
    "Wall",
    "Wood"
]

# Font options
FONTS = [
    "Arial, sans-serif",
    "Brush Script MT, cursive",
    "Courier New, monospace",
    "Georgia, serif",
    "Lucida Handwriting, cursive",
    "Times New Roman"
]

# Character limits for preview in Dashboard view
ENTRYLIMIT = 79
TITLELIMIT = 9

@app.route("/")
def index():

    # Remove all unassigned entries (accounts for premature exit where entry was added but no login)
    db.execute("""
    DELETE FROM entries
    WHERE user_id is null
    """)

    # Remove any previous downloaded entries stored on server
    for f in os.listdir(save_path):
        path = os.path.join(save_path, f)
        os.remove(path)

    # Query DB for user's background image and font preference
    if session.get("user_id"):
        style = db.execute("""
        SELECT background, font
        FROM users
        WHERE id = ?
        """, session["user_id"])

        image = (style[0]['background'])
        font = (style[0]['font'])

        # If no image or font (new user) set to default
        if image is None:
            image = "url('/static/Classic.jpg')"

        if font is None:
            font = "Lucida Handwriting, cursive"

        return render_template("home.html",
                                image=image,
                                paper=PAPER,
                                font=font,
                                fonts=FONTS
                                )

    return render_template("home.html",
                            paper=PAPER,
                            fonts=FONTS
                            )


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")


@app.route("/download", methods=["GET"])
@login_required
def download():

    """ Download all entries """

    entry = db.execute("""
    SELECT entry, title, time
    FROM entries
    WHERE user_id = ?
    ORDER BY time
    """, session["user_id"])

    downloadEntries(entry)


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():

    # Get style attributes the user has chosen before submitting their entry
    style = db.execute("""
    SELECT background, font
    FROM entries
    WHERE user_id is null
    """)

    if style:
        pad = style[0]['background']
        font = style[0]['font']

        if pad:
            db.execute("""
            UPDATE users
            SET background = ?
            WHERE id = ?
            """, pad, session["user_id"])

        if font:
            db.execute("""
            UPDATE users
            SET font = ?
            WHERE id = ?
            """, font, session["user_id"])

    # Add most recent unassigned entry to current user
    db.execute("""
    UPDATE entries
    SET user_id = ?
    WHERE user_id is null
    """, session["user_id"])

    # Remove any previous downloaded entries stored on server
    for f in os.listdir(save_path):
        path = os.path.join(save_path, f)
        os.remove(path)

    title = db.execute("""
    SELECT title
    FROM entries
    WHERE user_id = ?
    """, session["user_id"])

    journal = db.execute("""
    SELECT *
    FROM entries
    WHERE user_id = ?
    ORDER BY time DESC
    """, session["user_id"])

    # Prepare to send relevant data to dashboard page
    entries = []
    for row in journal:
        entries.append({
            "entry": row['entry'][0:ENTRYLIMIT + 1],
            "title": row['title'][0:TITLELIMIT + 1],
            "time": row['time'],
            "id": row['id']
        })

    # Add ellipsis to shortened entries if there is at least 1 entry
    if entries:
        for row in entries:
            if len(row['entry']) > ENTRYLIMIT:
                row['entry'] += "..."
            if len(row['title']) > TITLELIMIT:
                row['title'] += "..."

    return render_template("dashboard.html",
                            entries=entries
                            )


@app.route("/view", methods=["GET", "POST"])
@login_required
def view():

    """ Allow user to update, delete or download entries from dashboard"""

    viewid = request.form.get("view")
    checked = request.form.getlist("delete")
    download = request.form.get("download")

    # User requesting to download all files via "delete account" button
    if request.method == "GET":
        entry = db.execute("""
                SELECT entry, title, time
                FROM entries
                WHERE user_id = ?
                ORDER BY time
                """, session["user_id"])

        if entry:
            downloadEntries(entry)
            return send_file('MyEntries.zip',
                            mimetype="application/zip",
                            as_attachment=True,
                            cache_timeout=0
                            )
        else:
            flash("No entries to download.", "error")
            return redirect("/dashboard")

    # User requesting to download or delete checked files via dashboard
    if not viewid:
        if checked:
            if not download:
                for i in checked:
                    db.execute("""
                    DELETE FROM entries
                    WHERE id = ?
                    """, i)
                if len(checked) < 2:
                    flash("Entry deleted.", "success")
                else:
                    flash(f"{len(checked)} entries deleted.", "success")
                return redirect("/dashboard")

            # User has requested to download checked files
            else:
                entry = []
                for i in checked:
                    prep = db.execute("""
                    SELECT entry, title, time
                    FROM entries
                    WHERE user_id = ?
                    AND id in (?)
                    ORDER BY time
                    """, session["user_id"], i)

                    entry = entry + prep

                if entry:
                    downloadEntries(entry)
                    return send_file('MyEntries.zip',
                                    mimetype="application/zip",
                                    as_attachment=True,
                                    cache_timeout=0
                                    )

    # User clicked "view"
    else:
        entry = db.execute("""
        SELECT entry, title
        FROM entries
        WHERE id = ?
        """, viewid)

        # Query DB for user's font and background image preference
        background = db.execute("""
        SELECT background, font
        FROM users
        WHERE id = ?
        """, session["user_id"])

        image = (background[0]['background'])
        font = (background[0]['font'])

        if image is None:
            image = "url('/static/Classic.jpg')"

        if font is None:
            font = "Lucida Handwriting, cursive"

        return render_template("edit.html",
                                entry=entry,
                                viewid=viewid,
                                image=image,
                                paper=PAPER,
                                font=font,
                                fonts=FONTS
                                )


@app.route("/entry", methods=["POST"])
def entry():

    ## Clear download folder
    for f in os.listdir(save_path):
        path = os.path.join(save_path, f)
        os.remove(path)

    jentry = request.form.get("entry")
    title = request.form.get("title")
    font = request.form.get("fontSelector")
    pad = request.form.get("padSelector")

    if font:
        if font not in FONTS:
            return redirect("/")

    if pad:
        el = pad.split("/")[2]
        paper = el.split(".")[0]
        if paper not in PAPER:
            return redirect("/")

    if not jentry:
        flash("Entry cannot be blank.", "error")
        return redirect("/")

    db.execute("""
    INSERT INTO entries (entry, background, font)
    VALUES (?, ?, ?)
    """, jentry, pad, font)

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

    # If logged in add entry. Redirect to Dashboard where entry is assigned to user.
    else:
        flash("Entry added!", "success")
        return redirect("/dashboard")


@app.route("/edit", methods=["POST"])
def edit():

    """ Allow user to update or delete current entry """

    delid = request.form.get("delete")
    updateid = request.form.get("update")

    if delid:
        db.execute("""
        DELETE
        FROM entries
        WHERE id = ?
        """, delid)

        flash("Entry deleted.")

    elif updateid:
        entry = request.form.get("entry")
        title = request.form.get("title")
        font = request.form.get("fontSelector")
        pad = request.form.get("padSelector")

        db.execute("""
        UPDATE entries
        SET entry = ?, title = ?, time = CURRENT_TIMESTAMP
        WHERE id = ?
        """, entry, title, updateid)

        if pad:
            el = pad.split("/")[2]
            paper = el.split(".")[0]
            if paper not in PAPER:
                return redirect("/dashboard")

            db.execute("""
            UPDATE users
            SET background = ?
            WHERE id = ?
            """, pad, session["user_id"])

        if font:
            if font not in FONTS:
                return redirect("/dashboard")

            db.execute("""
            UPDATE users
            SET font = ?
            WHERE id = ?
            """, font, session["user_id"])

        flash("Entry updated!", "success")

    return redirect("/dashboard")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        pword = request.form.get("password")
        error = False
        message = ""

        # Ensure username was submitted
        if not username:
            message = "Must provide username."
            error = True

        # Ensure password was submitted
        elif not pword:
            message = "Must provide password."
            error = True

        if error:
            flash(f"{message}", "error")
            return render_template("login.html")

        # Ensure username exists and password is correct
        rows = db.execute("""
        SELECT *
        FROM users
        WHERE username = ?
        """, username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], pword):
            flash("Invalid username and/or password.", "error")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash(f"Welcome back, {username}!")

        # Redirect user to home page
        return redirect("/dashboard")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    """Register user"""

    username = request.form.get("username")
    pword = request.form.get("password")
    confirmation = request.form.get("confirmation")
    error = False
    message = ""

    # Ensure username is unique
    rows = db.execute("""
    SELECT *
    FROM users
    WHERE username = ?
    """, username)
    if len(rows) != 0:
        message = "That username is already taken."
        error = True

    # Ensure username was submitted
    elif not username:
        message = "Must provide username."
        error = True

    # Ensure password was submitted
    elif not pword:
        message = "Must provide password."
        error = True

    # Ensure password was entered twice for confirmation
    elif not confirmation:
        message = "Please confirm password."
        error = True

    # Ensure password inputs match each other
    elif not pword == confirmation:
        message = "Passwords do not match."
        error = True

    elif len(username) < 3:
        message = "Username must be at least 3 characters long."
        error = True

    elif not username.isalnum():
        message = "Username may only contain letters and numbers."
        error = True

    elif len(pword) < 8:
        message = "Password must be at least 8 characters long."
        error = True

    if error:
        flash(f"{message}", "error")
        return render_template("login.html")

    # If all prerequisites are successful, update database
    db.execute("""
    INSERT INTO users (username, hash)
    VALUES (?, ?)
    """, username, generate_password_hash(pword))

    # Prepare for auto-login (get username that was just inserted into database and set this id to the session id)
    rows = db.execute("""
    SELECT *
    FROM users
    WHERE username = ?
    """, username)

    # Remember which user is logged in
    session["user_id"] = rows[0]["id"]

    flash(f"Welcome, {username}!", "success")

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
        SELECT *
        FROM users
        WHERE id = ?
        """, session["user_id"])

        currentPword = request.form.get("currentpassword")
        newPword = request.form.get("newpassword")
        confirmation = request.form.get("confirmation")
        error = False
        message = ""

        # Ensure password was submitted
        if not currentPword:
            message = "Must provide password."
            error = True

        # Ensure new password was entered twice for confirmation
        elif not newPword or not confirmation:
            message = "Please confirm password."
            error = True

        # Ensure current password is correct
        elif not check_password_hash(rows[0]["hash"], currentPword):
            message = "Password incorrect."
            error = True

        # Ensure new password inputs match each other
        elif not newPword == confirmation:
            message = "Passwords do not match."
            error = True

        # Ensure new password is different from current password
        elif check_password_hash(rows[0]["hash"], newPword):
            message = "New password must be different from current password."
            error = True

        elif len(newPword) < 8:
            message = "Password must be at least 8 characters long."
            error = True

        if error:
            flash(f"{message}", "error")
            return render_template("password.html")

        # Update password
        db.execute("""
        UPDATE users
        SET hash = ?
        WHERE id = ?
        """, generate_password_hash(newPword), session["user_id"])

        flash("Password change successful.", "success")

        return redirect("/dashboard")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():

    """ Delete user's account and all user's entries """

    if request.method == "GET":
        return render_template("delete.html")
    else:

        # Clear temp files
        for f in os.listdir(save_path):
            path = os.path.join(save_path, f)
            os.remove(path)

        db.execute("""
        DELETE FROM entries
        WHERE user_id = ?
        """, session["user_id"])

        db.execute("""
        DELETE FROM users
        WHERE id = ?
        """, session["user_id"])

        session.clear()

        flash("Account deleted.")
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Clear temp folder
    for f in os.listdir(save_path):
        path = os.path.join(save_path, f)
        os.remove(path)

    # Forget any user_id
    session.clear()

    flash("See you next time!")

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
        flash("{}, {}".format(e.name, e.code), "error")
    return redirect("/")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)