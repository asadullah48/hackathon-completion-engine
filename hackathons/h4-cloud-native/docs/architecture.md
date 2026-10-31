# H4 Cloud-Native Architecture

## System Architecture

```
+-----------------------------------------------------------------------+
|                    MINIKUBE KUBERNETES CLUSTER                         |
|                    (v1.35.0 | 6GB RAM | 4 CPUs)                       |
|                                                                       |
|  +----------------------------------------------------------------+  |
|  |                    todo-app namespace                           |  |
|  |                                                                 |  |
|  |  +--------------+  +---------------+  +---------------------+  |  |
|  |  |  Frontend    |  |   Backend     |  |  Notification Svc   |  |  |
|  |  |  Next.js 14  |  |   FastAPI     |  |  FastAPI            |  |  |
|  |  |  + Dapr      |  |   + Dapr      |  |  + Dapr             |  |  |
|  |  |  Port: 3000  |  |   Port: 8000  |  |  Port: 8001         |  |  |
|  |  +------+-------+  +-------+-------+  +----------+----------+  |  |
|  |         |                  |                      |             |  |
|  |         |            +-----v-------+              |             |  |
|  |         |            | Dapr Pub/Sub|--------------+             |  |
|  |         |            | (Kafka)     |                            |  |
|  |         |            +-----+-------+                            |  |
|  |         |                  |                                    |  |
|  |  +------v------+  +-------v-------+  +-----------------------+ |  |
|  |  | Redis       |  | PostgreSQL    |  | Prometheus            | |  |
|  |  | State Store |  | StatefulSet   |  | Metrics (4 targets)   | |  |
|  |  | Port: 6379  |  | Port: 5432    |  | Port: 9090            | |  |
|  |  +-------------+  +---------------+  +-----------------------+ |  |
|  +----------------------------------------------------------------+  |
|                                                                       |
|  +----------------------------------------------------------------+  |
|  |                    kafka namespace                              |  |
|  |  +----------------------------------------------------------+  |  |
|  |  |  Strimzi Kafka (KRaft v4.0.0 - No ZooKeeper)             |  |  |
|  |  |  Topics: todo-events(3p), todo-notifications(2p),         |  |  |
|  |  |          todo-analytics(2p)                                |  |  |
|  |  +----------------------------------------------------------+  |  |
|  +----------------------------------------------------------------+  |
|                                                                       |
|  +----------------------------------------------------------------+  |
|  |                    dapr-system namespace                        |  |
|  |  dapr-operator | dapr-sentry | dapr-sidecar-injector |         |  |
|  |  dapr-placement-server                                         |  |
|  +----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

## Event-Driven Flow

```
User Action --> Frontend --> Backend API
                               |
                       Dapr Sidecar (publish)
                               |
                       Kafka (todo-events topic)
                               |
                       Dapr Sidecar (subscribe)
                               |
                       Notification Service
                               |
                       Event Processing + Logging
```

## Technology Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Orchestration | Kubernetes (Minikube) | v1.35.0 |
| Service Mesh | Dapr | v1.x |
| Event Streaming | Apache Kafka (Strimzi KRaft) | v4.0.0 |
| Backend API | Python FastAPI | 3.12 |
| Frontend | Next.js | 14.x |
| Database | PostgreSQL (StatefulSet) | 15-alpine |
| Cache/State | Redis | 7-alpine |
| Monitoring | Prometheus | v2.50.1 |
| CI/CD | GitHub Actions | v4 |
| Containers | Docker (multi-stage) | 24.x |

## Kubernetes Resources (14 manifests)

| File | Resource | Purpose |
|------|----------|---------|
| 00-namespace.yaml | Namespace | todo-app isolation |
| 01-configmap.yaml | ConfigMap | App configuration |
| 02-secret.yaml | Secret | Sensitive credentials |
| 03-postgresql.yaml | StatefulSet + PVC + Service | Persistent database |
| 04-backend.yaml | Deployment + Service | FastAPI backend (Dapr) |
| 05-frontend.yaml | Deployment + Service | Next.js frontend (Dapr) |
| 06-redis.yaml | Deployment + Service | State store + cache |
| 07-dapr-statestore.yaml | Dapr Component | Redis state store |
| 08-dapr-pubsub.yaml | Dapr Component | Redis pub/sub (legacy) |
| 09-kafka.yaml | Kafka + KafkaNodePool | Event streaming |
| 10-kafka-topics.yaml | KafkaTopic (x3) | Event topics |
| 11-dapr-pubsub-kafka.yaml | Dapr Component | Kafka pub/sub |
| 12-notification-service.yaml | Deployment + Service | Event consumer (Dapr) |
| 13-prometheus.yaml | Deployment + ConfigMap + RBAC | Metrics collection |

## Dapr Components

| Component | Type | Backend |
|-----------|------|---------|
| statestore | state.redis | Redis |
| pubsub | pubsub.kafka | Kafka (Strimzi) |

## Events Published

| Event | Topic | Trigger |
|-------|-------|---------|
| todo_created | todo-events | POST /api/todos |
| todo_updated | todo-events | PUT /api/todos/{id} |
| todo_deleted | todo-events | DELETE /api/todos/{id} |
| todo_blocked | todo-events | PATCH (block) |
| todo_flagged | todo-events | PATCH (flag) |

## Prometheus Metrics

| Metric | Type | Labels |
|--------|------|--------|
| http_requests_total | Counter | method, endpoint, status_code |
| http_request_duration_seconds | Histogram | method, endpoint |
| todo_events_published_total | Counter | event_type |
| todo_crud_operations_total | Counter | operation |

## Resource Budget (6GB Cluster)

| Component | CPU Request | Memory Request |
|-----------|------------|----------------|
| Backend (x2) | 200m | 512Mi |
| Frontend (x2) | 200m | 512Mi |
| Notification | 50m | 128Mi |
| PostgreSQL | 100m | 256Mi |
| Redis | 100m | 128Mi |
| Kafka (KRaft) | 250m | 512Mi |
| Prometheus | 100m | 256Mi |
| Dapr sidecars (x3) | ~150m | ~384Mi |
| **Total** | **~1150m** | **~2.7GB** |

Cluster utilization: ~19% CPU, ~44% memory
