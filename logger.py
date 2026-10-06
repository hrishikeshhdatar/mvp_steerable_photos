import json
import os
import time

class EventLogger:
    def __init__(self, log_file="data/session_log.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

    def log_event(self, event_type: str, data: dict):
        """Logs user interactions, feedback signals (+1/-1), and search telemetry."""
        event = {
            "timestamp": time.time(),
            "event_type": event_type,
            "data": data
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Logging error: {e}")
