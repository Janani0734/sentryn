import requests

class SentryClient:
    def __init__(self, gateway_url="http://localhost:8080"):
        self.gateway_url = gateway_url

    def inspect(self, action_verb, target_resource, reasoning_context, agent_id="default_agent"):
        payload = {
            "action_verb": action_verb,
            "target_resource": target_resource,
            "reasoning_context": reasoning_context,
            "agent_id": agent_id
        }
        try:
            response = requests.post(
                f"{self.gateway_url}/gateway/inspect",
                json=payload,
                timeout=5
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Sentryn gateway unavailable", "verdict": "UNKNOWN"}
