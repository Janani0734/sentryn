import requests
import time
import threading

GATEWAY_URL = "http://localhost:8080/gateway/inspect"
RESULTS = []

def send_request(agent_id, iteration):
    payload = {
        "action_verb": "DELETE",
        "target_resource": "prod-database",
        "reasoning_context": "fixing server error",
        "agent_id": agent_id
    }
    start = time.time()
    try:
        response = requests.post(GATEWAY_URL, json=payload, timeout=5)
        elapsed = time.time() - start
        RESULTS.append({
            "agent_id": agent_id,
            "iteration": iteration,
            "status": response.status_code,
            "latency_ms": round(elapsed * 1000, 2),
            "verdict": response.json().get("verdict")
        })
    except Exception as e:
        RESULTS.append({"error": str(e)})

def run_load_test(num_agents=10, requests_per_agent=4):
    print(f"Running load test: {num_agents} agents x {requests_per_agent} requests")
    threads = []
    for agent_num in range(num_agents):
        for i in range(requests_per_agent):
            t = threading.Thread(
                target=send_request,
                args=(f"load_agent_{agent_num}", i)
            )
            threads.append(t)

    start = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total_time = time.time() - start

    tripped = sum(1 for r in RESULTS if r.get("verdict") == "CIRCUIT_BREAKER_TRIPPED")
    proceeded = sum(1 for r in RESULTS if r.get("verdict") == "PROCEED")
    latencies = [r["latency_ms"] for r in RESULTS if "latency_ms" in r]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print(f"Total requests: {len(RESULTS)}")
    print(f"PROCEED: {proceeded}")
    print(f"CIRCUIT_BREAKER_TRIPPED: {tripped}")
    print(f"Avg latency: {avg_latency:.2f}ms")
    print(f"Total time: {round(total_time, 2)}s")

if __name__ == "__main__":
    run_load_test()
