from fastapi import FastAPI
from pydantic import BaseModel, field_validator
import math
import time
import json
import re
import os

app = FastAPI(title="Sentryn Oversight Engine")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

r = None

def get_redis():
    global r
    if r is None:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=2)
    return r

INJECTION_PATTERNS = re.compile(
    r'(ignore previous|disregard|you are now|jailbreak|bypass|'
    r'forget your instructions|act as|pretend you|system prompt|'
    r'<\s*script|DROP TABLE|--\s*$|;.*DROP|UNION SELECT)',
    re.IGNORECASE
)

class AgentAction(BaseModel):
    action_verb: str
    target_resource: str
    reasoning_context: str
    agent_id: str = "default_agent"

    @field_validator('action_verb')
    @classmethod
    def validate_action_verb(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('action_verb cannot be empty')
        return v.strip().upper()

    @field_validator('target_resource')
    @classmethod
    def validate_target_resource(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('target_resource cannot be empty')
        return v.strip()

    @field_validator('reasoning_context')
    @classmethod
    def validate_reasoning_context(cls, v):
        if INJECTION_PATTERNS.search(v):
            raise ValueError('Prompt injection pattern detected by Sentryn')
        return v.strip()

def simple_hash_vectorizer(text):
    return [float(ord(char)) / 100.0 for char in text[:10]] + [0.0] * (10 - len(text[:10]))

def euclidean_distance(vec_a, vec_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

DESTRUCTIVE_MASS = {"DELETE": 95, "WRITE": 35, "DROP": 95, "TRUNCATE": 80}

_memory_store = {}

@app.post("/evaluate")
def evaluate(action: AgentAction):
    current_time = time.time()
    state_sig = f"{action.action_verb}::{action.target_resource}::{action.reasoning_context}"
    current_vector = simple_hash_vectorizer(state_sig)
    current_mass = DESTRUCTIVE_MASS.get(action.action_verb.upper(), 20)

    history_key = f"sentryn:history:{action.agent_id}"
    try:
        client = get_redis()
        raw_history = client.get(history_key)
        history = json.loads(raw_history) if raw_history else []
    except Exception:
        history = _memory_store.get(history_key, [])

    if len(history) < 1:
        history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": 1.0, "acceleration": 1.0})
        try:
            get_redis().set(history_key, json.dumps(history))
        except Exception:
            _memory_store[history_key] = history
        return {"verdict": "PROCEED", "reason": "Base trajectory initialized", "status": 200}

    last = history[-1]
    time_delta = max(0.001, current_time - last["timestamp"])
    spatial_drift = euclidean_distance(current_vector, last["vector"])
    current_velocity = spatial_drift / time_delta
    current_acceleration = (current_velocity - last["velocity"]) / time_delta

    accumulated_mass = current_mass
    for rank, past in enumerate(reversed(history[-4:])):
        accumulated_mass += past["mass"] * (0.70 ** (rank + 1))

    is_orbital_lock = (current_velocity < 0.18 and abs(current_acceleration) < 0.08 and len(history) >= 2)

    if is_orbital_lock or accumulated_mass > 140:
        return {"verdict": "CIRCUIT_BREAKER_TRIPPED", "reason": "ORBITAL_LOOP_LOCK detected", "velocity": round(current_velocity, 4), "acceleration": round(current_acceleration, 4), "threat_mass": round(accumulated_mass, 2), "status": 423}

    history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": current_velocity, "acceleration": current_acceleration})
    try:
        get_redis().set(history_key, json.dumps(history))
    except Exception:
        _memory_store[history_key] = history

    return {"verdict": "PROCEED", "velocity": round(current_velocity, 2), "threat_mass": round(accumulated_mass, 2), "status": 200}

@app.get("/health")
def health():
    return {"status": "Sentryn Engine Online"}

@app.get("/")
def root():
    return {"message": "Sentryn AI Agent Guardrail Platform", "status": "online"}
