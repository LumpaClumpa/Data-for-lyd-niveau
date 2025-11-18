from socket import gethostname
import sqlite3
import json
from time import time
from random import random
from flask import Flask, render_template, make_response, request, jsonify, url_for

app = Flask(__name__)

DB_PATH = "LD.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # create threshold table
    cur.execute("""CREATE TABLE IF NOT EXISTS thresholds (lokale INTEGER PRIMARY KEY,maxDB REAL)""")
    # create maalinger (measurements) table
    cur.execute("""CREATE TABLE IF NOT EXISTS maalinger (id INTEGER PRIMARY KEY AUTOINCREMENT,ts INTEGER,lokale INTEGER,db REAL)""")

    # ensure at least one threshold exists
    cur.execute("SELECT COUNT(*) FROM thresholds")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO thresholds (lokale, maxDB) VALUES (?, ?)", (221, 60.0))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/arduino", methods=["POST"])
def receive_from_arduino():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON received"}), 400
    # expected JSON: { "lokale": 2221, "db": 55.2 }
    try:
        lokale = int(data.get("lokale"))
        db_val = float(data.get("db"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid payload, expected 'lokale' and 'db'"}), 400
    ts = int(time() * 1000)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO maalinger (ts, lokale, db) VALUES (?, ?, ?)", (ts, lokale, db_val))
    conn.commit()
    conn.close()
    return jsonify({"status": "ok", "lokale": lokale, "db": db_val, "ts": ts}), 201

@app.route("/graf", methods=["GET"])
def graf():
    return render_template("index.html")

@app.route("/maalinger/<int:lokale>", methods=["GET"])
def maalinger_for_lokale(lokale):
    # return last 500 measurements as array of [ts, db]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT ts, db FROM maalinger WHERE lokale = ? ORDER BY ts DESC LIMIT 500", (lokale,))
    rows = cur.fetchall()
    conn.close()
    # return ordered ascending by timestamp
    rows = list(reversed(rows))
    return jsonify([[r[0], r[1]] for r in rows])

@app.route("/thresholds", methods=["GET"])
def list_thresholds():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT lokale, maxDB FROM thresholds")
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"lokale": r[0], "maxDB": r[1]} for r in rows])

@app.route("/thresholds", methods=["POST"])
def upsert_threshold():
    data = request.get_json(silent=True) or {}
    try:
        lokale = int(data.get("lokale"))
        max_db = float(data.get("maxDB"))
    except (TypeError, ValueError):
        return jsonify({"error": "Expected JSON with integer 'lokale' and numeric 'maxDB'"}), 400
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO thresholds (lokale, maxDB) VALUES (?, ?)
        ON CONFLICT(lokale) DO UPDATE SET maxDB=excluded.maxDB
    """, (lokale, max_db))
    conn.commit()
    conn.close()
    return jsonify({"lokale": lokale, "maxDB": max_db}), 201

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
