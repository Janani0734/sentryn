import http.client
import json
import random
import os
import logging

logger = logging.getLogger("sentryn")

QDRANT_HOST = os.getenv("QDRANT_HOST", "sentryn-qdrant")
QDRANT_PORT = 6333
COLLECTION = "sentryn_agent_vectors"
VECTOR_SIZE = 768


def _request(method, path, body=None, timeout=15):
    logger.warning(f"[QDRANT] {method} {path}")

    conn = http.client.HTTPConnection(
        QDRANT_HOST,
        QDRANT_PORT,
        timeout=timeout
    )

    headers = {"Content-Type": "application/json"} if body else {}

    logger.warning("[QDRANT] Sending request...")
    conn.request(method, path, json.dumps(body) if body else None, headers)

    logger.warning("[QDRANT] Waiting for response...")
    resp = conn.getresponse()

    logger.warning(f"[QDRANT] HTTP {resp.status}")

    raw = resp.read().decode()

    logger.warning(f"[QDRANT] Body: {raw[:300]}")

    conn.close()

    if raw:
        data = json.loads(raw)
    else:
        data = {}

    return resp.status, data


def ensure_collection():
    status, _ = _request("GET", f"/collections/{COLLECTION}")

    if status == 404:
        _request(
            "PUT",
            f"/collections/{COLLECTION}",
            {
                "vectors": {
                    "size": VECTOR_SIZE,
                    "distance": "Cosine"
                }
            },
        )


def upsert_vector(vector, payload):
    ensure_collection()

    _request(
        "PUT",
        f"/collections/{COLLECTION}/points",
        {
            "points": [
                {
                    "id": random.randint(1, 999999999),
                    "vector": vector,
                    "payload": payload,
                }
            ]
        },
    )


def health_check():
    try:
        status, _ = _request("GET", "/collections", timeout=15)
        return status == 200
    except Exception as e:
        logger.warning(f"Qdrant health check failed: {e}")
        return False