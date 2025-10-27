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
    # Readings table
  
    # Seed one threshold if none exist
    cur.execute("SELECT COUNT(*) FROM thresholds")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO thresholds (lokale, maxDB) VALUES (?, ?)", (221, 60.0))
    conn.commit()
    conn.close()

@app.route("/")
def home():
    # templates/home.html must exist
    return render_template("home.html")

@app.route("/arduino", methods=["POST"])
def receive_from_arduino():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON received"}), 400
    # TODO: validate & insert into maalinger if desired
    return jsonify({"status": "success", "received": data}), 200

@app.route("/graf", methods=["GET"])
def graf():
    # templates/index.html must exist
    return render_template("index.html")

@app.route("/data", methods=["GET"])
def get_data():
    # Throttle on client side; this just returns a point
    payload = [int(time() * 1000), random() * 100]
    resp = make_response(json.dumps(payload))
    resp.content_type = "application/json"
    return resp

# Thresholds API (consistent!)
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
    # Avoid auto-reloader spawning duplicates in some environments
    app.run(host="0.0.0.0", port=5000, debug=False)
