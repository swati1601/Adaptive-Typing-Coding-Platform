# CodeArena — Adaptive Typing & Coding Platform

A full-stack web platform that helps users improve **typing speed (WPM)** and **programming skills** through adaptive difficulty. The system analyzes performance in real-time and automatically adjusts question difficulty to match the user's skill level.

---

## Features

### Typing Practice
- Real-time **WPM (Words Per Minute)** and **accuracy** calculation
- **Error pattern analysis** — identifies frequently mistyped characters
- Adaptive difficulty — text complexity increases/decreases based on performance
- Live metrics displayed while typing

### Coding Practice
- **LeetCode-style questions** with function signatures, starter code, and test cases
- **Real code execution** — Python code runs against test cases via subprocess sandbox (5s timeout)
- **Run Tests** button — check output before submitting (like LeetCode)
- Per-test-case results showing actual vs expected output, with runtime error display
- Supports **Python**, **C**, and **Java** questions across 3 difficulty tiers
- 33+ questions across easy / medium / hard levels

### Adaptive Difficulty Engine
- Tracks `consecutive_correct` and `consecutive_wrong` counts per user
- **3 correct in a row** → level moves **UP** (easy → medium → hard)
- **3 wrong in a row** → level moves **DOWN** (hard → medium → easy)
- Level changes are logged in `level_history` for progress tracking
- Next question is always picked from the user's current level pool

### Dashboard
- Total questions solved, accuracy %, current level, XP, streak
- Recent submissions history with pass/fail indicators
- Skill breakdown per language and difficulty (e.g. `python_medium`, `java_easy`)
- Level change history timeline

### Leaderboard
- Top 50 users ranked by XP
- Shows level, accuracy %, questions solved

### Profile
- Public user profiles at `/profile/<username>`
- Full stats: XP, accuracy, skill scores, account creation date

### Compare Users
- Side-by-side comparison of any two registered users
- Stats comparison: XP, accuracy, questions solved, skill scores

### Authentication
- Register / Login / Logout with Flask-Login
- Password hashing via Werkzeug (bcrypt)
- Session persistence with "remember me"

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, Flask 3.x |
| Auth | Flask-Login, Werkzeug |
| Database | SQLite 3 |
| Frontend | HTML5, CSS3 (dark theme), Vanilla JavaScript |
| Code Execution | Python `subprocess` with temp files + 5s timeout |
| Deployment | Gunicorn, Docker |

---

## Project Structure

```
Adaptive-Typing-Coding-Platform/
├── backend/
│   ├── data/
│   │   ├── coding_questions.json   # LeetCode-style questions with test cases
│   │   └── typing_questions.json  # Typing practice texts
│   ├── app.py                      # Flask app, all routes & code runner
│   ├── database.py                 # SQLite queries, adaptive logic, helpers
│   ├── database.db                 # SQLite database (auto-created)
│   └── requirements.txt
├── frontend/
│   ├── static/
│   │   ├── script.js               # Legacy typing script
│   │   └── style.css               # Dark theme styles
│   └── templates/
│       ├── base.html               # Base layout + navbar
│       ├── index.html              # Landing page
│       ├── login.html
│       ├── register.html
│       ├── coding.html             # Coding practice (LeetCode UI)
│       ├── typing.html             # Typing practice
│       ├── dashboard.html          # Stats & analytics
│       ├── leaderboard.html
│       ├── profile.html
│       └── compare.html
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

---

## Run on Linux

### Method 1: Manual Setup (Recommended for Development)

**Prerequisites:** Python 3.11+, pip, venv

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Adaptive-Typing-Coding-Platform.git
cd Adaptive-Typing-Coding-Platform

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Run the Flask development server
cd backend
python app.py
```

Open your browser at: **http://localhost:5000**

> The SQLite database (`backend/database.db`) is created automatically on first run.

---

### Method 2: Using Docker (Recommended for Production)

**Prerequisites:** Docker, Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/your-username/Adaptive-Typing-Coding-Platform.git
cd Adaptive-Typing-Coding-Platform

# 2. Build and start the container
docker compose up --build -d
```

Open your browser at: **http://localhost:5000**

To stop the container:
```bash
docker compose down
```

---

### Method 3: One-Liner (Quick Test)

```bash
cd Adaptive-Typing-Coding-Platform
python3 -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
cd backend && python app.py
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `codearena-dev-secret-key-change-in-prod` | Flask session secret |
| `PORT` | `5000` | Server port |
| `FLASK_ENV` | — | Set to `production` for Docker |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | Landing page |
| GET/POST | `/register` | No | Create account |
| GET/POST | `/login` | No | Login |
| GET | `/logout` | Yes | Logout |
| GET | `/coding` | Yes | Coding practice page |
| GET | `/api/next_question?lang=python` | Yes | Get next adaptive question |
| POST | `/api/run_tests` | Yes | Run code against test cases (no submit) |
| POST | `/api/submit_code` | Yes | Submit code, run tests, record result |
| GET | `/dashboard` | Yes | User stats & analytics |
| GET | `/leaderboard` | No | Top 50 users |
| GET | `/profile/<username>` | No | Public user profile |
| GET | `/compare` | No | Compare two users |
