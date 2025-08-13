import os, requests, threading, time, datetime
from fastapi import FastAPI, Body

# ====== CONFIG ======
PIPEDREAM_WEBHOOK_URL = os.getenv("PIPEDREAM_WEBHOOK_URL")  # set on Render
SEND_INTERVAL_SECONDS = int(os.getenv("SEND_INTERVAL_SECONDS", "600"))  # every 10 mins (600)
# ====================

app = FastAPI()

def send_to_webhook(payload: dict):
    if not PIPEDREAM_WEBHOOK_URL:
        print("No PIPEDREAM_WEBHOOK_URL set.")
        return
    try:
        r = requests.post(PIPEDREAM_WEBHOOK_URL, json=payload, timeout=10)
        print("POST", r.status_code, r.text[:200])
    except Exception as e:
        print("Error sending to webhook:", e)

def make_pick_payload(
    player="(Heartbeat) System Online",
    market="Over 1.5 Shots",
    bookie="bet365",
    odds=2.10,
    model_prob=0.55,
    fair_odds=1.82,
    stake=0.8,
    checks="Pipeline warmup · Email verified · Scheduler active",
    rationale="This is a heartbeat to confirm end-to-end delivery.",
    title="(Heartbeat) System Online – Ready for picks",
    subject="[System] Heartbeat – Feed Online"
):
    return {
        "player": player,
        "market": market,
        "bookie": bookie,
        "odds": odds,
        "model_prob": model_prob,
        "fair_odds": fair_odds,
        "stake": stake,
        "checks": checks,
        "rationale": rationale,
        "title": title,
        "subject": subject,
    }

def background_sender():
    """Sends one heartbeat immediately, then ticks every N seconds.
       Later, replace the tick body with real odds/stat scanning."""
    # Immediate heartbeat
    send_to_webhook(make_pick_payload())
    print("Heartbeat sent.")

    # Periodic tick (placeholder message so you see it's alive)
    while True:
        time.sleep(SEND_INTERVAL_SECONDS)
        now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        payload = make_pick_payload(
            player="(Scheduler Tick)",
            market="Polling markets…",
            odds=1.90,
            model_prob=0.52,
            fair_odds=1.85,
            stake=0.3,
            checks=f"Tick @ {now} · Ready to scan",
            rationale="This is a periodic tick. When live APIs are connected, this sends real picks.",
            title=f"(Tick) Feed active @ {now}",
            subject=f"[System] Tick {now}"
        )
        send_to_webhook(payload)
        print("Tick sent.")

@app.on_event("startup")
def on_startup():
    # Start the background thread
    t = threading.Thread(target=background_sender, daemon=True)
    t.start()

@app.get("/")
def root():
    return {"status": "ok", "message": "Edge Picks Sender running."}

@app.post("/send")
def send_custom_pick(payload: dict = Body(...)):
    """Manually send a pick (POST JSON with your fields)."""
    send_to_webhook(payload)
    return {"status": "sent"}
