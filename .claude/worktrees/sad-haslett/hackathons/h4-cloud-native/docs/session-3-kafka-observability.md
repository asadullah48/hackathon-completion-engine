# Session 3: Kafka Event Streaming + Observability

## Overview
Session 3 added production-grade event streaming via Apache Kafka and observability via Prometheus metrics. The Dapr pub/sub component was switched from Redis to Kafka with zero application code changes.

## Part 1: Kafka Deployment (Strimzi KRaft)

### What Was Deployed
- **Strimzi Kafka Operator** v0.45.0 via Helm (namespace: `kafka`)
- **KRaft single-node Kafka** cluster (no ZooKeeper dependency)
  - 1 broker, 1 controller in combined mode
  - 2Gi persistent storage, 1Gi JVM heap
- **3 Kafka topics** created:
  - `todo-events` (3 partitions, 1 replica) - main event stream
  - `todo-notifications` (3 partitions, 1 replica) - notification routing
  - `todo-audit` (3 partitions, 1 replica) - compliance audit trail

### Verification
```bash
kubectl get kafka -n kafka
kubectl get kafkatopics -n kafka
```

## Part 2: Redis to Kafka Pub/Sub Switch

### Dapr Component Update
- File: `k8s/base/11-dapr-pubsub-kafka.yaml`
- Replaced the Redis-backed `pubsub` Dapr component with Kafka-backed version
- **Zero application code changes** required — Dapr abstraction handled the swap
- Backend publishes events via `dapr.publish("pubsub", "todo-events", data)` unchanged

### Key Configuration
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
spec:
  type: pubsub.kafka
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app"
    - name: authType
      value: "none"
```

## Part 3: Notification Microservice

### Architecture
- Independent Python/FastAPI microservice consuming Kafka events via Dapr
- File: `k8s/base/12-notification-service.yaml`
- Docker image: `todo-notification:v1.0.0`
- Subscribes to `todo-events` topic via Dapr pub/sub

### Event Types Handled
| Event | Action |
|-------|--------|
| `todo_created` | Log new todo notification |
| `todo_updated` | Log update notification |
| `todo_deleted` | Log deletion notification |
| `todo_flagged` | Log constitutional flag alert |
| `todo_blocked` | Log constitutional block alert |

### Verification
```bash
kubectl logs -n todo-app deploy/todo-notification -c notification --tail=20
```

## Part 4: Prometheus Metrics + Observability

### Backend Metrics (v1.5.0)
Added `prometheus_client` instrumentation to the backend:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `http_requests_total` | Counter | method, endpoint, status_code | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency distribution |
| `todo_events_published_total` | Counter | event_type | Kafka events published |
| `todo_crud_operations_total` | Counter | operation | CRUD operation counts |

- Middleware auto-instruments all HTTP requests (excluding `/metrics`)
- UUID path segments normalized to `{id}` for cardinality control
- Histogram buckets: 10ms, 50ms, 100ms, 250ms, 500ms, 1s, 2.5s, 5s

### Prometheus Server
- File: `k8s/base/13-prometheus.yaml`
- Image: `prom/prometheus:v2.50.1`
- 24h retention, 256Mi-512Mi memory
- RBAC: ServiceAccount + ClusterRole for pod discovery

### Scrape Targets
| Job | Target | Port | Discovery |
|-----|--------|------|-----------|
| `todo-backend` | Backend pods | 8000 | `app.kubernetes.io/component=backend` label |
| `todo-notification` | Notification pods | 8001 | `app.kubernetes.io/component=notification` label |
| `dapr-sidecars` | Dapr sidecar metrics | Varies | `dapr.io/enabled=true` annotation |

### Verification
```bash
# Check Prometheus targets
kubectl exec -n todo-app deploy/prometheus -- wget -qO- http://localhost:9090/api/v1/targets

# Check backend metrics
kubectl exec -n todo-app deploy/todo-app-backend -c backend -- \
  python3 -c "from urllib.request import urlopen; print(urlopen('http://localhost:8000/metrics').read().decode()[:500])"
```

## Architecture After Session 3

```
                    ┌─────────────────────────────────┐
                    │         Prometheus               │
                    │   (scrapes /metrics endpoints)   │
                    └────┬──────────┬─────────────────┘
                         │          │
              scrape     │          │  scrape
                         ▼          ▼
┌──────────┐    ┌──────────────┐  ┌───────────────────┐
│ Frontend │───▶│   Backend    │  │  Notification Svc  │
│ (Next.js)│    │  (FastAPI)   │  │    (FastAPI)       │
└──────────┘    └──────┬───────┘  └────────▲──────────┘
                       │ Dapr pub/sub       │ Dapr sub
                       ▼                    │
                ┌──────────────┐            │
                │    Kafka     │────────────┘
                │  (Strimzi)   │
                └──────────────┘
```

## Docker Image Versions
| Image | Version | Changes |
|-------|---------|---------|
| `todo-backend` | v1.5.0 | + Prometheus metrics, middleware, CRUD instrumentation |
| `todo-notification` | v1.0.0 | Kafka consumer via Dapr subscription |
| `todo-frontend` | v1.0.0 | Unchanged |

## Files Changed/Added
- `backend/metrics/__init__.py` - Metrics module init
- `backend/metrics/prometheus_metrics.py` - Counters, histogram, middleware
- `backend/main.py` - Added PrometheusMiddleware + /metrics endpoint
- `backend/requirements.txt` - Added prometheus_client>=0.20.0
- `backend/routers/todos.py` - CRUD operation counter instrumentation
- `backend/services/dapr_service.py` - Event publish counter instrumentation
- `k8s/base/13-prometheus.yaml` - Prometheus server deployment
