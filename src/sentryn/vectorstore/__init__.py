from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import random

COLLECTION_NAME = "sentryn_agent_vectors"

def get_client():
    return QdrantClient(host="localhost", port=6333, check_compatibility=False)

def ensure_collection(client, vector_size=10):
    try:
        client.get_collection(COLLECTION_NAME)
    except:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

def store_vector(client, vector, agent_id, action_verb, target_resource, timestamp):
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[PointStruct(
            id=random.randint(1, 999999999),
            vector=vector,
            payload={
                "agent_id": agent_id,
                "action_verb": action_verb,
                "target_resource": target_resource,
                "timestamp": timestamp
            }
        )]
    )
