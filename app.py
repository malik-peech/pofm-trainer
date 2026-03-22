import json
import random
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from generator import generate_exercise, generate_exam as gen_exam

app = Flask(__name__)
EXERCISES_PATH = os.path.join(os.path.dirname(__file__), "exercises.json")

DATABASE_URL = os.environ.get("DATABASE_URL")

USERS = {
    "alia": {"name": "Alia", "level": "college", "class": "4eme"},
    "imran": {"name": "Imran", "level": "lycee", "class": "1ere"},
}

# ── Database abstraction (PostgreSQL or SQLite fallback) ────

if DATABASE_URL:
    import psycopg2
    import psycopg2.extras

    def get_db():
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        return conn

    def db_execute(conn, query, params=None):
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params or ())
        return cur

    def db_fetchone(conn, query, params=None):
        cur = db_execute(conn, query, params)
        return cur.fetchone()

    def db_fetchall(conn, query, params=None):
        cur = db_execute(conn, query, params)
        return cur.fetchall()

    PH = "%s"  # PostgreSQL placeholder

else:
    import sqlite3

    DB_PATH = os.path.join(os.path.dirname(__file__), "pofm.db")

    def get_db():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def db_execute(conn, query, params=None):
        return conn.execute(query, params or ())

    def db_fetchone(conn, query, params=None):
        return conn.execute(query, params or ()).fetchone()

    def db_fetchall(conn, query, params=None):
        return conn.execute(query, params or ()).fetchall()

    PH = "?"  # SQLite placeholder


def _sql(query):
    """Convert ? placeholders to %s for PostgreSQL."""
    if DATABASE_URL:
        return query.replace("?", "%s")
    return query


def init_db():
    conn = get_db()
    cur = conn.cursor()

    if DATABASE_URL:
        # PostgreSQL schema
        cur.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'alia',
                exercise_id INTEGER NOT NULL,
                theme TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                user_answer INTEGER,
                correct_answer INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                is_retry BOOLEAN NOT NULL DEFAULT FALSE,
                points REAL NOT NULL DEFAULT 0,
                mode TEXT NOT NULL,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'alia',
                started_at TIMESTAMP DEFAULT NOW(),
                finished_at TIMESTAMP,
                score INTEGER DEFAULT 0,
                total INTEGER DEFAULT 25
            );
            CREATE TABLE IF NOT EXISTS exercise_store (
                id INTEGER PRIMARY KEY,
                theme TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                statement TEXT NOT NULL,
                answer INTEGER NOT NULL,
                explanation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            CREATE TABLE IF NOT EXISTS bookmarks (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'alia',
                statement TEXT NOT NULL,
                theme TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                correct_answer INTEGER NOT NULL,
                explanation TEXT NOT NULL,
                user_answer INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                reviewed BOOLEAN DEFAULT FALSE
            );
        """)
    else:
        # SQLite schema
        try:
            row = conn.execute("PRAGMA table_info(results)").fetchall()
            cols = [r[1] for r in row]
            if 'user_id' not in cols or 'points' not in cols:
                cur.executescript("DROP TABLE IF EXISTS results; DROP TABLE IF EXISTS exam_sessions; DROP TABLE IF EXISTS bookmarks; DROP TABLE IF EXISTS exercise_store;")
        except Exception:
            pass
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'alia',
                exercise_id INTEGER NOT NULL,
                theme TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                user_answer INTEGER,
                correct_answer INTEGER NOT NULL,
                is_correct BOOLEAN NOT NULL,
                is_retry BOOLEAN NOT NULL DEFAULT 0,
                points REAL NOT NULL DEFAULT 0,
                mode TEXT NOT NULL,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS exam_sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'alia',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                finished_at TIMESTAMP,
                score INTEGER DEFAULT 0,
                total INTEGER DEFAULT 25
            );
            CREATE TABLE IF NOT EXISTS exercise_store (
                id INTEGER PRIMARY KEY,
                theme TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                statement TEXT NOT NULL,
                answer INTEGER NOT NULL,
                explanation TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS bookmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'alia',
                statement TEXT NOT NULL,
                theme TEXT NOT NULL,
                difficulty INTEGER NOT NULL,
                correct_answer INTEGER NOT NULL,
                explanation TEXT NOT NULL,
                user_answer INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reviewed BOOLEAN DEFAULT 0
            );
        """)

    conn.commit()
    conn.close()


def load_exercises():
    with open(EXERCISES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


init_db()


# ── Helper to access row values (dict for PG, sqlite3.Row for SQLite) ──

def row_get(row, key):
    if row is None:
        return None
    if isinstance(row, dict):
        return row.get(key)
    return row[key]


# ── Routes ──────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/users")
def get_users():
    return jsonify(USERS)


@app.route("/api/exercise/random")
def random_exercise():
    theme = request.args.get("theme")
    difficulty = request.args.get("difficulty", type=int)

    ex = generate_exercise(theme=theme, difficulty=difficulty)
    if not ex:
        return jsonify({"error": "Aucun exercice trouve"}), 404

    return jsonify({
        "id": ex["id"],
        "theme": ex["theme"],
        "difficulty": ex["difficulty"],
        "statement": ex["statement"],
        "answer": ex["answer"],
        "explanation": ex["explanation"]
    })


@app.route("/api/exam/generate")
def generate_exam_route():
    session_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(100, 999))
    user_id = request.args.get("user", "alia")
    exercises = gen_exam(25)

    conn = get_db()
    db_execute(conn, _sql(
        "INSERT INTO exam_sessions (id, user_id, total) VALUES (?, ?, ?)"
    ), (session_id, user_id, len(exercises)))
    conn.commit()
    conn.close()

    return jsonify({
        "session_id": session_id,
        "exercises": [
            {"num": i, "id": ex["id"], "theme": ex["theme"],
             "difficulty": ex["difficulty"], "statement": ex["statement"],
             "answer": ex["answer"], "explanation": ex["explanation"]}
            for i, ex in enumerate(exercises, 1)
        ],
        "total": len(exercises)
    })


@app.route("/api/submit", methods=["POST"])
def submit_answer():
    data = request.json
    user_answer = data.get("answer")
    correct_answer = data.get("correct_answer")
    mode = data.get("mode", "individual")
    session_id = data.get("session_id")
    user_id = data.get("user", "alia")
    theme = data.get("theme", "")
    difficulty = data.get("difficulty", 1)
    is_retry = data.get("is_retry", False)

    is_correct = user_answer == correct_answer
    points = 0
    if is_correct:
        points = difficulty * (0.25 if is_retry else 1)

    conn = get_db()
    db_execute(conn, _sql(
        """INSERT INTO results
           (user_id, exercise_id, theme, difficulty, user_answer, correct_answer, is_correct, is_retry, points, mode, session_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    ), (user_id, data.get("exercise_id", 0), theme, difficulty,
        user_answer, correct_answer, is_correct, is_retry, points, mode, session_id))

    if session_id and is_correct:
        db_execute(conn, _sql(
            "UPDATE exam_sessions SET score = score + 1 WHERE id = ?"
        ), (session_id,))

    conn.commit()
    conn.close()

    return jsonify({"correct": is_correct, "points": points})


@app.route("/api/exam/finish", methods=["POST"])
def finish_exam():
    data = request.json
    session_id = data.get("session_id")

    conn = get_db()
    if DATABASE_URL:
        db_execute(conn, "UPDATE exam_sessions SET finished_at = NOW() WHERE id = %s", (session_id,))
    else:
        db_execute(conn, "UPDATE exam_sessions SET finished_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
    conn.commit()

    session = db_fetchone(conn, _sql("SELECT * FROM exam_sessions WHERE id = ?"), (session_id,))
    conn.close()

    if not session:
        return jsonify({"error": "Session introuvable"}), 404

    return jsonify({
        "score": row_get(session, "score"),
        "total": row_get(session, "total"),
        "percentage": round(row_get(session, "score") / row_get(session, "total") * 100, 1)
    })


@app.route("/api/stats")
def get_stats():
    user_id = request.args.get("user")
    conn = get_db()

    if user_id:
        where = "WHERE user_id = ?"
        params = (user_id,)
        correct_q = "SELECT COUNT(*) as c FROM results WHERE user_id = ? AND is_correct = true"
    else:
        where = ""
        params = ()
        correct_q = "SELECT COUNT(*) as c FROM results WHERE is_correct = true"

    total = row_get(db_fetchone(conn, _sql(f"SELECT COUNT(*) as c FROM results {where}"), params), "c")
    correct = row_get(db_fetchone(conn, _sql(correct_q), params), "c")

    theme_stats = db_fetchall(conn, _sql(f"""
        SELECT theme, COUNT(*) as total,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM results {where} GROUP BY theme ORDER BY theme
    """), params)

    diff_stats = db_fetchall(conn, _sql(f"""
        SELECT difficulty, COUNT(*) as total,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM results {where} GROUP BY difficulty ORDER BY difficulty
    """), params)

    exam_where = "WHERE user_id = ? AND finished_at IS NOT NULL" if user_id else "WHERE finished_at IS NOT NULL"
    exams = db_fetchall(conn, _sql(f"""
        SELECT id, started_at, score, total FROM exam_sessions
        {exam_where} ORDER BY started_at DESC LIMIT 10
    """), params)

    daily = db_fetchall(conn, _sql("""
        SELECT DATE(created_at) as day, user_id,
               SUM(points) as points,
               COUNT(*) as total_exos,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_exos
        FROM results
        GROUP BY DATE(created_at), user_id
        ORDER BY day ASC
    """))

    log_where = "WHERE user_id = ?" if user_id else ""
    log_params = (user_id,) if user_id else ()
    activity = db_fetchall(conn, _sql(f"""
        SELECT user_id, theme, difficulty, is_correct, is_retry, points, created_at
        FROM results {log_where}
        ORDER BY created_at DESC LIMIT 50
    """), log_params)

    total_points_row = db_fetchone(conn, _sql(f"SELECT SUM(points) as pts FROM results {where}"), params)
    total_points = row_get(total_points_row, "pts") or 0

    conn.close()

    return jsonify({
        "global": {
            "total": total,
            "correct": correct,
            "percentage": round(correct / total * 100, 1) if total > 0 else 0,
            "points": round(total_points, 1)
        },
        "by_theme": [
            {"theme": row_get(r, "theme"), "total": row_get(r, "total"), "correct": row_get(r, "correct"),
             "percentage": round(row_get(r, "correct") / row_get(r, "total") * 100, 1) if row_get(r, "total") > 0 else 0}
            for r in theme_stats
        ],
        "by_difficulty": [
            {"difficulty": row_get(r, "difficulty"), "total": row_get(r, "total"), "correct": row_get(r, "correct"),
             "percentage": round(row_get(r, "correct") / row_get(r, "total") * 100, 1) if row_get(r, "total") > 0 else 0}
            for r in diff_stats
        ],
        "recent_exams": [
            {"id": row_get(r, "id"), "date": str(row_get(r, "started_at")), "score": row_get(r, "score"),
             "total": row_get(r, "total"), "percentage": round(row_get(r, "score") / row_get(r, "total") * 100, 1)}
            for r in exams
        ],
        "daily": [
            {"day": str(row_get(r, "day")), "user": row_get(r, "user_id"), "points": row_get(r, "points") or 0,
             "total_exos": row_get(r, "total_exos"), "correct_exos": row_get(r, "correct_exos")}
            for r in daily
        ],
        "activity": [
            {"user": row_get(r, "user_id"), "theme": row_get(r, "theme"), "difficulty": row_get(r, "difficulty"),
             "correct": bool(row_get(r, "is_correct")), "retry": bool(row_get(r, "is_retry")),
             "points": row_get(r, "points") or 0, "date": str(row_get(r, "created_at"))}
            for r in activity
        ]
    })


@app.route("/api/bookmark", methods=["POST"])
def add_bookmark():
    data = request.json
    user_id = data.get("user", "alia")
    conn = get_db()
    db_execute(conn, _sql(
        """INSERT INTO bookmarks (user_id, statement, theme, difficulty, correct_answer, explanation, user_answer)
           VALUES (?, ?, ?, ?, ?, ?, ?)"""
    ), (user_id, data["statement"], data["theme"], data["difficulty"],
        data["correct_answer"], data["explanation"], data.get("user_answer")))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/bookmarks")
def get_bookmarks():
    user_id = request.args.get("user", "alia")
    conn = get_db()
    rows = db_fetchall(conn, _sql(
        "SELECT * FROM bookmarks WHERE user_id = ? ORDER BY reviewed ASC, created_at DESC"
    ), (user_id,))
    conn.close()
    return jsonify([
        {"id": row_get(r, "id"), "statement": row_get(r, "statement"), "theme": row_get(r, "theme"),
         "difficulty": row_get(r, "difficulty"), "correct_answer": row_get(r, "correct_answer"),
         "explanation": row_get(r, "explanation"), "user_answer": row_get(r, "user_answer"),
         "date": str(row_get(r, "created_at")), "reviewed": bool(row_get(r, "reviewed"))}
        for r in rows
    ])


@app.route("/api/bookmark/<int:bid>/review", methods=["POST"])
def toggle_review(bid):
    conn = get_db()
    db_execute(conn, _sql(
        "UPDATE bookmarks SET reviewed = NOT reviewed WHERE id = ?"
    ), (bid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/bookmark/<int:bid>", methods=["DELETE"])
def delete_bookmark(bid):
    conn = get_db()
    db_execute(conn, _sql("DELETE FROM bookmarks WHERE id = ?"), (bid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/stats/reset", methods=["POST"])
def reset_stats():
    conn = get_db()
    db_execute(conn, "DELETE FROM results")
    db_execute(conn, "DELETE FROM exam_sessions")
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/stats/add_points", methods=["POST"])
def add_manual_points():
    data = request.json
    user_id = data.get("user", "alia")
    points = data.get("points", 0)
    note = data.get("note", "Points ajoutes manuellement")

    conn = get_db()
    db_execute(conn, _sql(
        """INSERT INTO results
           (user_id, exercise_id, theme, difficulty, user_answer, correct_answer,
            is_correct, is_retry, points, mode, session_id)
           VALUES (?, 0, ?, 0, 0, 0, true, false, ?, 'manual', ?)"""
    ), (user_id, note, points, f"manual_{datetime.now().strftime('%Y%m%d%H%M%S')}"))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "points_added": points})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
