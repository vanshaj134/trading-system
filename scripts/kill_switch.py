# scripts/kill_switch.py

from backend.state.system_state import SystemState

state = SystemState()

def kill(reason="manual override"):
    state.shutdown(reason)
    print(f"SYSTEM SHUTDOWN: {reason}")

if __name__ == "__main__":
    kill()