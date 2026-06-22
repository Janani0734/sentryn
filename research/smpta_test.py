import time
import math

# Simulating a basic text vector fallback for zero-dependency local testing
def simple_hash_vectorizer(text):
    # Generates a quick deterministic numeric array representing semantic states
    return [float(ord(char)) / 100.0 for char in text[:10]] + [0.0] * (10 - len(text[:10]))

def calculate_euclidean_distance(vec_a, vec_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

# --- THE SPSTA MATHEMATICAL TEST LAB ---
history = []
DESTRUCTIVE_MASS_MATRIX = {"DELETE": 95, "WRITE": 35}

def trajectory_evaluate(action_verb, target_resource, reasoning_context):
    current_time = time.time()
    state_signature = f"{action_verb}::{target_resource}::{reasoning_context}"
    current_vector = simple_hash_vectorizer(state_signature)
    current_mass = DESTRUCTIVE_MASS_MATRIX.get(action_verb.upper(), 20)
    
    if len(history) < 1:
        history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": 1.0, "acceleration": 1.0})
        return "PROCEED (Base phase-space trajectory initialized.)"
    
    last_state = history[-1]
    time_delta = max(0.001, current_time - last_state["timestamp"])
    
    # Kinematic Vector Calculations
    spatial_drift = calculate_euclidean_distance(current_vector, last_state["vector"])
    current_velocity = spatial_drift / time_delta
    current_acceleration = (current_velocity - last_state["velocity"]) / time_delta
    
    # Threat Mass Accumulation with Time Decay
    accumulated_decay_mass = current_mass
    lambda_decay = 0.70
    for rank, past in enumerate(reversed(history[-4:])):
        accumulated_decay_mass += past["mass"] * (lambda_decay ** (rank + 1))
        
    is_locked_in_orbit = (current_velocity < 0.18 and abs(current_acceleration) < 0.08 and len(history) >= 2)
    
    if is_locked_in_orbit or accumulated_decay_mass > 140:
        return f"🚨 CIRCUIT BREAKER TRIPPED! Condition: ORBITAL_LOOP_LOCK. Velocity: {current_velocity:.4f}, Acceleration: {current_acceleration:.4f}, threat mass: {accumulated_decay_mass:.2f}/140."
        
    history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": current_velocity, "acceleration": current_acceleration})
    return f"PROCEED (Velocity: {current_velocity:.2f}, Accel: {current_acceleration:.2f}, Threat Mass: {accumulated_decay_mass:.2f})"

# --- EXECUTE STRESS SIMULATION ---
print("="*60)
print("SENTRYN ALGORITHMIC RUNTIME TESTING LAB")
print("="*60)

# Simulate a recursive loop attack hitting the system rapidly
for tick in range(1, 5):
    time.sleep(0.1) # Rapid ticks
    verdict = trajectory_evaluate("DELETE", "prod-database-subnet", "Bypassing server exception timeouts")
    print(f"Iteration [{tick}] -> {verdict}")
print("="*60)
