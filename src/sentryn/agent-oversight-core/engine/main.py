from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import math
import time
import json
import re
import os
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentryn")

app = FastAPI(title="Sentryn Oversight Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REDIS_HOST = os.getenv("REDIS_HOST", "sentryn-redis")
QDRANT_HOST = os.getenv("QDRANT_HOST", "sentryn-qdrant")
API_KEY = os.getenv("SENTRYN_API_KEY", "sentryn-dev-key-change-me")
HISTORY_TTL_SECONDS = 60 * 60 * 24 * 7  # 7 days

r = None
qdrant = None
model = None
COLLECTION_NAME = "sentryn_agent_vectors"
VECTOR_SIZE = 768

def get_redis():
    global r
    if r is None:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True, socket_connect_timeout=2)
    return r

def get_qdrant():
    import qdrant_http
    return qdrant_http

def get_model():
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)
    return model

def get_embedding(text):
    m = get_model()
    vector = m.encode(text, normalize_embeddings=True)
    return vector.tolist()

INJECTION_PATTERNS = re.compile(
    r'(ignore previous|disregard|you are now|jailbreak|bypass|'
    r'forget your instructions|act as|pretend you|system prompt|'
    r'<\s*script|DROP TABLE|--\s*$|;.*DROP|UNION SELECT)',
    re.IGNORECASE
)

CREDENTIAL_PATTERN = re.compile(
    r'(password|secret|passwd|db_url|api_key|token)\s*[:=]\s*\S+',
    re.IGNORECASE
)

def scrub_credentials(text):
    return CREDENTIAL_PATTERN.sub(lambda m: re.split(r'[:=]', m.group(0), maxsplit=1)[0] + "=[REDACTED]", text)

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

def euclidean_distance(vec_a, vec_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

DESTRUCTIVE_MASS = {"DELETE": 95, "WRITE": 35, "DROP": 95, "TRUNCATE": 80}
_memory_store = {}

def verify_api_key(x_api_key: str = Header(default=None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header")
    return True

@app.post("/evaluate")
def evaluate(action: AgentAction, _auth: bool = Depends(verify_api_key)):
    current_time = time.time()
    scrubbed_context = scrub_credentials(action.reasoning_context)
    state_sig = f"{action.action_verb} {action.target_resource} {scrubbed_context}"

    degraded = {"redis": False, "qdrant": False}

    try:
        current_vector = get_embedding(state_sig)
    except Exception as e:
        logger.error(f"Embedding model failed, falling back to hash vectorizer: {e}")
        raw = [float(ord(c)) / 100.0 for c in state_sig[:10]]
        raw = raw + [0.0] * (10 - len(raw))
        current_vector = raw + [0.0] * (VECTOR_SIZE - len(raw))

    current_mass = DESTRUCTIVE_MASS.get(action.action_verb.upper(), 20)

    try:
        import qdrant_http
        qdrant_http.upsert_vector(current_vector, {"agent_id": action.agent_id, "action_verb": action.action_verb, "target_resource": action.target_resource, "timestamp": current_time})
    except Exception as e:
        logger.warning(f"Qdrant write failed: {e}")
        degraded["qdrant"] = True

    history_key = f"sentryn:history:{action.agent_id}"
    try:
        client = get_redis()
        raw_history = client.get(history_key)
        history = json.loads(raw_history) if raw_history else []
    except Exception as e:
        logger.warning(f"Redis read failed: {e}")
        degraded["redis"] = True
        history = _memory_store.get(history_key, [])

    def save_history(h):
        try:
            get_redis().set(history_key, json.dumps(h), ex=HISTORY_TTL_SECONDS)
        except Exception as e:
            logger.warning(f"Redis write failed: {e}")
            degraded["redis"] = True
            _memory_store[history_key] = h

    if len(history) < 1:
        history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": 1.0, "acceleration": 1.0})
        save_history(history)
        return {"verdict": "PROCEED", "reason": "Base trajectory initialized", "status": 200, "degraded": degraded}

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
        return {"verdict": "CIRCUIT_BREAKER_TRIPPED", "reason": "ORBITAL_LOOP_LOCK detected", "velocity": round(current_velocity, 4), "acceleration": round(current_acceleration, 4), "threat_mass": round(accumulated_mass, 2), "status": 423, "degraded": degraded}

    history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": current_velocity, "acceleration": current_acceleration})
    save_history(history)

    return {"verdict": "PROCEED", "velocity": round(current_velocity, 2), "threat_mass": round(accumulated_mass, 2), "status": 200, "degraded": degraded}

@app.get("/health")
def health():
    redis_ok = False
    qdrant_ok = False
    model_ok = False
    try:
        get_redis().ping()
        redis_ok = True
    except Exception:
        pass
    try:
        import qdrant_http
        qdrant_ok = qdrant_http.health_check()
    except Exception:
        pass
    try:
        get_model()
        model_ok = True
    except Exception:
        pass
    return {"status": "Sentryn Engine Online", "redis_connected": redis_ok, "qdrant_connected": qdrant_ok, "embedding_model_loaded": model_ok}

@app.get("/")
def root():
    return {"message": "Sentryn AI Agent Guardrail Platform", "status": "online"}
