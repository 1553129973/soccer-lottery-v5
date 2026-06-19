import os, sys, json
from datetime import datetime
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Simple match data
MATCHES = [
    {"home":"??","away":"??","time":"00:00","date":"2026-06-20","lg":"???H?","lh":1.88,"la":1.56,"fh":"2?1?1?","fa":"3?1?2?","h2h":"????"},
    {"home":"??","away":"??","time":"03:00","date":"2026-06-20","lg":"???G?","lh":2.20,"la":1.20,"fh":"4?1?1?","fa":"1?2?3?","h2h":"??1?1?"},
    {"home":"???","away":"???","time":"06:00","date":"2026-06-20","lg":"???F?","lh":1.65,"la":1.10,"fh":"2?2?2?","fa":"0?3?3?","h2h":"????"},
    {"home":"???","away":"??","time":"09:00","date":"2026-06-20","lg":"???A?","lh":1.72,"la":1.30,"fh":"3?1?2?","fa":"2?2?2?","h2h":"??1?1?"},
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/api/matches")
def api_matches():
    return jsonify({"matches": MATCHES, "date": "2026-06-20"})

@app.route("/api/picks")
def api_picks():
    return jsonify({"picks": [], "date": "2026-06-20"})

@app.route("/api/full")
def api_full():
    return jsonify({"matches": MATCHES, "date": "2026-06-20"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
