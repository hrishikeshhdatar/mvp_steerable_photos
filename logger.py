import json
import time

class TelemetryLogger:
    def __init__(self, log_file="session_log.jsonl"):
        self.log_file = log_file

    def log_event(self, event_type: str, details: dict):
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "details": details
        }
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
