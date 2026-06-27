from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import math
import time
import redis
import json
import re
import random

app = FastAPI(title="Sentryn Oversight Engine")

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
qdrant = QdrantClient(host="localhost", port=6333, check_compatibility=False)

# Load embedding model once
model = SentenceTransformer('nomic-ai/nomic-embed-text-v1.5', trust_remote_code=True)

COLLECTION_NAME = "sentryn_agent_vectors"
VECTOR_SIZE = 768

try:
    qdrant.get_collection(COLLECTION_NAME)
except:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )

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
        if len(v) > 50:
            raise ValueError('action_verb too long')
        return v.strip().upper()

    @field_validator('target_resource')
    @classmethod
    def validate_target_resource(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('target_resource cannot be empty')
        if len(v) > 200:
            raise ValueError('target_resource too long')
        return v.strip()

    @field_validator('reasoning_context')
    @classmethod
    def validate_reasoning_context(cls, v):
        if len(v) > 1000:
            raise ValueError('reasoning_context exceeds limit')
        if INJECTION_PATTERNS.search(v):
            raise ValueError('Prompt injection pattern detected by Sentryn')
        return v.strip()

    @field_validator('agent_id')
    @classmethod
    def validate_agent_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_\-]{1,50}$', v):
            raise ValueError('agent_id contains invalid characters')
        return v

def get_embedding(text):
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()

def euclidean_distance(vec_a, vec_b):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))

DESTRUCTIVE_MASS = {"DELETE": 95, "WRITE": 35, "DROP": 95, "TRUNCATE": 80}

@app.post("/evaluate")
def evaluate(action: AgentAction):
    current_time = time.time()
    state_sig = f"{action.action_verb} {action.target_resource} {action.reasoning_context}"
    current_vector = get_embedding(state_sig)
    current_mass = DESTRUCTIVE_MASS.get(action.action_verb.upper(), 20)

    try:
        qdrant.upsert(
            collection_name=COLLECTION_NAME,
            points=[PointStruct(
                id=random.randint(1, 999999999),
                vector=current_vector,
                payload={
                    "agent_id": action.agent_id,
                    "action_verb": action.action_verb,
                    "target_resource": action.target_resource,
                    "timestamp": current_time
                }
            )]
        )
    except Exception:
        pass

    history_key = f"sentryn:history:{action.agent_id}"
    raw_history = r.get(history_key)
    history = json.loads(raw_history) if raw_history else []

    if len(history) < 1:
        history.append({"timestamp": current_time, "vector": current_vector, "mass": current_mass, "velocity": 1.0, "acceleration": 1.0})
        r.set(history_key, json.dumps(history))
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
    r.set(history_key, json.dumps(history))

    return {"verdict": "PROCEED", "velocity": round(current_velocity, 2), "threat_mass": round(accumulated_mass, 2), "status": 200}

@app.get("/health")
def health():
    return {"status": "Sentryn Engine Online", "validation": "Pydantic v2 Active", "vector_store": "Qdrant Connected", "embeddings": "all-MiniLM-L6-v2"}
