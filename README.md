# Sentryn — AI Agent Guardrail Platform

Sentryn is an enterprise AI governance middleware that sits between autonomous AI agents and critical production systems. It intercepts every agent action before execution, detects recursive execution loops using kinematic mathematics, and trips a circuit breaker before damage occurs.

## The Problem Sentryn Solves

As AI agents become more autonomous, a single reasoning error can cause an agent to enter a recursive loop:

1. Agent detects a database issue
2. Agent attempts a fix
3. Fix fails
4. Agent retries with the same reasoning
5. Agent repeats hundreds of times

The result: runaway API costs, infrastructure instability, data corruption. Sentryn stops this before it happens.

## Architecture

AI Agent → Go Fiber Gateway (8080) → Python Oversight Engine (8000) → Redis + Qdrant

- Go Fiber Gateway — high-speed ingestion layer that scrubs credentials from every payload before forwarding
- Python Oversight Engine — converts agent reasoning into 768-dimension semantic vectors using nomic-embed-text-v1.5 and runs kinematic loop detection
- Redis — stores per-agent execution history for real-time state tracking
- Qdrant — stores vector embeddings for permanent audit trail

## How Loop Detection Works

Every agent action is converted into a semantic vector using nomic-embed-text-v1.5 running locally. Sentryn tracks these vectors across time using kinematic equations:

- Velocity = semantic distance between consecutive actions / time delta
- Acceleration = change in velocity / time delta

When an agent gets stuck in a loop, its reasoning stops changing — velocity drops to zero. Sentryn detects this orbital lock and trips the circuit breaker on the 3rd iteration, returning HTTP 423.

## Security

- Pydantic v2 input validation blocks prompt injection attacks before they reach the model
- Credential scrubbing removes passwords, API keys, and secrets from all payloads
- All ML processing happens locally — no data leaves the network

## Tech Stack

- Go + Fiber — gateway layer
- Python + FastAPI + Uvicorn — oversight engine
- sentence-transformers nomic-embed-text-v1.5 — local semantic embeddings
- Redis — agent state memory
- Qdrant — vector storage
- Docker — infrastructure
- Pydantic v2 — input validation

## Running Locally

Start infrastructure:
cd infra && docker-compose up -d

Start Python engine:
cd src/sentryn/agent-oversight-core/engine
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

Start Go gateway:
cd src/sentryn/api-gateway
go run main.go

## Testing

Unit tests:
python tests/unit/test_kinematics.py

Injection blocking tests:
python tests/property/test_injection.py

Load tests:
python tests/load/test_load.py

## Test Results

- Unit tests: 7/7 passed
- Injection blocking: 6/6 payloads blocked
- Load test: 40 requests, 100% loop detection rate, avg latency 3886ms on CPU
