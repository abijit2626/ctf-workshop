"""
TinkerHub CTF - Web Exploitation demo (2 challenges).

ch1  : view page source            -> flag hidden in raw HTML, invisible when rendered
login: SQL injection login bypass  -> ' OR '1'='1' -- style bypass

Flask + in-memory sqlite, no external services, fully offline.
"""
import sqlite3
from flask import Flask, render_template, request, g

app = Flask(__name__)

FLAG_CH1 = "flag{v13w_s0urc3_ftw}"
FLAG_SQLI = "flag{sql1_1s_n3v3r_s4f3}"

DB_PATH = "file:tinkerdb?mode=memory&cache=shared"
_keepalive = sqlite3.connect(DB_PATH, uri=True)  # keeps the in-memory db alive for app lifetime


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, uri=True)
    return g.db


def init_db():
    conn = sqlite3.connect(DB_PATH, uri=True)
    conn.execute("DROP TABLE IF EXISTS users")
    conn.execute("CREATE TABLE users (username TEXT, password TEXT)")
    conn.execute("INSERT INTO users VALUES ('admin', 's3cr3t-only-admin-knows')")
    conn.commit()
    conn.close()


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ch1")
def ch1():
    return render_template("ch1.html", flag=FLAG_CH1)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    success_flag = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        # Deliberately vulnerable: raw string concatenation into SQL query.
        query = (
            f"SELECT username FROM users WHERE username='{username}' "
            f"AND password='{password}'"
        )
        db = get_db()
        try:
            row = db.execute(query).fetchone()
        except sqlite3.OperationalError as e:
            error = f"Database error: {e}"
            row = None
        if row:
            success_flag = FLAG_SQLI
        else:
            error = "Invalid username or password."
    return render_template("login.html", error=error, flag=success_flag)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
