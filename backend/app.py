import os
import sys
import json
import random
import subprocess
import tempfile
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Add backend to path so we can import database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database as db

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, "templates")
STATIC_DIR   = os.path.join(FRONTEND_DIR, "static")
DATA_DIR     = os.path.join(BASE_DIR, "data")

# ── Load .env from project root ──────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    env_path = os.path.join(PROJECT_ROOT, ".env")
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed, rely on system env vars

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.secret_key = os.environ.get("SECRET_KEY", "codearena-dev-secret-key-change-in-prod")

# ── Login Manager ─────────────────────────────────────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

# ── Load Questions ────────────────────────────────────────────────────────────
QUESTIONS_PATH = os.path.join(DATA_DIR, "coding_questions.json")
with open(QUESTIONS_PATH) as f:
    CODING_QUESTIONS = json.load(f)

LEVELS = ["easy", "medium", "hard"]

# Track which questions have been served per user (in-memory)
_user_used_questions: dict = {}


# ── User Model for Flask-Login ────────────────────────────────────────────────
class User(UserMixin):
    def __init__(self, user_row):
        row = dict(user_row)
        self.id            = row["id"]
        self.username    = row["username"]
        self.email       = row["email"]
        self.password_hash = row["password_hash"]
        self.created_at  = row["created_at"]


@login_manager.user_loader
def load_user(user_id):
    row = db.get_user_by_id(int(user_id))
    if row is None:
        return None
    return User(row)


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_used_questions(user_id: int, lang: str, level: str) -> set:
    key = f"{user_id}:{lang}:{level}"
    return _user_used_questions.setdefault(key, set())


def pick_question(user_id: int, lang: str, level: str):
    pool = CODING_QUESTIONS.get(lang, {}).get(level, [])
    used = get_used_questions(user_id, lang, level)
    available = [q for q in pool if q["question"] not in used]
    if not available:
        used.clear()
        available = pool
    q = random.choice(available)
    used.add(q["question"])
    return q


# ── Code Execution Runner ─────────────────────────────────────────────────────

def run_python_code(user_code: str, test_cases: list, timeout: int = 5) -> dict:
    """
    Execute user_code against test_cases using a subprocess.
    Returns dict with 'results' (list per test case) and 'passed_count'.
    """
    # Build the runner script: user code + test harness
    tc_json = json.dumps(test_cases)
    runner_script = user_code + "\n\n" + """
import json, sys

_test_cases = json.loads('''""" + tc_json + """''')
_out = []
for _tc in _test_cases:
    try:
        _result = eval(_tc["input"])
        _actual = repr(_result)
        _expected = _tc["expected"]
        _pass = _actual.strip() == _expected.strip()
        _out.append({"passed": _pass, "actual": _actual, "expected": _expected, "error": None})
    except Exception as _e:
        _out.append({"passed": False, "actual": None, "expected": _tc["expected"],
                     "error": str(_e)})
print("__RESULTS__" + json.dumps(_out))
"""

    try:
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False, dir='/tmp'
        ) as f:
            f.write(runner_script)
            tmp_path = f.name

        proc = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=timeout
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        if "__RESULTS__" not in stdout:
            return {
                "error": stderr.strip().split('\n')[-1] if stderr else "No output from runner.",
                "results": [{"passed": False, "actual": None, "expected": tc["expected"],
                             "error": stderr.strip().split('\n')[-1][:200]}
                            for tc in test_cases],
                "passed_count": 0,
            }

        results = json.loads(stdout.split("__RESULTS__")[1].strip())
        passed_count = sum(1 for r in results if r["passed"])
        return {"results": results, "passed_count": passed_count, "error": None}

    except subprocess.TimeoutExpired:
        return {
            "error": f"Time limit exceeded ({timeout}s).",
            "results": [{"passed": False, "actual": None, "expected": tc["expected"],
                         "error": "Time limit exceeded"}
                        for tc in test_cases],
            "passed_count": 0,
        }
    except Exception as e:
        return {
            "error": str(e),
            "results": [{"passed": False, "actual": None, "expected": tc["expected"],
                         "error": str(e)}
                        for tc in test_cases],
            "passed_count": 0,
        }
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Auth ───────────────────────────────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm  = request.form.get("confirm_password", "")

    if not username or not email or not password:
        return render_template("register.html", error="All fields are required.")
    if password != confirm:
        return render_template("register.html", error="Passwords do not match.")
    if len(password) < 6:
        return render_template("register.html", error="Password must be at least 6 characters.")
    if len(username) < 3:
        return render_template("register.html", error="Username must be at least 3 characters.")
    if db.get_user_by_username(username):
        return render_template("register.html", error="Username already taken.")
    if db.get_user_by_email(email):
        return render_template("register.html", error="Email already registered.")

    pw_hash  = generate_password_hash(password)
    user_id  = db.create_user(username, email, pw_hash)
    if not user_id:
        return render_template("register.html", error="Could not create account.")

    user_row = db.get_user_by_id(user_id)
    user_obj = User(user_row)
    login_user(user_obj, remember=True)
    flash("Account created! Welcome to CodeArena.", "success")
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user_row = db.get_user_by_username(username)
    if not user_row or not check_password_hash(user_row["password_hash"], password):
        return render_template("login.html", error="Invalid username or password.")

    user_obj = User(user_row)
    login_user(user_obj, remember=True)
    flash(f"Welcome back, {username}!", "success")
    return redirect(url_for("dashboard"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


# ── Coding / Adaptive Engine ───────────────────────────────────────────────────

@app.route("/coding")
@login_required
def coding():
    return render_template("coding.html")


@app.route("/api/next_question")
@login_required
def next_question():
    lang = request.args.get("lang", "python")
    progress = db.get_progress(current_user.id)
    level    = progress["current_level"]

    q = pick_question(current_user.id, lang, level)

    # Build display-friendly test cases (without revealing expected for "run" mode)
    display_tests = [
        {"input": tc["input"], "expected": tc["expected"]}
        for tc in q.get("test_cases", [])
    ]

    return jsonify({
        "question":          q["question"],
        "description":       q.get("description", ""),
        "answer":            q.get("answer", ""),
        "starter_code":      q.get("starter_code", ""),
        "function_signature": q.get("function_signature", ""),
        "test_cases":        display_tests,
        "hint":              q.get("hint", ""),
        "difficulty":        q["difficulty"],
        "current_level":     level,
        "xp":                progress["xp"],
        "streak":            progress["streak"],
    })


@app.route("/api/run_tests", methods=["POST"])
@login_required
def run_tests():
    """Run user code against test cases without recording submission."""
    data       = request.get_json()
    user_code  = data.get("code", "").strip()
    language   = data.get("language", "python")
    test_cases = data.get("test_cases", [])

    if not user_code:
        return jsonify({"error": "No code provided.", "results": []}), 400

    if language == "python" and test_cases:
        result = run_python_code(user_code, test_cases)
        return jsonify(result)
    else:
        return jsonify({"error": "Code execution not supported for this language yet.", "results": []})


@app.route("/api/submit_code", methods=["POST"])
@login_required
def submit_code():
    data       = request.get_json()
    user_code  = data.get("code", "").strip()
    answer     = data.get("answer", "").strip()
    question   = data.get("question", "")
    language   = data.get("language", "python")
    difficulty = data.get("difficulty", "easy")
    time_taken = float(data.get("time_taken", 0))
    test_cases = data.get("test_cases", [])

    # ── Execute code and determine correctness ──────────────────────────────
    test_results = []
    runtime_error = None

    if language == "python" and test_cases:
        run = run_python_code(user_code, test_cases)
        test_results = run.get("results", [])
        runtime_error = run.get("error")
        total_tests = len(test_cases)
        passed_tests = run.get("passed_count", 0)
        correct = (passed_tests == total_tests) and total_tests > 0
    else:
        # Fallback: exact string match for C/Java (no execution engine yet)
        correct = user_code == answer
        passed_tests = 1 if correct else 0
        total_tests = 1

    # ── XP calculation ────────────────────────────────────────────────────────
    if correct:
        xp_earned = 10
        if time_taken < 30:
            xp_earned += 5   # speed bonus
        if total_tests > 3:
            xp_earned += 3   # bonus for multi-test questions
    else:
        xp_earned = 2        # attempt credit

    # ── Record submission ─────────────────────────────────────────────────────
    db.add_submission(
        current_user.id, question, user_code,
        1 if correct else 0, language, time_taken, difficulty
    )

    # ── Update skills ─────────────────────────────────────────────────────────
    db.update_skill(current_user.id, language, difficulty, correct)

    # ── Update progress & adaptive level ──────────────────────────────────────
    new_level = db.update_progress(current_user.id, correct, xp_earned)
    progress  = db.get_progress(current_user.id)

    return jsonify({
        "result":        "Correct" if correct else "Wrong",
        "xp_earned":     xp_earned,
        "new_xp":        progress["xp"],
        "new_level":     new_level or progress["current_level"],
        "streak":        progress["streak"],
        "test_results":  test_results,
        "passed_tests":  passed_tests,
        "total_tests":   total_tests,
        "runtime_error": runtime_error,
    })


# ── Dashboard ──────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
def dashboard():
    progress      = db.get_progress(current_user.id)
    recent        = db.get_recent_submissions(current_user.id, limit=10)
    skills        = db.get_skills(current_user.id)
    level_history = db.get_level_history(current_user.id)

    total    = progress["correct_count"] + progress["wrong_count"]
    accuracy = round(progress["correct_count"] / total * 100, 1) if total > 0 else 0.0

    return render_template(
        "dashboard.html",
        user=current_user,
        progress=progress,
        recent=recent,
        skills=skills,
        level_history=level_history,
        accuracy=accuracy,
    )


# ── Profile ────────────────────────────────────────────────────────────────────

@app.route("/profile/<username>")
def profile(username):
    stats = db.get_user_full_stats(username)
    if not stats:
        flash("User not found.", "error")
        return redirect(url_for("index"))
    return render_template("profile.html", stats=stats)


# ── Compare ────────────────────────────────────────────────────────────────────

@app.route("/compare")
def compare():
    users = db.get_all_users()
    u1    = request.args.get("user1", "")
    u2    = request.args.get("user2", "")

    stats1 = db.get_user_full_stats(u1) if u1 else None
    stats2 = db.get_user_full_stats(u2) if u2 else None

    return render_template(
        "compare.html",
        users=users,
        stats1=stats1,
        stats2=stats2,
        selected_user1=u1,
        selected_user2=u2,
    )


# ── Leaderboard ────────────────────────────────────────────────────────────────

@app.route("/leaderboard")
def leaderboard():
    board = db.get_leaderboard(limit=50)
    return render_template("leaderboard.html", leaderboard=board)


# ── Initialize DB on import (safe to call multiple times) ─────────────────────
db.init_db()

# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
