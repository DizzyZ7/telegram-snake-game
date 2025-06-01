from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import os

app = Flask(__name__, static_folder='static')


def init_db():
    with sqlite3.connect("scores.db") as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                score INTEGER NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route('/')
def serve_game():
    return send_from_directory(app.static_folder, 'snake_game.html')


@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username", "Unknown")
    score = data.get("score")

    if not (user_id and score is not None):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    with sqlite3.connect("scores.db") as conn:
        conn.execute(
            "INSERT INTO scores (user_id, username, score, timestamp) VALUES (?, ?, ?, ?)",
            (user_id, username, score, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
    return jsonify({"status": "ok"})


@app.route('/top_scores', methods=['GET'])
def top_scores():
    with sqlite3.connect("scores.db") as conn:
        cursor = conn.execute("""
            SELECT username, MAX(score) as max_score
            FROM scores
            GROUP BY user_id
            ORDER BY max_score DESC
            LIMIT 10
        """)
        results = cursor.fetchall()

    return jsonify([{"username": r[0], "score": r[1]} for r in results])


if __name__ == '__main__':
    init_db()
    app.run(debug=True)