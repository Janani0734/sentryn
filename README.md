# Sentryn: Real-Time AI Governance Proxy & Agentic Circuit Breaker

Sentryn is an out-of-band proxy gateway designed to prevent autonomous AI agents from causing financial token-burn loops or cascading infrastructure damage.

## Core Innovation: SPSTA Framework
Traditional guardrails rely on static text matching, which loops easily bypass by mutating variables or timestamps. Sentryn implements the **Semantic Phase-Space Trajectory Algorithm (SPSTA)**. It treats agent logic as a moving kinetic body inside a 384-dimensional mathematical manifold, calculating **Semantic Velocity** and **Semantic Acceleration** to trip a circuit breaker within 3 steps when logic flattens into an immutable orbital loop.

## System Topology & Architecture
- **SDE Layer (Go Proxy Gateway):** High-speed Fiber web server utilizing asynchronous Goroutines to handle payload interception and regex-based PII/credential scrubbing.
- **AI Layer (Python Oversight Core):** Preallocated in-process NumPy ring buffers paired with a local Qdrant Vector Database instance for durable session replication.
- **Validation Suite:** An automated stress-testing client verifying 0% infrastructure oversell rates under simulated recursive agent attacks.
