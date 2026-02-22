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
@app.route("/log")
def log():
    user = request.args.get("user", "").strip()
    force = request.args.get("force", "0")

    if not user:
        return "Missing ?user=NAME", 400

    from zoneinfo import ZoneInfo
    IST = ZoneInfo("Asia/Kolkata")
    now_ist = datetime.now(IST)

    # ⛔ Only count at 6:07 PM IST unless force=1
    if now_ist.strftime("%H:%M") != "18:07" and force != "1":
        return "Not counted (only at 6:07 PM IST).", 200

    today = now_ist.date().isoformat()
    yesterday = (now_ist.date() - timedelta(days=1)).isoformat()

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

    return f"✅ Counted! {user} streak = {streaks[user]}"
@app.route("/leaderboard")
def leaderboard():
    ranked = sorted(data["streaks"].items(), key=lambda x: x[1], reverse=True)
    return jsonify(ranked)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
from flask import Response

@app.get("/ui")
def ui():
    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>67 Streak</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; background: #0b0f19; color: #e8eaf0; }
    .wrap { max-width: 720px; margin: 0 auto; padding: 24px; }
    .card { background: #121a2a; border: 1px solid #22304d; border-radius: 16px; padding: 18px; box-shadow: 0 10px 30px rgba(0,0,0,.25); }
    h1 { margin: 0 0 8px; font-size: 26px; }
    p { margin: 6px 0 14px; color: #b9c2d8; }
    .row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
    input, button { border-radius: 12px; border: 1px solid #2a3b61; background: #0f1626; color: #e8eaf0; padding: 12px 14px; font-size: 16px; }
    input { flex: 1; min-width: 180px; }
    button { cursor: pointer; background: #2b5cff; border-color: #2b5cff; font-weight: 700; }
    button.secondary { background: transparent; border-color: #2a3b61; font-weight: 600; }
    button:disabled { opacity: .6; cursor: not-allowed; }
    .msg { margin-top: 12px; padding: 12px; border-radius: 12px; background: #0f1626; border: 1px solid #22304d; color: #cfe0ff; white-space: pre-wrap; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; overflow: hidden; border-radius: 14px; }
    th, td { padding: 12px; border-bottom: 1px solid #22304d; text-align: left; }
    th { color: #b9c2d8; font-weight: 700; font-size: 14px; }
    tr:last-child td { border-bottom: none; }
    .pill { display: inline-block; padding: 6px 10px; border-radius: 999px; background: #0f1626; border: 1px solid #22304d; color: #b9c2d8; font-size: 12px; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <h1>67 Streak</h1>
      <p class="pill">Click to log your 67, then see the leaderboard</p>

      <div class="row">
        <input id="name" placeholder="Your name (exact spelling)" />
        <button id="logBtn" onclick="log67()">Log 67</button>
        <button class="secondary" onclick="refreshBoard()">Refresh</button>
      </div>

      <div id="out" class="msg" style="display:none;"></div>

      <h2 style="margin:18px 0 8px; font-size:18px;">Leaderboard</h2>
      <table>
        <thead>
          <tr><th>#</th><th>Name</th><th>Streak</th></tr>
        </thead>
        <tbody id="board">
          <tr><td colspan="3" style="color:#b9c2d8;">Loading…</td></tr>
        </tbody>
      </table>
    </div>
  </div>

<script>
  async function log67() {
    const name = document.getElementById("name").value.trim();
    if (!name) return show("Type your name first.");

    const btn = document.getElementById("logBtn");
    btn.disabled = true;

    // If you kept the strict time rule, use force=1 for testing:
    // const url = `/log?user=${encodeURIComponent(name)}&force=1`;
    const url = `/log?user=${encodeURIComponent(name)}`;

    try {
      const res = await fetch(url);
      const text = await res.text();
      show(text);
      await refreshBoard();
    } catch (e) {
      show("Error contacting server.");
    } finally {
      btn.disabled = false;
    }
  }

  function show(text) {
    const out = document.getElementById("out");
    out.style.display = "block";
    out.textContent = text;
  }

  async function refreshBoard() {
    const tbody = document.getElementById("board");
    try {
      const res = await fetch("/leaderboard");
      if (!res.ok) throw new Error();
      const data = await res.json(); // [["Raj", 3], ["Keerapi", 2], ...]
      if (!data.length) {
        tbody.innerHTML = `<tr><td colspan="3" style="color:#b9c2d8;">No entries yet.</td></tr>`;
        return;
      }
      tbody.innerHTML = data.map((row, i) => `
        <tr>
          <td>${i+1}</td>
          <td>${escapeHtml(row[0])}</td>
          <td><b>${row[1]}</b></td>
        </tr>
      `).join("");
    } catch (e) {
      tbody.innerHTML = `<tr><td colspan="3" style="color:#b9c2d8;">Couldn’t load leaderboard.</td></tr>`;
    }
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  }

  refreshBoard();
  setInterval(refreshBoard, 15000);
</script>
</body>
</html>
"""
    return Response(html, mimetype="text/html")
