import json

def save_history(redis_client, agent_id, history):
    key = f"sentryn:history:{agent_id}"
    redis_client.set(key, json.dumps(history))

def load_history(redis_client, agent_id):
    key = f"sentryn:history:{agent_id}"
    raw = redis_client.get(key)
    return json.loads(raw) if raw else []

def clear_history(redis_client, agent_id):
    key = f"sentryn:history:{agent_id}"
    redis_client.delete(key)
    return {"cleared": agent_id}
