# Sentryn - AI Agent Guardrail Platform

**🟢 Live Demo:** https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io
**📖 API Docs:** https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io/docs

## The Problem Sentryn Solves

As AI agents become more autonomous, a single reasoning error can cause an agent to enter a recursive loop:

1. Agent detects a database issue
2. Agent attempts a fix → fix fails → agent retries with the same reasoning
3. Agent repeats hundreds of times

**Result:** runaway API costs, infrastructure damage, data corruption. Sentryn stops this before it happens.

## Architecture
AI Agent → Python FastAPI Engine (8000) → Redis + Qdrant

- **FastAPI Engine** — intercepts every agent action, converts reasoning into 768-dim semantic vectors using nomic-embed-text-v1.5, runs kinematic loop detection
- **Redis** — per-agent execution history with 7-day TTL
- **Qdrant** — vector embeddings for permanent audit trail
- **Azure Container Apps** — independently scaled containers in Korea Central

## How Loop Detection Works

Every agent action is converted into a semantic vector using nomic-embed-text-v1.5 (768-dim). Sentryn tracks these vectors using kinematic equations:

- **Velocity** = semantic distance between consecutive actions / time delta
- **Acceleration** = change in velocity / time delta
- **Threat Mass** = weighted destructive action scores with exponential decay

When velocity drops near zero (orbital lock), the circuit breaker trips → **HTTP 423**.

## Security

- **API Key Auth** — X-API-Key header required on all /evaluate requests (401 without it)
- **Pydantic v2 Validation** — blocks malformed inputs before reaching the model
- **Credential Scrubbing** — redacts passwords, API keys, tokens before vector storage
- **Injection Blocking** — 8/8 known injection patterns blocked (jailbreak, DROP TABLE, UNION SELECT, etc.)

## Tech Stack

| Layer | Technology |
|---|---|
| API Framework | Python · FastAPI · Uvicorn |
| Embeddings | nomic-embed-text-v1.5 (768-dim) |
| State Storage | Redis 7.2 |
| Vector Audit Trail | Qdrant v1.9 |
| Input Validation | Pydantic v2 |
| Cloud | Azure Container Apps (Korea Central) |
| CI/CD | GitHub Actions → Azure Container Registry |
| Containers | Docker |

## Live API

```bash
# Health check
curl https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io/health

# Evaluate agent action
curl -X POST https://sentryn-engine.ambitioushill-87ee6da5.koreacentral.azurecontainerapps.io/evaluate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sentryn-prod-key-2026" \
  -d '{"action_verb": "DELETE", "target_resource": "prod-database", "reasoning_context": "fixing error", "agent_id": "agent_001"}'
```

## Test Results (26/26 passing)

```bash
pytest tests/test_engine.py -v
```

| Category | Tests | Result |
|---|---|---|
| API Key Authentication | 3 | ✅ |
| Health & Root endpoints | 3 | ✅ |
| Pydantic validation | 4 | ✅ |
| Injection blocking | 8 | ✅ |
| Credential scrubbing | 4 | ✅ |
| Circuit breaker logic | 4 | ✅ |
| **Total** | **26** | **✅ 26/26** |

## Benchmark Results (Live Azure)

| Metric | Result |
|---|---|
| Loop detection accuracy | 100% |
| Circuit breaker trips on | 2nd repeated action |
| Injection patterns blocked | 8/8 |
| Auth enforcement | 401 without key |
| All backends | Redis ✅ Qdrant ✅ nomic ✅ |

## What I Learned

- Silent exception swallowing hides critical bugs in production — always log warnings
- Azure Container Apps internal DNS resolves short service names but some libraries need `prefer_grpc=False`
- Mocking heavy ML dependencies (torch, sentence-transformers) enables fast pytest runs without loading 2GB models

## Future Improvements

- Next.js dashboard for real-time agent monitoring
- Go Fiber gateway for credential scrubbing at ingress
- Threshold tuning based on empirical loop detection data
- Multi-tenant API key management
- Alert webhooks when circuit breaker trips
