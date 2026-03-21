import json
import random
import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from generator import generate_exercise, generate_exam as gen_exam

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "pofm.db")
EXERCISES_PATH = os.path.join(os.path.dirname(__file__), "exercises.json")

USERS = {
    "alia": {"name": "Alia", "level": "college", "class": "4eme"},
    "imran": {"name": "Imran", "level": "lycee", "class": "1ere"},
}


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL DEFAULT 'alia',
            exercise_id INTEGER NOT NULL,
            theme TEXT NOT NULL,
            difficulty INTEGER NOT NULL,
            user_answer INTEGER,
            correct_answer INTEGER NOT NULL,
            is_correct BOOLEAN NOT NULL,
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


def store_exercise(ex):
    """Persiste un exercice genere dans SQLite."""
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO exercise_store (id, theme, difficulty, statement, answer, explanation) VALUES (?,?,?,?,?,?)",
        (ex["id"], ex["theme"], ex["difficulty"], ex["statement"], ex["answer"], ex["explanation"])
    )
    conn.commit()
    conn.close()


def find_exercise(exercise_id):
    """Retrouve un exercice par ID (DB generee puis banque statique)."""
    conn = get_db()
    row = conn.execute("SELECT * FROM exercise_store WHERE id = ?", (exercise_id,)).fetchone()
    conn.close()
    if row:
        return {"id": row["id"], "theme": row["theme"], "difficulty": row["difficulty"],
                "statement": row["statement"], "answer": row["answer"], "explanation": row["explanation"]}
    exercises = load_exercises()
    return next((e for e in exercises if e["id"] == exercise_id), None)


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

    store_exercise(ex)
    return jsonify({
        "id": ex["id"],
        "theme": ex["theme"],
        "difficulty": ex["difficulty"],
        "statement": ex["statement"]
    })


@app.route("/api/exam/generate")
def generate_exam_route():
    session_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(100, 999))
    user_id = request.args.get("user", "alia")
    exercises = gen_exam(25)

    for ex in exercises:
        store_exercise(ex)

    conn = get_db()
    conn.execute(
        "INSERT INTO exam_sessions (id, user_id, total) VALUES (?, ?, ?)",
        (session_id, user_id, len(exercises))
    )
    conn.commit()
    conn.close()

    return jsonify({
        "session_id": session_id,
        "exercises": [
            {"num": i, "id": ex["id"], "theme": ex["theme"],
             "difficulty": ex["difficulty"], "statement": ex["statement"]}
            for i, ex in enumerate(exercises, 1)
        ],
        "total": len(exercises)
    })


@app.route("/api/submit", methods=["POST"])
def submit_answer():
    data = request.json
    exercise_id = data.get("exercise_id")
    user_answer = data.get("answer")
    mode = data.get("mode", "individual")
    session_id = data.get("session_id")
    user_id = data.get("user", "alia")

    exercise = find_exercise(exercise_id)

    if not exercise:
        return jsonify({"error": "Exercice introuvable"}), 404

    is_correct = user_answer == exercise["answer"]

    conn = get_db()
    conn.execute(
        """INSERT INTO results
           (user_id, exercise_id, theme, difficulty, user_answer, correct_answer, is_correct, mode, session_id)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, exercise_id, exercise["theme"], exercise["difficulty"],
         user_answer, exercise["answer"], is_correct, mode, session_id)
    )
    if session_id and is_correct:
        conn.execute(
            "UPDATE exam_sessions SET score = score + 1 WHERE id = ?",
            (session_id,)
        )
    conn.commit()
    conn.close()

    return jsonify({
        "correct": is_correct,
        "correct_answer": exercise["answer"],
        "explanation": exercise["explanation"],
        "your_answer": user_answer
    })


@app.route("/api/exam/finish", methods=["POST"])
def finish_exam():
    data = request.json
    session_id = data.get("session_id")

    conn = get_db()
    conn.execute(
        "UPDATE exam_sessions SET finished_at = CURRENT_TIMESTAMP WHERE id = ?",
        (session_id,)
    )
    conn.commit()
    session = conn.execute(
        "SELECT * FROM exam_sessions WHERE id = ?", (session_id,)
    ).fetchone()
    conn.close()

    if not session:
        return jsonify({"error": "Session introuvable"}), 404

    return jsonify({
        "score": session["score"],
        "total": session["total"],
        "percentage": round(session["score"] / session["total"] * 100, 1)
    })


@app.route("/api/stats")
def get_stats():
    user_id = request.args.get("user")
    conn = get_db()

    where = "WHERE user_id = ?" if user_id else ""
    params = (user_id,) if user_id else ()

    total = conn.execute(f"SELECT COUNT(*) as c FROM results {where}", params).fetchone()["c"]
    correct = conn.execute(f"SELECT COUNT(*) as c FROM results {where} AND is_correct = 1" if user_id else "SELECT COUNT(*) as c FROM results WHERE is_correct = 1", params if user_id else ()).fetchone()["c"]

    theme_stats = conn.execute(f"""
        SELECT theme, COUNT(*) as total,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM results {where} GROUP BY theme ORDER BY theme
    """, params).fetchall()

    diff_stats = conn.execute(f"""
        SELECT difficulty, COUNT(*) as total,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
        FROM results {where} GROUP BY difficulty ORDER BY difficulty
    """, params).fetchall()

    exam_where = "WHERE user_id = ? AND finished_at IS NOT NULL" if user_id else "WHERE finished_at IS NOT NULL"
    exams = conn.execute(f"""
        SELECT id, started_at, score, total FROM exam_sessions
        {exam_where} ORDER BY started_at DESC LIMIT 10
    """, params).fetchall()

    # Daily points: each exercise gives points based on difficulty
    daily = conn.execute(f"""
        SELECT DATE(created_at) as day, user_id,
               SUM(CASE WHEN is_correct THEN difficulty ELSE 0 END) as points,
               COUNT(*) as total_exos,
               SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct_exos
        FROM results
        GROUP BY DATE(created_at), user_id
        ORDER BY day ASC
    """).fetchall()

    conn.close()

    return jsonify({
        "global": {
            "total": total,
            "correct": correct,
            "percentage": round(correct / total * 100, 1) if total > 0 else 0
        },
        "by_theme": [
            {"theme": r["theme"], "total": r["total"], "correct": r["correct"],
             "percentage": round(r["correct"] / r["total"] * 100, 1) if r["total"] > 0 else 0}
            for r in theme_stats
        ],
        "by_difficulty": [
            {"difficulty": r["difficulty"], "total": r["total"], "correct": r["correct"],
             "percentage": round(r["correct"] / r["total"] * 100, 1) if r["total"] > 0 else 0}
            for r in diff_stats
        ],
        "recent_exams": [
            {"id": r["id"], "date": r["started_at"], "score": r["score"],
             "total": r["total"], "percentage": round(r["score"] / r["total"] * 100, 1)}
            for r in exams
        ],
        "daily": [
            {"day": r["day"], "user": r["user_id"], "points": r["points"],
             "total_exos": r["total_exos"], "correct_exos": r["correct_exos"]}
            for r in daily
        ]
    })


@app.route("/api/bookmark", methods=["POST"])
def add_bookmark():
    data = request.json
    user_id = data.get("user", "alia")
    conn = get_db()
    conn.execute(
        """INSERT INTO bookmarks (user_id, statement, theme, difficulty, correct_answer, explanation, user_answer)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (user_id, data["statement"], data["theme"], data["difficulty"],
         data["correct_answer"], data["explanation"], data.get("user_answer"))
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/bookmarks")
def get_bookmarks():
    user_id = request.args.get("user", "alia")
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM bookmarks WHERE user_id = ? ORDER BY reviewed ASC, created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return jsonify([
        {"id": r["id"], "statement": r["statement"], "theme": r["theme"],
         "difficulty": r["difficulty"], "correct_answer": r["correct_answer"],
         "explanation": r["explanation"], "user_answer": r["user_answer"],
         "date": r["created_at"], "reviewed": bool(r["reviewed"])}
        for r in rows
    ])


@app.route("/api/bookmark/<int:bid>/review", methods=["POST"])
def toggle_review(bid):
    conn = get_db()
    conn.execute("UPDATE bookmarks SET reviewed = NOT reviewed WHERE id = ?", (bid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/bookmark/<int:bid>", methods=["DELETE"])
def delete_bookmark(bid):
    conn = get_db()
    conn.execute("DELETE FROM bookmarks WHERE id = ?", (bid,))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@app.route("/api/stats/reset", methods=["POST"])
def reset_stats():
    conn = get_db()
    conn.execute("DELETE FROM results")
    conn.execute("DELETE FROM exam_sessions")
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
