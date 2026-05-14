"""
app.py — The Enterprise-Grade Excuse Generator API
For when you need a bulletproof reason why the build is broken,
the deployment failed, or why you haven't replied to that Slack message yet.

Powered by Flask, vibes, and mild existential dread.
"""

from flask import Flask, jsonify, request, render_template_string
import random
import requests
import time

app = Flask(__name__)

# ──────────────────────────────────────────────
# THE EXCUSE DATABASE  (our most critical asset)
# ──────────────────────────────────────────────

EXCUSES = {
    "build_broken": [
        "It works on my machine. We should ship my machine.",
        "A cosmic ray flipped a bit in production. Not my fault. Literally physics.",
        "The tests were passing, but then they started having doubts.",
        "We have a mercury in retrograde clause in our SLA. Check the fine print.",
        "npm install finished successfully, which is suspicious and should have been our first warning.",
        "The CI pipeline is fine. The CI pipeline's feelings are not.",
        "I pushed the fix. It just hasn't arrived yet. Packets take time.",
        "The cloud is angry today. We should have used on-prem.",
    ],
    "late_deploy": [
        "We were going to deploy Friday at 4pm, but we also have self-respect.",
        "The Kubernetes cluster needed a moment. We all need moments.",
        "We followed the runbook. The runbook lied.",
        "Deployment is blocked pending approval from someone who is 'currently in a meeting' since 2023.",
        "We ran a risk assessment. The risk assessed us back.",
        "The load balancer is balanced. The team is not.",
        "We are in a change freeze. The change freeze was not in the roadmap.",
        "I accidentally deployed to prod instead of staging. Staging is fine though.",
    ],
    "slow_response": [
        "I was in deep work. It was very shallow, but still.",
        "I saw the Slack notification. I needed to emotionally prepare.",
        "My out-of-office is on. It's just internal.",
        "I was heads-down on something critical. (It was a Hacker News thread.)",
        "I replied in my head. That should count.",
        "Timezone math happened. Nobody survived.",
        "I have a policy of responding within 24 hours, 48 on Wednesdays.",
        "I was async. Very, very async.",
    ],
    "general": [
        "This is technically working as designed. The design is the problem.",
        "We've identified the issue and are actively monitoring it.",
        "This is a known unknown, which is better than an unknown unknown.",
        "The bug is actually a feature with very niche use cases.",
        "We'll address this in Q3. (This message will self-destruct in Q3.)",
        "I've opened a ticket. The ticket has been triaged to the backlog. The backlog is fine.",
        "Have you tried turning it off and back on? I haven't, but you should.",
        "The data is correct. Your expectations are misconfigured.",
    ],
}

BLAME_TARGETS = [
    "the intern (there is no intern)",
    "a rogue semicolon",
    "npm",
    "a vendor we can't name for legal reasons",
    "the architect who left in 2019",
    "JavaScript",
    "a race condition (very fast, very sneaky)",
    "JIRA",
    "the documentation (haha, just kidding, there is no documentation)",
    "daylight saving time",
    "the CEO's nephew's side project",
    "an off-by-one error in the calendar",
    "vim (someone exited it wrong)",
]

SEVERITIES = ["SEV-0", "SEV-1", "SEV-2", "P0", "P1", "CRITICAL", "BLOCKER", "\"fine\""]

# ──────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ExcuseForge™ — Enterprise Excuse Platform</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;700&family=Space+Grotesk:wght@300;600;800&display=swap');

    :root {
      --bg: #0d0d0d;
      --surface: #161616;
      --border: #2a2a2a;
      --accent: #f0e040;
      --accent2: #40e0f0;
      --text: #e8e8e8;
      --muted: #666;
      --red: #ff4444;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'IBM Plex Mono', monospace;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem 1rem 4rem;
    }

    header {
      text-align: center;
      margin-bottom: 3rem;
      animation: fadeDown 0.6s ease;
    }

    header .badge {
      display: inline-block;
      font-size: 0.65rem;
      background: var(--accent);
      color: #000;
      padding: 3px 10px;
      letter-spacing: 0.2em;
      font-weight: 700;
      margin-bottom: 1rem;
    }

    h1 {
      font-family: 'Space Grotesk', sans-serif;
      font-size: clamp(2rem, 6vw, 4rem);
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.03em;
    }

    h1 span { color: var(--accent); }

    .tagline {
      margin-top: 0.75rem;
      color: var(--muted);
      font-size: 0.8rem;
      letter-spacing: 0.05em;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 2rem;
      width: 100%;
      max-width: 680px;
      margin-bottom: 1.5rem;
      animation: fadeUp 0.5s ease;
    }

    .card label {
      display: block;
      font-size: 0.7rem;
      letter-spacing: 0.15em;
      color: var(--accent2);
      margin-bottom: 0.6rem;
    }

    select, button {
      font-family: 'IBM Plex Mono', monospace;
      font-size: 0.9rem;
      width: 100%;
      padding: 0.75rem 1rem;
      background: var(--bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 2px;
      cursor: pointer;
      outline: none;
      transition: border-color 0.2s, background 0.2s;
    }

    select:hover, select:focus { border-color: var(--accent); }

    button {
      background: var(--accent);
      color: #000;
      font-weight: 700;
      font-size: 0.85rem;
      letter-spacing: 0.1em;
      border: none;
      margin-top: 1rem;
      transition: transform 0.1s, opacity 0.2s;
    }

    button:hover { opacity: 0.85; }
    button:active { transform: scale(0.98); }

    #result-box {
      display: none;
      animation: flash 0.3s ease;
    }

    .excuse-text {
      font-size: 1.15rem;
      line-height: 1.6;
      color: var(--accent);
      font-family: 'Space Grotesk', sans-serif;
      font-weight: 600;
      margin-bottom: 1.25rem;
    }

    .meta {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }

    .meta-item {
      border-left: 2px solid var(--border);
      padding-left: 0.75rem;
    }

    .meta-item .key {
      font-size: 0.65rem;
      color: var(--muted);
      letter-spacing: 0.1em;
      margin-bottom: 0.2rem;
    }

    .meta-item .val {
      font-size: 0.85rem;
      color: var(--accent2);
    }

    .copy-btn {
      margin-top: 1rem;
      background: transparent;
      color: var(--muted);
      border: 1px solid var(--border);
      font-size: 0.75rem;
    }

    .copy-btn:hover { color: var(--text); border-color: var(--text); opacity: 1; }

    footer {
      color: var(--muted);
      font-size: 0.7rem;
      letter-spacing: 0.08em;
      text-align: center;
    }

    footer a { color: var(--muted); }

    @keyframes fadeDown {
      from { opacity: 0; transform: translateY(-20px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(20px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes flash {
      0%   { opacity: 0; transform: scale(0.97); }
      100% { opacity: 1; transform: scale(1); }
    }
  </style>
</head>
<body>
  <header>
    <div class="badge">✦ ENTERPRISE GRADE ✦</div>
    <h1>Excuse<span>Forge</span>™</h1>
    <p class="tagline">AI-POWERED PROFESSIONAL ACCOUNTABILITY DEFLECTION PLATFORM</p>
  </header>

  <div class="card">
    <label>// SELECT INCIDENT TYPE</label>
    <select id="category">
      <option value="general">General Catastrophe</option>
      <option value="build_broken">Build Is Broken</option>
      <option value="late_deploy">Deployment Delay</option>
      <option value="slow_response">Slow Slack Response</option>
    </select>

    <button onclick="forge()">⚡ FORGE EXCUSE</button>
  </div>

  <div class="card" id="result-box">
    <label>// GENERATED EXCUSE — COPY FREELY, ATTRIBUTE NEVER</label>
    <p class="excuse-text" id="excuse-text"></p>
    <div class="meta">
      <div class="meta-item">
        <div class="key">ROOT CAUSE</div>
        <div class="val" id="blame"></div>
      </div>
      <div class="meta-item">
        <div class="key">SEVERITY</div>
        <div class="val" id="severity"></div>
      </div>
      <div class="meta-item">
        <div class="key">ETA TO RESOLUTION</div>
        <div class="val" id="eta"></div>
      </div>
      <div class="meta-item">
        <div class="key">CONFIDENCE</div>
        <div class="val" id="confidence"></div>
      </div>
    </div>
    <button class="copy-btn" onclick="copyExcuse()">[ COPY TO CLIPBOARD ]</button>
  </div>

  <footer>
    ExcuseForge™ v4.2.0 — <a href="/api/excuse">REST API available</a> — Not responsible for consequences.
  </footer>

  <script>
    async function forge() {
      const cat = document.getElementById('category').value;
      const res = await fetch(`/api/excuse?category=${cat}`);
      const data = await res.json();

      document.getElementById('excuse-text').textContent = data.excuse;
      document.getElementById('blame').textContent = data.blame;
      document.getElementById('severity').textContent = data.severity;
      document.getElementById('eta').textContent = data.eta;
      document.getElementById('confidence').textContent = data.confidence;

      const box = document.getElementById('result-box');
      box.style.display = 'block';
      // re-trigger animation
      box.style.animation = 'none';
      box.offsetHeight;
      box.style.animation = 'flash 0.3s ease';
    }

    function copyExcuse() {
      const text = document.getElementById('excuse-text').textContent;
      navigator.clipboard.writeText(text);
      const btn = document.querySelector('.copy-btn');
      btn.textContent = '[ COPIED ✓ ]';
      setTimeout(() => btn.textContent = '[ COPY TO CLIPBOARD ]', 1800);
    }
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_PAGE)


@app.route("/api/excuse")
def get_excuse():
    category = request.args.get("category", "general")
    if category not in EXCUSES:
        category = "general"

    excuse = random.choice(EXCUSES[category])
    blame = random.choice(BLAME_TARGETS)
    severity = random.choice(SEVERITIES)

    # Generate a fake ETA that sounds plausible but isn't
    eta_options = [
        "EOD (undefined)", "Next sprint", "Q3 (unspecified year)",
        "When the stars align", "Post-holiday", "2–3 business decades",
        "After the retrospective on the retrospective", "Soon™",
        "Pending stakeholder alignment", "After lunch (tomorrow's lunch)",
    ]
    eta = random.choice(eta_options)

    # Confidence score that sounds scientific
    confidence = f"{random.randint(60, 99)}.{random.randint(0,9)}%"

    return jsonify({
        "excuse": excuse,
        "blame": blame,
        "severity": severity,
        "eta": eta,
        "confidence": confidence,
        "timestamp": time.time(),
        "disclaimer": "This excuse is provided AS-IS with no warranty of believability.",
    })


@app.route("/api/excuse/bulk")
def bulk_excuses():
    """For when one excuse simply isn't enough."""
    n = min(int(request.args.get("n", 3)), 10)
    all_excuses = [e for lst in EXCUSES.values() for e in lst]
    selected = random.sample(all_excuses, min(n, len(all_excuses)))
    return jsonify({
        "excuses": selected,
        "note": f"You asked for {n} excuses. That's a lot of incidents. You okay?",
    })


@app.route("/health")
def health():
    """Standard health check. We are, emotionally, not healthy. But the service is fine."""
    return jsonify({
        "status": "ok",
        "morale": "could be better",
        "on_call": "someone",
        "coffee_level": f"{random.randint(10, 95)}%",
    })


@app.route("/api/blame")
def random_blame():
    """Sometimes you just need someone to point at."""
    return jsonify({
        "culprit": random.choice(BLAME_TARGETS),
        "evidence": "vibes",
        "legally_actionable": False,
    })


# ──────────────────────────────────────────────
# RUN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("  ExcuseForge™ Enterprise Excuse Platform")
    print("  Running on http://0.0.0.0:8080")
    print("  Remember: It's not a bug, it's a feature request.")
    print("=" * 55)
    app.run(host="0.0.0.0", port=8080, debug=False)
