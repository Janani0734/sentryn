import time
import json

def log_event(event_type, agent_id, verdict, threat_mass=None, velocity=None):
    log = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event_type,
        "agent_id": agent_id,
        "verdict": verdict,
    }
    if threat_mass is not None:
        log["threat_mass"] = threat_mass
    if velocity is not None:
        log["velocity"] = velocity
    print(f"[SENTRYN] {json.dumps(log)}")
    return log
