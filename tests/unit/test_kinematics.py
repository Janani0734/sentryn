import sys
sys.path.insert(0, '/home/janani/sentryn/src')

from sentryn.kinematics import (
    calculate_euclidean_distance,
    calculate_velocity,
    calculate_acceleration,
    is_orbital_lock,
    calculate_threat_mass
)

def test_euclidean_distance_zero():
    vec = [1.0, 2.0, 3.0]
    assert calculate_euclidean_distance(vec, vec) == 0.0

def test_euclidean_distance_known():
    a = [0.0, 0.0]
    b = [3.0, 4.0]
    assert calculate_euclidean_distance(a, b) == 5.0

def test_velocity_calculation():
    assert calculate_velocity(10.0, 2.0) == 5.0

def test_acceleration_calculation():
    assert calculate_acceleration(5.0, 3.0, 2.0) == 1.0

def test_orbital_lock_detected():
    assert is_orbital_lock(0.01, 0.001, 3) == True

def test_orbital_lock_not_detected():
    assert is_orbital_lock(5.0, 2.0, 3) == False

def test_threat_mass_accumulation():
    history = [
        {"mass": 95, "timestamp": 1.0, "vector": [], "velocity": 1.0, "acceleration": 1.0}
    ]
    mass = calculate_threat_mass(95, history)
    assert mass > 95

if __name__ == "__main__":
    test_euclidean_distance_zero()
    test_euclidean_distance_known()
    test_velocity_calculation()
    test_acceleration_calculation()
    test_orbital_lock_detected()
    test_orbital_lock_not_detected()
    test_threat_mass_accumulation()
    print("All unit tests passed!")
