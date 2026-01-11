# backend/state/system_state.py

class SystemState:
    def __init__(self):
        self.status = "RUNNING"
        self.reason = None

    def freeze(self, reason: str):
        self.status = "FROZEN"
        self.reason = reason

    def shutdown(self, reason: str):
        self.status = "SHUTDOWN"
        self.reason = reason

    def assert_running(self):
        if self.status != "RUNNING":
            raise RuntimeError(f"System not running: {self.status} ({self.reason})")