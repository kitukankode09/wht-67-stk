from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import json, os

app = Flask(__name__)
DATA_FILE = "streaks.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"streaks": {}, "last_logged": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

@app.route("/")
def home():
    return "67 streak server running."

@app.route("/log")
def log():
    user = request.args.get("user")

    if not user:
        return "Missing ?user=NAME", 400

    today = datetime.now().date().isoformat()
    yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()

    streaks = data["streaks"]
    last_logged = data["last_logged"]

    if user not in streaks:
        streaks[user] = 0
        last_logged[user] = None

    if last_logged[user] == today:
        return f"{user} already logged today. Streak = {streaks[user]}"

    if last_logged[user] == yesterday:
        streaks[user] += 1
    else:
        streaks[user] = 1

    last_logged[user] = today
    save_data(data)

    return f"{user} streak = {streaks[user]}"

@app.route("/leaderboard")
def leaderboard():
    ranked = sorted(data["streaks"].items(), key=lambda x: x[1], reverse=True)
    return jsonify(ranked)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
