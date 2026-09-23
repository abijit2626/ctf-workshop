"""
TinkerHub CTF - Web Exploitation round (9 challenges).

ch1 : view page source          - flag hidden in raw HTML, invisible when rendered
ch2 : robots.txt / unlinked page - flag on a page not linked anywhere
ch3 : HTML comment              - flag inside <!-- -->
ch4 : inspect element           - flag injected into DOM after load, display:none
ch5 : cookie viewing            - flag stored directly in a cookie value
ch6 : cookie tampering          - role=user -> role=admin unlocks the flag
ch7 : IDOR                      - user_id=104 -> 103 returns someone else's flag
ch8 : SQL injection login       - ' OR '1'='1' -- style bypass
ch9 : reflected XSS             - injected script reads a flag out of a cookie

Flask + in-memory sqlite (used only for ch8), no external services, offline.
"""
import sqlite3
from flask import Flask, render_template, request, g, make_response

app = Flask(__name__)

FLAGS = {
    "ch1": "flag{v13w_s0urc3_ftw}",
    "ch2": "flag{r0b0ts_txt_g1v3s_1t_away}",
    "ch3": "flag{c0mm3nts_ar3nt_s3cr3ts}",
    "ch4": "flag{1nsp3ct_th3_dom}",
    "ch5": "flag{c00k13_j4r_s3cr3ts}",
    "ch6": "flag{r0l3_fl1p_pr1v_3sc}",
    "ch7": "flag{1d0r_us3r_103_pwn3d}",
    "ch8": "flag{sql1_1s_n3v3r_s4f3}",
    "ch9": "flag{xss_st34ls_c00k13s}",
}

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


# Fake "profile" data for the IDOR challenge (ch7).
PROFILES = {
    103: {"username": "admin", "note": "Executive dashboard access.", "secret": FLAGS["ch7"]},
    104: {"username": "guest_dana", "note": "Standard employee account.", "secret": None},
}


@app.route("/")
def index():
    return render_template("index.html")


# --- ch1: view page source -------------------------------------------------

@app.route("/ch1")
def ch1():
    return render_template("ch1.html", flag=FLAGS["ch1"])


# --- ch2: robots.txt / unlinked page ----------------------------------------

@app.route("/robots.txt")
def robots():
    return (
        "User-agent: *\n"
        "Disallow: /internal-9f3a2c\n",
        200,
        {"Content-Type": "text/plain"},
    )


@app.route("/internal-9f3a2c")
def ch2():
    return render_template("ch2.html", flag=FLAGS["ch2"])


# --- ch3: HTML comment ------------------------------------------------------

@app.route("/ch3")
def ch3():
    return render_template("ch3.html", flag=FLAGS["ch3"])


# --- ch4: inspect element (hidden DOM node injected after load) ------------

@app.route("/ch4")
def ch4():
    return render_template("ch4.html")


@app.route("/ch4/api/status")
def ch4_api_status():
    return {"status": "ok", "debug_message": f"debug: {FLAGS['ch4']}"}


# --- ch5: cookie viewing (read-only) ----------------------------------------

@app.route("/ch5")
def ch5():
    resp = make_response(render_template("ch5.html"))
    resp.set_cookie("debug_flag", FLAGS["ch5"])
    return resp


# --- ch6: cookie tampering (role=user -> role=admin) ------------------------

@app.route("/ch6")
def ch6():
    role = request.cookies.get("role", "user")
    resp = make_response(render_template("ch6.html", role=role, flag=FLAGS["ch6"] if role == "admin" else None))
    if "role" not in request.cookies:
        resp.set_cookie("role", "user")
    return resp


# --- ch7: IDOR ---------------------------------------------------------------

@app.route("/ch7/profile")
def ch7():
    user_id = request.args.get("user_id", "104")
    try:
        user_id = int(user_id)
    except ValueError:
        user_id = 104
    profile = PROFILES.get(user_id)
    return render_template("ch7.html", user_id=user_id, profile=profile)


# --- ch8: SQL injection login bypass -----------------------------------------

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
            success_flag = FLAGS["ch8"]
        else:
            error = "Invalid username or password."
    return render_template("login.html", error=error, flag=success_flag)


# --- ch9: reflected XSS -------------------------------------------------------

@app.route("/ch9/search")
def ch9():
    q = request.args.get("q", "")
    resp = make_response(render_template("ch9.html", q=q))
    resp.set_cookie("search_flag", FLAGS["ch9"])
    return resp


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
