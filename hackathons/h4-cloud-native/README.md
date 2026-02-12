# H4: Cloud-Native Todo Application

> **Panaversity Hackathon II -- Phase 4: Kubernetes + Dapr + Kafka + Observability**
>
> Built by [@asadullah48](https://github.com/asadullah48) | Targeting: **Platinum Tier**

## Achievement Summary

| Session | Deliverable | Status |
|---------|-------------|--------|
| Session 1 | Kubernetes cluster + Docker containers + 14 manifests | Done |
| Session 2 | Dapr service mesh + event-driven architecture (5 events) | Done |
| Session 3 | Kafka (Strimzi KRaft) + Notification microservice + Prometheus | Done |
| Session 4 | CI/CD pipeline + architecture docs + submission | Done |

## Architecture

```
Frontend (Next.js + Dapr) --> Backend (FastAPI + Dapr) --> Kafka --> Notification Service
                                        |
                                PostgreSQL + Redis + Prometheus
```

See [docs/architecture.md](docs/architecture.md) for full architecture diagram.

## Technology Stack

- **Orchestration**: Kubernetes (Minikube v1.35.0)
- **Service Mesh**: Dapr (sidecar pattern)
- **Event Streaming**: Apache Kafka (Strimzi KRaft v4.0.0 -- no ZooKeeper)
- **Backend**: Python FastAPI + Prometheus metrics
- **Frontend**: Next.js 14
- **Database**: PostgreSQL 15 (StatefulSet with PVC)
- **State/Cache**: Redis 7
- **Monitoring**: Prometheus (scraping 4 targets)
- **CI/CD**: GitHub Actions (test -> build -> validate -> security scan)

## Key Technical Achievements

### Zero-Downtime Infrastructure Migration
Switched Dapr pub/sub from Redis to Kafka with zero application code changes -- Dapr's abstraction layer made the infrastructure swap completely transparent.

### Resource-Constrained Cloud-Native
Deployed full production stack (Kafka + Dapr + Prometheus + 3 microservices) within a 6GB Minikube cluster at only 44% memory utilization through careful resource budgeting.

### Event-Driven Microservices
5 event types flowing through Kafka with durable persistence, consumed by a dedicated Notification microservice -- true event sourcing pattern.

### Production-Grade Observability
Custom Prometheus metrics (4 metric types) with automatic scraping of application metrics AND Dapr sidecar metrics across all services.

## Quick Start

### Prerequisites
- Docker Desktop
- Minikube
- kubectl
- Dapr CLI
- Helm (optional)

### Deploy

```bash
# Start cluster
minikube start --memory=6144 --cpus=4

# Create namespace
kubectl apply -f k8s/base/00-namespace.yaml

# Deploy infrastructure
kubectl apply -f k8s/base/01-configmap.yaml
kubectl apply -f k8s/base/02-secret.yaml
kubectl apply -f k8s/base/03-postgresql.yaml
kubectl apply -f k8s/base/06-redis.yaml

# Install Dapr
dapr init -k
kubectl apply -f k8s/base/07-dapr-statestore.yaml
kubectl apply -f k8s/base/11-dapr-pubsub-kafka.yaml

# Deploy Kafka (Strimzi)
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl apply -f k8s/base/09-kafka.yaml
kubectl apply -f k8s/base/10-kafka-topics.yaml

# Deploy applications
kubectl apply -f k8s/base/04-backend.yaml
kubectl apply -f k8s/base/05-frontend.yaml
kubectl apply -f k8s/base/12-notification-service.yaml

# Deploy monitoring
kubectl apply -f k8s/base/13-prometheus.yaml

# Verify
kubectl get pods -n todo-app
kubectl get pods -n kafka
```

### Access Services

```bash
# Backend API
kubectl port-forward -n todo-app svc/backend 8000:8000

# Frontend
kubectl port-forward -n todo-app svc/frontend 3000:3000

# Prometheus
kubectl port-forward -n todo-app svc/prometheus 9090:9090

# Metrics
curl http://localhost:8000/metrics
```

## Project Structure

```
h4-cloud-native/
├── .github/workflows/ci-cd.yaml    # CI/CD pipeline
├── backend/
│   ├── main.py                     # FastAPI app + Dapr init
│   ├── routers/todos.py            # CRUD + event publishing
│   ├── services/
│   │   ├── dapr_service.py         # Dapr HTTP client
│   │   └── notification_service.py # Kafka consumer
│   └── metrics/
│       └── prometheus_metrics.py   # Custom metrics
├── frontend/                       # Next.js 14 app
├── docker/
│   ├── backend.Dockerfile          # Multi-stage build
│   ├── frontend.Dockerfile         # Multi-stage build
│   └── notification.Dockerfile     # Lightweight consumer
├── k8s/base/                       # 14 Kubernetes manifests
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml
│   ├── 02-secret.yaml
│   ├── 03-postgresql.yaml          # StatefulSet + PVC
│   ├── 04-backend.yaml             # + Dapr annotations
│   ├── 05-frontend.yaml            # + Dapr annotations
│   ├── 06-redis.yaml
│   ├── 07-dapr-statestore.yaml     # Dapr Component
│   ├── 08-dapr-pubsub.yaml         # Redis pub/sub (legacy)
│   ├── 09-kafka.yaml               # Strimzi KRaft
│   ├── 10-kafka-topics.yaml        # 3 topics
│   ├── 11-dapr-pubsub-kafka.yaml   # Dapr Kafka pub/sub
│   ├── 12-notification-service.yaml # + Dapr annotations
│   └── 13-prometheus.yaml          # + RBAC
├── helm/todo-app/                  # Helm chart
├── scripts/
│   ├── deploy.sh                   # Deployment automation
│   ├── build-images.sh             # Docker build script
│   ├── access-app.sh               # Port-forwarding helper
│   └── verify-cluster.sh           # Cluster health check
├── docs/
│   ├── architecture.md             # Full architecture diagram
│   ├── SESSION-1-DEPLOYMENT.md
│   ├── H4-SESSION-SUMMARY.md
│   ├── session-3-kafka-observability.md
│   └── session-4-cicd-docs.md
└── README.md                       # This file
```

## Hackathon Journey (H0 -> H4)

| Hackathon | Project | Tier | Code Reuse |
|-----------|---------|------|------------|
| H0 | Personal AI CTO | Bronze | -- |
| H1 | Course Companion | Silver | 60% |
| H2 | AI-Powered Todo | Silver | 70% |
| H3 | Advanced Todo (149 tests) | Gold | 85% |
| **H4** | **Cloud-Native Deployment** | **Platinum** | **90%+** |

## Platinum Tier Criteria Met

- [x] Kubernetes deployment with multiple services
- [x] Dapr service mesh with sidecar injection
- [x] Event-driven architecture (Kafka pub/sub)
- [x] Multiple microservices (Backend, Frontend, Notification)
- [x] Persistent storage (PostgreSQL StatefulSet + PVC)
- [x] Observability (Prometheus metrics + scraping)
- [x] CI/CD pipeline (GitHub Actions)
- [x] Comprehensive documentation
- [x] Resource-constrained optimization (6GB cluster)

## Session Documentation

- [Session 1: Kubernetes Setup](docs/SESSION-1-DEPLOYMENT.md)
- [Session 2: Dapr Integration](docs/H4-SESSION-SUMMARY.md)
- [Session 3: Kafka + Observability](docs/session-3-kafka-observability.md)
- [Session 4: CI/CD + Docs](docs/session-4-cicd-docs.md)

## Author

**Asadullah Shafique**
- GitHub: [@asadullah48](https://github.com/asadullah48)
- GIAIC Roll: 00458550
- Program: Panaversity Hackathon II
