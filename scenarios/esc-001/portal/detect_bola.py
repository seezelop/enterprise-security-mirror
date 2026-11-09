import json
from pathlib import Path

LOG_FILE = Path(__file__).parent / "logs" / "events.jsonl"

if not LOG_FILE.exists():
    print("[INFO] No se encontró el archivo de eventos.")
    raise SystemExit(0)

alerts = 0

with LOG_FILE.open(encoding="utf-8") as file:
    for line in file:
        event = json.loads(line)

        if (
            event.get("event") == "customer_access"
            and event.get("result") == "allowed"
            and event.get("role") == "cliente"
            and event.get("assigned_customer") is not None
            and event.get("customer_id") is not None
            and event["assigned_customer"] != event["customer_id"]
        ):
            alerts += 1
            print("[ALERT] Potential BOLA exploitation")
            print(f"  User: {event['username']}")
            print(f"  Assigned customer: {event['assigned_customer']}")
            print(f"  Accessed customer: {event['customer_id']}")
            print(f"  Timestamp: {event['timestamp']}")
            print()

print(f"[RESULT] {alerts} suspicious access events detected")
