import os
import json
import time
import sqlite3
import subprocess
from datetime import date
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

DB_PATH = os.environ.get("DB_PATH", "devtrack.db")


# ── DB INIT ──────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id      TEXT PRIMARY KEY,
                data    TEXT NOT NULL,
                created TEXT NOT NULL
            )
        """)
        conn.commit()


# ── STATIC ───────────────────────────────────────────────
@app.route("/")
def index():
    return app.send_static_file("index.html")


# ── API: PROJECTS ─────────────────────────────────────────
@app.route("/api/projects", methods=["GET"])
def get_projects():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT data FROM projects ORDER BY created DESC"
        ).fetchall()
    return jsonify([json.loads(r["data"]) for r in rows])


@app.route("/api/projects", methods=["POST"])
def create_project():
    p = request.get_json()
    p["id"] = "p" + str(int(time.time() * 1000))
    p.setdefault("created", date.today().isoformat())
    p.setdefault("versions", [])
    with get_db() as conn:
        conn.execute(
            "INSERT INTO projects (id, data, created) VALUES (?, ?, ?)",
            (p["id"], json.dumps(p, ensure_ascii=False), p["created"]),
        )
        conn.commit()
    return jsonify(p), 201


@app.route("/api/projects/<pid>", methods=["PUT"])
def update_project(pid):
    p = request.get_json()
    with get_db() as conn:
        conn.execute(
            "UPDATE projects SET data = ? WHERE id = ?",
            (json.dumps(p, ensure_ascii=False), pid),
        )
        conn.commit()
    return jsonify(p)


@app.route("/api/projects/<pid>", methods=["DELETE"])
def delete_project(pid):
    with get_db() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
        conn.commit()
    return jsonify({"ok": True})


# ── API: VERSIONS (add to existing project) ──────────────
@app.route("/api/projects/<pid>/versions", methods=["POST"])
def add_version(pid):
    note = request.get_json().get("note", "")
    with get_db() as conn:
        row = conn.execute(
            "SELECT data FROM projects WHERE id = ?", (pid,)
        ).fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        p = json.loads(row["data"])
        p.setdefault("versions", []).append({
            "date": date.today().isoformat(),
            "note": note,
        })
        conn.execute(
            "UPDATE projects SET data = ? WHERE id = ?",
            (json.dumps(p, ensure_ascii=False), pid),
        )
        conn.commit()
    return jsonify(p)


# ── API: RUN .BAT (local only — ignored on Render) ───────
@app.route("/api/run", methods=["POST"])
def run_bat():
    bat_path = request.get_json().get("bat_path", "")
    if not bat_path:
        return jsonify({"error": "no bat_path"}), 400
    if not os.path.isfile(bat_path):
        return jsonify({"error": f"file not found: {bat_path}"}), 404
    try:
        subprocess.Popen(
            ["cmd.exe", "/c", "start", "", bat_path],
            shell=False,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
        )
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── HEALTH ────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "local": os.name == "nt"})


# ── INIT ON IMPORT (gunicorn + direct) ───────────────────
init_db()

# ── MAIN ──────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7474))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    print(f"\n✅  DevTrack שרת רץ על http://localhost:{port}\n")
    app.run(host=host, port=port, debug=debug)
