import time
import yaml
from price_fetcher import get_price
from decision_engine import evaluate
from notifier import send_email
from utils import load_pending, save_pending

def load_state():
    state = {}
    with open("state.txt") as f:
        for line in f:
            k, v = line.strip().split("=")
            state[k] = float(v) if "." in v else v
    return state

config = yaml.safe_load(open("config.yaml"))

print("🚀 Crypto Notifier started")

while True:
    pending = load_pending()

    if pending.get("pending"):
        time.sleep(config["check_interval_sec"])
        continue

    state = load_state()
    asset = state["ASSET"]
    price = get_price(asset)

    decisions = evaluate(
        price,
        state["LAST_REFERENCE_PRICE"],
        state["CURRENT_BALANCE"],
        state["AVAILABLE_CASH_HKD"],
        config
    )

    if decisions:
        decision = decisions[0]  # only one at a time
        subject = f"[CRYPTO ACTION] {decision['type']} {asset}"

        body = "\n".join([
            f"Asset: {asset}",
            f"Current price: {decision['price']} HKD",
            f"Trigger: {decision['trigger_pct']}%",
            "",
            "ACTION:",
            str(decision),
            "",
            "After executing trade:",
            "👉 Update state.txt with new balance & reference price"
        ])

        send_email(subject, body, config["email"])

        save_pending({
            "pending": True,
            "decision": decision,
            "reference_price": state["LAST_REFERENCE_PRICE"]
        })

        print("📧 Email sent. Waiting for manual state update.")

    time.sleep(config["check_interval_sec"])
