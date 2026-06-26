import math

def calculate_euclidean_distance(vec_a, vec_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

def calculate_velocity(spatial_drift, time_delta):
    return spatial_drift / max(0.001, time_delta)

def calculate_acceleration(current_velocity, last_velocity, time_delta):
    return (current_velocity - last_velocity) / max(0.001, time_delta)

def is_orbital_lock(velocity, acceleration, history_length):
    return (
        velocity < 0.18 and
        abs(acceleration) < 0.08 and
        history_length >= 2
    )

def calculate_threat_mass(current_mass, history, decay=0.70, window=4):
    accumulated = current_mass
    for rank, past in enumerate(reversed(history[-window:])):
        accumulated += past["mass"] * (decay ** (rank + 1))
    return accumulated
