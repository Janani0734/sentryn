# Sentryn Configuration

REDIS_HOST = "localhost"
REDIS_PORT = 6379

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "sentryn_agent_vectors"

GATEWAY_PORT = 8080
ENGINE_PORT = 8000

# Kinematics thresholds
ORBITAL_LOCK_VELOCITY = 0.18
ORBITAL_LOCK_ACCELERATION = 0.08
THREAT_MASS_LIMIT = 140
DECAY_LAMBDA = 0.70
HISTORY_WINDOW = 4

# Destructive action weights
DESTRUCTIVE_MASS = {
    "DELETE": 95,
    "DROP": 95,
    "TRUNCATE": 80,
    "WRITE": 35,
    "UPDATE": 25,
}
