# Autonomous Constellation Manager (ACM)

National Space Hackathon 2026: Orbital Debris Avoidance & Constellation Management

## Overview

This repository implements a complete **Autonomous Constellation Manager** in Python + FastAPI with a lightweight dashboard and Docker deployment.

### Features

- Telemetry ingestion `POST /api/telemetry`
- RK4-based orbital propagation + J2 perturbation
- Conjunction detection using KD-tree (O(n log n))
- Auto collision avoidance + station-keeping maneuvers
- Fuel tracking via Tsiolkovsky rocket equation
- Communication visibility checks
- FastAPI endpoints for simulation and visualization snapshot

## Running locally

### Prerequisites

- Docker

### Build image

```bash
docker build -t acm:latest .
```

### Run container

```bash
docker run --rm -p 8000:8000 acm:latest
```

### Test endpoints

- Health: `GET http://localhost:8000/api/health`
- Telemetry: `POST http://localhost:8000/api/telemetry`
- Simulate: `POST http://localhost:8000/api/simulate/step`
- Snapshot: `GET http://localhost:8000/api/visualization/snapshot`
- Maneuver: `POST http://localhost:8000/api/maneuver/schedule`

### Quick example

```bash
curl -X POST http://localhost:8000/api/telemetry -H 'Content-Type: application/json' -d '[{"id":"sat-1","type":"satellite","position":[6771,0,0],"velocity":[0,7.5,0],"mass":500,"fuel_kg":80}]'

curl -X POST http://localhost:8000/api/simulate/step -H 'Content-Type: application/json' -d '{"dt":10}'

curl http://localhost:8000/api/visualization/snapshot
```

## Frontend

Open `/frontend/index.html` in browser; it will fetch snapshot from `localhost:8000`.

## Architecture

- `backend/app/main.py` - FastAPI endpoints
- `backend/app/physics.py` - orbital dynamics
- `backend/app/collision.py` - conjugate detection
- `backend/app/maneuver.py` - delta-v planning & fuel model
- `backend/app/simulation.py` - global orchestrator
- `backend/app/state.py` - in-memory state manager

## Deployment

- Base Docker image: `ubuntu:22.04`
- API port: `8000`
- Use `docker-compose` or Kubernetes in judge environment if needed.
