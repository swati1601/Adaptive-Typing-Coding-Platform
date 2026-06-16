import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            current_level TEXT DEFAULT 'easy',
            xp INTEGER DEFAULT 0,
            questions_solved INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            wrong_count INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            consecutive_correct INTEGER DEFAULT 0,
            consecutive_wrong INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS user_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            user_code TEXT,
            correct INTEGER NOT NULL,
            language TEXT DEFAULT 'python',
            time_taken_sec REAL DEFAULT 0,
            difficulty TEXT DEFAULT 'easy',
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS user_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            score INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, skill_name)
        );

        CREATE TABLE IF NOT EXISTS level_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            old_level TEXT NOT NULL,
            new_level TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)

    conn.commit()
    conn.close()


# --- User helpers ---

def create_user(username, email, password_hash):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO user_progress (user_id) VALUES (?)",
            (user_id,)
        )
        conn.commit()
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user


# --- Progress helpers ---

def get_progress(user_id):
    conn = get_db()
    progress = conn.execute(
        "SELECT * FROM user_progress WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return dict(progress) if progress else None


def update_progress(user_id, correct, xp_earned):
    conn = get_db()
    progress = conn.execute(
        "SELECT * FROM user_progress WHERE user_id = ?", (user_id,)
    ).fetchone()

    if not progress:
        conn.close()
        return None

    new_xp = progress['xp'] + xp_earned
    new_solved = progress['questions_solved'] + 1
    new_streak = progress['streak'] + 1 if correct else 0

    if correct:
        new_correct = progress['correct_count'] + 1
        new_wrong = progress['wrong_count']
        new_consec_correct = progress['consecutive_correct'] + 1
        new_consec_wrong = 0
    else:
        new_correct = progress['correct_count']
        new_wrong = progress['wrong_count'] + 1
        new_consec_correct = 0
        new_consec_wrong = progress['consecutive_wrong'] + 1

    # Determine new level
    old_level = progress['current_level']
    new_level = old_level
    levels = ['easy', 'medium', 'hard']
    level_idx = levels.index(old_level)

    if new_consec_correct >= 3 and level_idx < 2:
        level_idx += 1
        new_level = levels[level_idx]
        new_consec_correct = 0
    elif new_consec_wrong >= 3 and level_idx > 0:
        level_idx -= 1
        new_level = levels[level_idx]
        new_consec_wrong = 0

    conn.execute("""
        UPDATE user_progress SET
            current_level=?, xp=?, questions_solved=?,
            correct_count=?, wrong_count=?, streak=?,
            consecutive_correct=?, consecutive_wrong=?
        WHERE user_id=?
    """, (
        new_level, new_xp, new_solved,
        new_correct, new_wrong, new_streak,
        new_consec_correct, new_consec_wrong, user_id
    ))

    if new_level != old_level:
        conn.execute(
            "INSERT INTO level_history (user_id, old_level, new_level) VALUES (?, ?, ?)",
            (user_id, old_level, new_level)
        )

    conn.commit()
    conn.close()
    return new_level


# --- Submission helpers ---

def add_submission(user_id, question_text, user_code, correct, language, time_taken, difficulty):
    conn = get_db()
    conn.execute("""
        INSERT INTO user_submissions
        (user_id, question_text, user_code, correct, language, time_taken_sec, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, question_text, user_code, 1 if correct else 0, language, time_taken, difficulty))
    conn.commit()
    conn.close()


def get_recent_submissions(user_id, limit=10):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM user_submissions
        WHERE user_id = ?
        ORDER BY submitted_at DESC
        LIMIT ?
    """, (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_submissions(user_id):
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM user_submissions
        WHERE user_id = ?
        ORDER BY submitted_at ASC
    """, (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Skill helpers ---

def update_skill(user_id, language, difficulty, correct):
    skill_name = f"{language}_{difficulty}"
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM user_skills WHERE user_id = ? AND skill_name = ?",
        (user_id, skill_name)
    ).fetchone()

    if existing:
        new_score = existing['score'] + (10 if correct else 2)
        conn.execute(
            "UPDATE user_skills SET score = ? WHERE user_id = ? AND skill_name = ?",
            (new_score, user_id, skill_name)
        )
    else:
        score = 10 if correct else 2
        conn.execute(
            "INSERT INTO user_skills (user_id, skill_name, score) VALUES (?, ?, ?)",
            (user_id, skill_name, score)
        )
    conn.commit()
    conn.close()


def get_skills(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM user_skills WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Leaderboard ---

def get_leaderboard(limit=50):
    conn = get_db()
    rows = conn.execute("""
        SELECT u.username, p.current_level, p.xp, p.questions_solved,
               p.correct_count, p.wrong_count,
               CASE WHEN (p.correct_count + p.wrong_count) > 0
                    THEN ROUND(CAST(p.correct_count AS FLOAT) / (p.correct_count + p.wrong_count) * 100, 1)
                    ELSE 0
               END AS accuracy
        FROM users u
        JOIN user_progress p ON u.id = p.user_id
        ORDER BY p.xp DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- Level history ---

def get_level_history(user_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM level_history WHERE user_id = ? ORDER BY changed_at ASC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# --- All users (for comparison) ---

def get_all_users():
    conn = get_db()
    rows = conn.execute("SELECT id, username FROM users ORDER BY username").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_user_full_stats(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user:
        conn.close()
        return None

    progress = conn.execute(
        "SELECT * FROM user_progress WHERE user_id = ?", (user['id'],)
    ).fetchone()

    skills = conn.execute(
        "SELECT * FROM user_skills WHERE user_id = ?", (user['id'],)
    ).fetchall()

    conn.close()

    stats = dict(progress) if progress else {}
    stats['username'] = user['username']
    stats['created_at'] = user['created_at']
    stats['skills'] = [dict(s) for s in skills]

    total = stats.get('correct_count', 0) + stats.get('wrong_count', 0)
    stats['accuracy'] = round(stats['correct_count'] / total * 100, 1) if total > 0 else 0

    return stats
