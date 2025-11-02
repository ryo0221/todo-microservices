# ToDo Microservices — FastAPI × Docker × TDD

> A practical microservices learning project with clean architecture, docs-as-code, and TDD.

## Overview

This project implements a minimal but realistic microservices system for hands-on learning of:

* Microservice architecture & service boundaries
* API Gateway routing
* Stateless authentication with JWT
* Docker-based local dev workflow
* TDD for backend services
* Docs-as-Code (ADR included)

It simulates practical production patterns in a small, clear scope.

---

## Architecture

```
[ Client ] ──▶ [ API Gateway ] ──▶  /auth/*  ─▶ [ Auth Service ] ──▶ [ Postgres (auth) ]
                        │
                        └─────────▶  /todos/* ─▶ [ Todo Service ] ──▶ [ Postgres (todo) ]
(任意) 監視/分散トレース: [ Prometheus / Grafana / Jaeger / OpenTelemetry Collector ]
(任意) 非同期イベント:   [ RabbitMQ or Redis ]  ← 第2フェーズで導入
```

> Detailed decisions are recorded in `docs/adr/`.

---

## Tech Stack

| Category   | Technology                          |
| ---------- | ----------------------------------- |
| Framework  | FastAPI                             |
| Database   | PostgreSQL (SQLite for tests)       |
| Auth       | JWT (HS256)                         |
| Containers | Docker Compose                      |
| Testing    | Pytest + FastAPI TestClient         |
| Docs       | ADR (Architecture Decision Records) |

### Principles

* Test-Driven Development (Red → Green → Refactor)
* Clear service boundaries
* Local dev ≈ production pattern
* Repeatable infra setup (docker-compose + make)

---

## Features

| Service | Description                                            |
| ------- | ------------------------------------------------------ |
| Auth    | Register, Login, Password Hashing, JWT issuance        |
| Todo    | User-scoped CRUD                                       |
| Gateway | Routes `/auth/*` and `/todos/*`, forwards auth headers |

---

## Directory Structure

```
.
├── services
│ ├── auth
│ │ ├── app
│ │ ├── tests
│ │ └── Dockerfile
│ └── todo
│ ├── app
│ ├── tests
│ └── Dockerfile
├── gateway
│ ├── app
│ ├── tests (planned)
│ └── Dockerfile
├── infra/docker
├── docs/adr
└── ops (scripts, Make targets)
```

---

## Getting Started

### Prerequisites

* Docker & Docker Compose
* Make (optional but recommended)

### Start Dev Environment

```bash
make dev
```

Services:

| Service      | URL                                            |
| ------------ | ---------------------------------------------- |
| API Gateway  | [http://localhost:8000](http://localhost:8000) |
| Auth Service | [http://localhost:8001](http://localhost:8001) |
| Todo Service | [http://localhost:8002](http://localhost:8002) |

### Run Tests

```bash
docker compose run --rm auth pytest
docker compose run --rm todo pytest
```

---

## ADR (Architecture Decision Records)

Key design decisions are documented in:

```
docs/adr/
```

Initial ADRs include:

* Record architecture decisions
* Service split (Auth / Todo)
* TDD for microservices
* Docker compose override (hot-reload dev env)

---

## Roadmap

* ✅ Microservices foundation
* ✅ TDD for each service
* ✅ ADR workflow
* ⏳ API Gateway auth utilities
* ⏳ CI (GitHub Actions)
* ⏳ Minimal UI (HTMX/FastAPI templates or React SPA)
* 🚀 Deploy to cloud (Fly.io / Render / ECS)

---

## License

MIT

