CIRCUIT_OPEN = "CIRCUIT_BREAKER_TRIPPED"
CIRCUIT_CLOSED = "PROCEED"

def evaluate_circuit(velocity, acceleration, threat_mass, threshold=140):
    from sentryn.kinematics import is_orbital_lock
    if is_orbital_lock(velocity, acceleration, 2) or threat_mass > threshold:
        return {
            "verdict": CIRCUIT_OPEN,
            "reason": "ORBITAL_LOOP_LOCK detected",
            "velocity": round(velocity, 4),
            "acceleration": round(acceleration, 4),
            "threat_mass": round(threat_mass, 2),
            "status": 423
        }
    return {"verdict": CIRCUIT_CLOSED, "status": 200}
