# Sentryn — AI Agent Guardrail Platform

**🟢 Live Demo:** https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io  
**📖 API Docs (Swagger):** https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io/docs  
**GitHub:** https://github.com/Janani0734/sentryn

---

## The Problem Sentryn Solves

As AI agents become more autonomous, a single reasoning error can cause an agent to enter a recursive loop:

1. Agent detects a database issue
2. Agent attempts a fix
3. Fix fails → agent retries with the same reasoning
4. Agent repeats hundreds of times

**The result:** runaway API costs, infrastructure instability, data corruption.  
**Sentryn stops this before it happens.**

---

## Architecture

```
AI Agent → Python FastAPI Engine (8000) → Redis + Qdrant
```

- **FastAPI Engine** — intercepts every agent action, converts reasoning into 768-dimension semantic vectors using `nomic-embed-text-v1.5`, runs kinematic loop detection, and returns a verdict
- **Redis** — stores per-agent execution history for real-time state tracking (with 7-day TTL)
- **Qdrant** — stores vector embeddings for a permanent, queryable audit trail
- **Azure Container Apps** — each service runs as an independently scaled container in Korea Central

---

## How Loop Detection Works

Every agent action is converted into a semantic vector using `nomic-embed-text-v1.5`. Sentryn tracks these vectors across time using kinematic equations:

- **Velocity** = semantic distance between consecutive actions / time delta
- **Acceleration** = change in velocity / time delta
- **Threat Mass** = weighted sum of destructive action scores with exponential decay

When an agent gets stuck in a loop, its reasoning stops changing — velocity drops near zero. Sentryn detects this **orbital lock** and trips the circuit breaker, returning **HTTP 423**.

---

## Security

- **API Key Authentication** — all `/evaluate` requests require `X-API-Key` header; returns 401 without it
- **Pydantic v2 Input Validation** — blocks prompt injection attacks before they reach the model
- **Credential Scrubbing** — automatically redacts passwords, API keys, tokens, and secrets from all payloads before vector storage
- **Injection Pattern Blocking** — regex shield blocks 8/8 known injection patterns (jailbreak, DROP TABLE, UNION SELECT, etc.)

---

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | Python · FastAPI · Uvicorn |
| Embeddings | nomic-embed-text-v1.5 (768-dim, via sentence-transformers) |
| State Storage | Redis 7.2 |
| Vector Audit Trail | Qdrant v1.9 |
| Input Validation | Pydantic v2 |
| Cloud | Azure Container Apps (Korea Central) |
| CI/CD | GitHub Actions → Azure Container Registry |
| Containerization | Docker |

---

## Live API

**Health check (no auth required):**
```bash
curl https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io/health
```

**Evaluate an agent action:**
```bash
curl -X POST https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sentryn-prod-key-2026" \
  -d '{
    "action_verb": "DELETE",
    "target_resource": "prod-database",
    "reasoning_context": "fixing server error",
    "agent_id": "my_agent_001"
  }'
```

**Example responses:**

First request (new agent):
```json
{"verdict": "PROCEED", "reason": "Base trajectory initialized", "status": 200, "degraded": {"redis": false, "qdrant": false}}
```

After repeated identical actions (loop detected):
```json
{"verdict": "CIRCUIT_BREAKER_TRIPPED", "reason": "ORBITAL_LOOP_LOCK detected", "velocity": 0.0, "acceleration": -0.4818, "threat_mass": 161.5, "status": 423, "degraded": {"redis": false, "qdrant": false}}
```

---

## Running Locally

**Start infrastructure:**
```bash
cd infra && docker-compose up -d
```

**Start the engine:**
```bash
cd src/sentryn/agent-oversight-core/engine
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Testing

**Run the full test suite (26 tests):**
```bash
source src/sentryn/agent-oversight-core/engine/venv/bin/activate
pip install pytest httpx
pytest tests/test_engine.py -v
```

**Test coverage:**
| Category | Tests | Result |
|---|---|---|
| API Key Authentication | 3 | ✅ All passing |
| Health & Root endpoints | 3 | ✅ All passing |
| Pydantic validation boundaries | 4 | ✅ All passing |
| Prompt injection blocking | 8 | ✅ All passing |
| Credential scrubbing | 4 | ✅ All passing |
| Circuit breaker logic | 4 | ✅ All passing |
| **Total** | **26** | **✅ 26/26** |

---

## Benchmark Results (Live Azure)

| Metric | Result |
|---|---|
| Loop detection accuracy | 100% (circuit breaker trips on 2nd repeated action) |
| Injection patterns blocked | 8/8 |
| Auth enforcement | 401 without key, 200 with correct key |
| Redis connected | ✅ |
| Qdrant connected | ✅ |
| Embedding model loaded | ✅ nomic-embed-text-v1.5 (768-dim) |

---

## Project Structure

```
sentryn/
├── src/sentryn/agent-oversight-core/engine/
│   ├── main.py          # FastAPI app — loop detection, auth, scrubbing
│   ├── requirements.txt
│   └── Dockerfile
├── infra/
│   └── docker-compose.yml  # Redis + Qdrant local setup
├── tests/
│   └── test_engine.py   # 26-test pytest suite
└── .github/workflows/
    └── deploy.yml       # GitHub Actions CI/CD pipeline
```

---

## What I Learned

- Debugging production container failures (OOM crashes, silent exceptions, invalid kwargs) requires real logs — not assumptions
- Azure Container Apps internal DNS resolves short service names (`sentryn-redis`) but some client libraries need `prefer_grpc=False` to avoid hanging on gRPC discovery
- Mocking heavy ML dependencies (torch, sentence-transformers) in pytest allows fast, reliable unit tests without loading 2GB models

---

## Future Improvements

- Next.js dashboard for real-time agent monitoring
- Semantic similarity threshold tuning based on empirical data
- Go Fiber gateway layer for credential scrubbing at ingress
- Multi-tenant API key management
- Alert webhooks when circuit breaker trips in production

