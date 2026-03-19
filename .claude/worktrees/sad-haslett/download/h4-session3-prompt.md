# IMPLEMENTATION: H4 Session 3 - Kafka Event Streaming + Observability Stack

## ROLE
You are an elite hackathon technical lead with deep expertise in full-stack development, AI systems, and hackathon-winning strategies. Your mission is to architect and execute a perfect scoring project while ruthlessly optimizing API token usage.

## CONTEXT
- ✅ H4 Session 1 Complete - Kubernetes cluster + containerized app (15+ manifests)
- ✅ H4 Session 2 Complete - Dapr service mesh + event-driven architecture
- Minikube cluster: v1.35.0 (6GB RAM, 4 CPUs) — RESOURCE-CONSTRAINED
- Backend v1.1.0: 2/2 Running with Dapr sidecars, 5 event types publishing
- Frontend: 2/2 Running with Dapr sidecars
- PostgreSQL: 1/1 StatefulSet with persistent storage
- Redis: 1/1 Running (current Dapr state store + pub/sub)
- Dapr: Fully operational (statestore + pubsub components in todo-app namespace)

## ENVIRONMENT STATUS
```
Cluster: todo-app namespace
Backend: todo-app-backend (2 replicas, Dapr app-id: backend)
Frontend: todo-app-frontend (2 replicas, Dapr app-id: frontend)
Database: todo-app-postgresql:5432 (StatefulSet)
Redis: redis:6379 (Dapr state + pub/sub)
Dapr: v1.x running in dapr-system namespace
```

## PROJECT PATH
`/mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/`

## OBJECTIVE
Replace Redis pub/sub with Kafka for production-grade event streaming + add full observability stack (3-4 hours)

## ⚠️ CRITICAL RESOURCE CONSTRAINTS
Minikube has only 6GB RAM. Current pods use ~3.5GB. We have ~2.5GB headroom.
- Use SINGLE-NODE Kafka (Strimzi KRaft mode, NO ZooKeeper)
- Use lightweight Prometheus (no Thanos, no HA)
- Skip Grafana if memory is tight (Prometheus UI is sufficient for hackathon)
- Monitor `kubectl top nodes` throughout — if memory > 85%, scale down replicas

---

## PHASE A: KAFKA DEPLOYMENT (Strimzi Operator)

### TASK 3.1: Install Strimzi Kafka Operator

```bash
# Create kafka namespace
kubectl create namespace kafka

# Install Strimzi operator (latest stable)
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
echo "⏳ Waiting for Strimzi operator..."
kubectl wait --for=condition=available deployment/strimzi-cluster-operator -n kafka --timeout=300s

# Verify operator is running
kubectl get pods -n kafka
# Should see: strimzi-cluster-operator-xxx Running

echo "✅ Strimzi operator installed"
```

**⚠️ CHECKPOINT**: Run `kubectl top nodes` — if memory usage > 80%, reduce backend/frontend to 1 replica each before proceeding:
```bash
kubectl scale deployment todo-app-backend -n todo-app --replicas=1
kubectl scale deployment todo-app-frontend -n todo-app --replicas=1
```

---

### TASK 3.2: Deploy Single-Node Kafka (KRaft Mode — No ZooKeeper)

Create: `k8s/base/09-kafka.yaml`

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: combined
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  replicas: 1
  roles:
    - controller
    - broker
  storage:
    type: jbod
    volumes:
      - id: 0
        type: persistent-claim
        size: 5Gi
        deleteClaim: true
        class: standard
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
---
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
  annotations:
    strimzi.io/node-pools: enabled
    strimzi.io/kraft: enabled
spec:
  kafka:
    version: 3.7.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: external
        port: 9094
        type: nodeport
        tls: false
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      num.partitions: 3
      log.retention.hours: 24
      log.segment.bytes: 1073741824
  entityOperator:
    topicOperator:
      resources:
        requests:
          cpu: 50m
          memory: 128Mi
        limits:
          cpu: 200m
          memory: 256Mi
    userOperator:
      resources:
        requests:
          cpu: 50m
          memory: 128Mi
        limits:
          cpu: 200m
          memory: 256Mi
```

Deploy Kafka:
```bash
kubectl apply -f k8s/base/09-kafka.yaml

# Wait for Kafka to be ready (this takes 2-5 minutes)
echo "⏳ Waiting for Kafka cluster to be ready..."
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka

# Verify Kafka pods
kubectl get pods -n kafka

# Should see:
# - strimzi-cluster-operator-xxx Running
# - todo-kafka-combined-0 Running (1/1)
# - todo-kafka-entity-operator-xxx Running

# Get Kafka bootstrap address
KAFKA_BOOTSTRAP=$(kubectl get kafka todo-kafka -n kafka -o jsonpath='{.status.listeners[?(@.name=="plain")].bootstrapServers}')
echo "Kafka Bootstrap: $KAFKA_BOOTSTRAP"

echo "✅ Kafka deployed (KRaft single-node)"
```

---

### TASK 3.3: Create Kafka Topics

Create: `k8s/base/10-kafka-topics.yaml`

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 86400000
    cleanup.policy: delete
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-notifications
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 2
  replicas: 1
  config:
    retention.ms: 86400000
    cleanup.policy: delete
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: todo-analytics
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 2
  replicas: 1
  config:
    retention.ms: 172800000
    cleanup.policy: delete
```

Apply topics:
```bash
kubectl apply -f k8s/base/10-kafka-topics.yaml

# Verify topics created
kubectl get kafkatopics -n kafka

# Should see:
# - todo-events (3 partitions)
# - todo-notifications (2 partitions)
# - todo-analytics (2 partitions)

echo "✅ Kafka topics created"
```

---

## PHASE B: SWITCH DAPR PUB/SUB FROM REDIS TO KAFKA

### TASK 3.4: Create Kafka Dapr Pub/Sub Component

Create: `k8s/base/11-dapr-pubsub-kafka.yaml`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
  - name: consumerGroup
    value: "todo-backend-group"
  - name: authType
    value: "none"
  - name: maxMessageBytes
    value: "1048576"
  - name: consumeRetryInterval
    value: "200ms"
  - name: version
    value: "3.7.0"
  - name: initialOffset
    value: "newest"
  - name: disableTls
    value: "true"
```

**⚠️ IMPORTANT**: This replaces the existing Redis pub/sub component (same name `pubsub`). Dapr will seamlessly switch the backend's event publishing from Redis to Kafka — zero code changes needed in the application!

Apply and restart:
```bash
# Delete old Redis pub/sub component
kubectl delete component pubsub -n todo-app 2>/dev/null

# Apply new Kafka pub/sub component
kubectl apply -f k8s/base/11-dapr-pubsub-kafka.yaml

# Restart pods to pick up new Dapr component
kubectl rollout restart deployment/todo-app-backend -n todo-app
kubectl rollout restart deployment/todo-app-frontend -n todo-app

# Wait for rollout
kubectl rollout status deployment/todo-app-backend -n todo-app --timeout=120s
kubectl rollout status deployment/todo-app-frontend -n todo-app --timeout=120s

# Verify pods running with Dapr sidecars
kubectl get pods -n todo-app

# Check Dapr sidecar picked up Kafka component
BACKEND_POD=$(kubectl get pod -n todo-app -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n todo-app $BACKEND_POD -c daprd | grep -i "kafka\|pubsub" | tail -10

echo "✅ Dapr pub/sub switched to Kafka"
```

---

### TASK 3.5: Test Kafka Event Flow End-to-End

```bash
# Port-forward backend
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000 &
sleep 3

# Create a todo (should publish to Kafka via Dapr)
echo "📤 Publishing test event via todo creation..."
curl -s -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Kafka Event Flow",
    "category": "work",
    "priority": "high"
  }' | python3 -m json.tool

# Check backend logs for successful publish
echo ""
echo "=== BACKEND EVENT LOGS ==="
kubectl logs -n todo-app $BACKEND_POD -c backend --tail=20 | grep -i "publish\|event"

# Check Dapr sidecar logs for Kafka delivery
echo ""
echo "=== DAPR SIDECAR KAFKA LOGS ==="
kubectl logs -n todo-app $BACKEND_POD -c daprd --tail=30 | grep -i "kafka\|publish\|topic"

# Verify message landed in Kafka topic using Strimzi kafka-console-consumer
echo ""
echo "=== KAFKA TOPIC MESSAGES ==="
kubectl run kafka-consumer -n kafka --rm -i --restart=Never \
  --image=quay.io/strimzi/kafka:0.40.0-kafka-3.7.0 \
  -- bin/kafka-console-consumer.sh \
    --bootstrap-server todo-kafka-kafka-bootstrap:9092 \
    --topic todo-events \
    --from-beginning \
    --max-messages 5 \
    --timeout-ms 10000

# Kill port-forward
kill %1 2>/dev/null

echo "✅ Kafka event flow verified end-to-end"
```

---

## PHASE C: EVENT CONSUMER MICROSERVICE

### TASK 3.6: Create Notification Service (Kafka Consumer)

Create: `backend/services/notification_service.py`

```python
"""
Notification Service - Consumes events from Kafka via Dapr pub/sub.
Runs as a separate microservice that handles event-driven notifications.
"""
from fastapi import FastAPI, Request
from datetime import datetime
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")

app = FastAPI(title="Todo Notification Service", version="1.0.0")


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service", "timestamp": datetime.utcnow().isoformat()}


@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr programmatic subscription endpoint.
    Tells Dapr which topics this service subscribes to.
    """
    subscriptions = [
        {
            "pubsubname": "pubsub",
            "topic": "todo-events",
            "route": "/events/todo",
            "metadata": {
                "rawPayload": "false"
            }
        },
        {
            "pubsubname": "pubsub",
            "topic": "todo-notifications",
            "route": "/events/notifications",
            "metadata": {
                "rawPayload": "false"
            }
        }
    ]
    logger.info(f"📋 Registered {len(subscriptions)} subscriptions")
    return subscriptions


@app.post("/events/todo")
async def handle_todo_event(request: Request):
    """Handle todo events from Kafka."""
    try:
        event = await request.json()
        event_data = event.get("data", event)
        event_type = event_data.get("eventType", "unknown")

        logger.info(f"📬 Received todo event: {event_type}")
        logger.info(f"   Data: {json.dumps(event_data, indent=2, default=str)}")

        # Route by event type
        if event_type == "todo_created":
            logger.info(f"🆕 New todo: {event_data.get('data', {}).get('title', 'N/A')}")
        elif event_type == "todo_completed":
            logger.info(f"✅ Todo completed: {event_data.get('data', {}).get('todoId', 'N/A')}")
        elif event_type == "todo_deleted":
            logger.info(f"🗑️ Todo deleted: {event_data.get('data', {}).get('todoId', 'N/A')}")
        elif event_type == "todo_updated":
            logger.info(f"📝 Todo updated: {event_data.get('data', {}).get('todoId', 'N/A')}")
        elif event_type == "todo_flagged":
            logger.info(f"🚩 Todo flagged: {event_data.get('data', {}).get('todoId', 'N/A')}")

        return {"success": True}
    except Exception as e:
        logger.error(f"❌ Error handling todo event: {e}")
        return {"success": False, "error": str(e)}


@app.post("/events/notifications")
async def handle_notification_event(request: Request):
    """Handle notification events."""
    try:
        event = await request.json()
        logger.info(f"🔔 Notification event: {json.dumps(event, indent=2, default=str)}")
        return {"success": True}
    except Exception as e:
        logger.error(f"❌ Error handling notification: {e}")
        return {"success": False, "error": str(e)}
```

---

### TASK 3.7: Create Notification Service Dockerfile

Create: `docker/notification.Dockerfile`

```dockerfile
FROM python:3.12-slim AS base

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn

# Copy service
COPY backend/services/notification_service.py /app/main.py

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"]
```

Build and load:
```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/

# Build notification service image
docker build -t todo-notification:v1.0.0 -f docker/notification.Dockerfile .

# Load into Minikube
minikube image load todo-notification:v1.0.0

echo "✅ Notification service image built"
```

---

### TASK 3.8: Deploy Notification Service to Kubernetes

Create: `k8s/base/12-notification-service.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-notification
  namespace: todo-app
  labels:
    app.kubernetes.io/component: notification
    app.kubernetes.io/instance: todo-app
    app.kubernetes.io/name: todo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/component: notification
      app.kubernetes.io/instance: todo-app
  template:
    metadata:
      labels:
        app.kubernetes.io/component: notification
        app.kubernetes.io/instance: todo-app
        app.kubernetes.io/name: todo-app
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "notification-service"
        dapr.io/app-port: "8001"
        dapr.io/log-level: "info"
        dapr.io/enable-metrics: "true"
        dapr.io/metrics-port: "9091"
    spec:
      containers:
      - name: notification
        image: todo-notification:v1.0.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8001
          name: http
        resources:
          requests:
            cpu: 50m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: todo-notification
  namespace: todo-app
  labels:
    app.kubernetes.io/component: notification
spec:
  type: ClusterIP
  ports:
  - port: 8001
    targetPort: 8001
    protocol: TCP
    name: http
  selector:
    app.kubernetes.io/component: notification
    app.kubernetes.io/instance: todo-app
```

Deploy:
```bash
kubectl apply -f k8s/base/12-notification-service.yaml

# Wait for notification service
kubectl wait --for=condition=available deployment/todo-notification -n todo-app --timeout=120s

# Verify it has Dapr sidecar (should show 2/2)
kubectl get pods -n todo-app -l app.kubernetes.io/component=notification

echo "✅ Notification service deployed with Dapr sidecar"
```

---

### TASK 3.9: Test Full Event Pipeline (Backend → Kafka → Notification Service)

```bash
# Port-forward backend
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000 &
sleep 3

# Get notification pod name
NOTIF_POD=$(kubectl get pod -n todo-app -l app.kubernetes.io/component=notification -o jsonpath='{.items[0].metadata.name}')

# Start watching notification service logs in background
echo "👀 Watching notification service logs..."
kubectl logs -n todo-app $NOTIF_POD -c notification -f &
LOG_PID=$!
sleep 2

# Create a todo — should flow: Backend → Dapr → Kafka → Dapr → Notification Service
echo ""
echo "📤 Creating todo to trigger full event pipeline..."
curl -s -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Full Pipeline Test - Kafka to Notification",
    "category": "testing",
    "priority": "high"
  }' | python3 -m json.tool

# Wait for event propagation
sleep 5

# Stop log watching
kill $LOG_PID 2>/dev/null
kill %1 2>/dev/null

echo ""
echo "=== NOTIFICATION SERVICE EVENT LOG ==="
kubectl logs -n todo-app $NOTIF_POD -c notification --tail=20

echo ""
echo "✅ Full event pipeline tested: Backend → Kafka → Notification Service"
```

---

## PHASE D: PROMETHEUS OBSERVABILITY

### TASK 3.10: Add Prometheus Metrics to Backend

Update the backend to expose `/metrics` endpoint.

Create: `backend/metrics/prometheus_metrics.py`

```python
"""
Prometheus metrics for the Todo backend.
Lightweight implementation using prometheus_client.
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Counters
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

TODO_EVENTS_PUBLISHED = Counter(
    'todo_events_published_total',
    'Total todo events published to Kafka',
    ['event_type']
)

TODO_CRUD_OPERATIONS = Counter(
    'todo_crud_operations_total',
    'Total CRUD operations on todos',
    ['operation']
)

# Histograms
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Gauges
ACTIVE_TODOS = Gauge(
    'active_todos_count',
    'Current number of active (non-completed) todos'
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track request metrics."""

    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        path = request.url.path

        # Normalize path (remove UUIDs/IDs)
        normalized = self._normalize_path(path)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        REQUEST_COUNT.labels(
            method=method,
            endpoint=normalized,
            status_code=response.status_code
        ).inc()

        REQUEST_DURATION.labels(
            method=method,
            endpoint=normalized
        ).observe(duration)

        return response

    @staticmethod
    def _normalize_path(path: str) -> str:
        """Replace UUIDs and numeric IDs with placeholders."""
        import re
        # Replace UUIDs
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}', path
        )
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        return path


def metrics_endpoint():
    """Generate Prometheus metrics response."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

**Integration with main.py** — Add these lines:

```python
# In main.py, add:
from backend.metrics.prometheus_metrics import PrometheusMiddleware, metrics_endpoint

# Add middleware
app.add_middleware(PrometheusMiddleware)

# Add metrics endpoint
@app.get("/metrics")
async def get_metrics():
    return metrics_endpoint()
```

**Integration with event publishing** — In dapr_service.py or wherever events are published, add:

```python
from backend.metrics.prometheus_metrics import TODO_EVENTS_PUBLISHED, TODO_CRUD_OPERATIONS

# After successful event publish:
TODO_EVENTS_PUBLISHED.labels(event_type="todo_created").inc()

# After CRUD operations:
TODO_CRUD_OPERATIONS.labels(operation="create").inc()
```

---

### TASK 3.11: Rebuild Backend with Metrics

```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/

# Add prometheus_client to requirements
# (Ensure requirements.txt includes: prometheus_client>=0.20.0)

# Rebuild backend
docker build -t todo-backend:v1.2.0 -f docker/backend.Dockerfile .

# Load into Minikube
minikube image load todo-backend:v1.2.0

# Update deployment image
kubectl set image deployment/todo-app-backend -n todo-app backend=todo-backend:v1.2.0

# Wait for rollout
kubectl rollout status deployment/todo-app-backend -n todo-app --timeout=120s

# Verify metrics endpoint works
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000 &
sleep 3
echo "=== PROMETHEUS METRICS ==="
curl -s http://localhost:8000/metrics | head -30
kill %1 2>/dev/null

echo "✅ Backend v1.2.0 deployed with Prometheus metrics"
```

---

### TASK 3.12: Deploy Prometheus Server

Create: `k8s/base/13-prometheus.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: todo-app
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s

    scrape_configs:
      # Backend application metrics
      - job_name: 'todo-backend'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['todo-app']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_component]
            regex: backend
            action: keep
          - source_labels: [__meta_kubernetes_pod_ip]
            target_label: __address__
            replacement: $1:8000

      # Notification service metrics
      - job_name: 'todo-notification'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['todo-app']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_component]
            regex: notification
            action: keep
          - source_labels: [__meta_kubernetes_pod_ip]
            target_label: __address__
            replacement: $1:8001

      # Dapr sidecar metrics
      - job_name: 'dapr-sidecars'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['todo-app']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
            regex: "true"
            action: keep
          - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_metrics_port]
            regex: (.+)
            action: keep
          - source_labels: [__meta_kubernetes_pod_ip, __meta_kubernetes_pod_annotation_dapr_io_metrics_port]
            target_label: __address__
            separator: ":"
            replacement: $1:$2
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus-todo-app
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus-todo-app
subjects:
  - kind: ServiceAccount
    name: prometheus
    namespace: todo-app
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus-todo-app
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: todo-app
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: todo-app
  labels:
    app: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:v2.50.1
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=24h'
          - '--web.enable-lifecycle'
        ports:
        - containerPort: 9090
          name: http
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 300m
            memory: 512Mi
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: data
          mountPath: /prometheus
        livenessProbe:
          httpGet:
            path: /-/healthy
            port: 9090
          initialDelaySeconds: 30
          periodSeconds: 15
        readinessProbe:
          httpGet:
            path: /-/ready
            port: 9090
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: data
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: todo-app
  labels:
    app: prometheus
spec:
  type: ClusterIP
  ports:
  - port: 9090
    targetPort: 9090
    protocol: TCP
    name: http
  selector:
    app: prometheus
```

Deploy Prometheus:
```bash
kubectl apply -f k8s/base/13-prometheus.yaml

# Wait for Prometheus
kubectl wait --for=condition=available deployment/prometheus -n todo-app --timeout=120s

# Verify Prometheus is running
kubectl get pods -n todo-app -l app=prometheus

echo "✅ Prometheus deployed"
```

---

### TASK 3.13: Verify Prometheus Scraping

```bash
# Port-forward Prometheus UI
kubectl port-forward -n todo-app svc/prometheus 9090:9090 &
sleep 3

# Check targets are being scraped
echo "=== PROMETHEUS TARGETS ==="
curl -s http://localhost:9090/api/v1/targets | python3 -m json.tool | grep -E '"job"|"health"' | head -20

# Query some metrics
echo ""
echo "=== HTTP REQUEST COUNT ==="
curl -s "http://localhost:9090/api/v1/query?query=http_requests_total" | python3 -m json.tool | head -20

echo ""
echo "=== TODO EVENTS PUBLISHED ==="
curl -s "http://localhost:9090/api/v1/query?query=todo_events_published_total" | python3 -m json.tool | head -20

echo ""
echo "=== DAPR SIDECAR METRICS ==="
curl -s "http://localhost:9090/api/v1/query?query=dapr_http_server_request_count" | python3 -m json.tool | head -20

kill %1 2>/dev/null

echo "✅ Prometheus scraping verified"
```

---

## PHASE E: RESOURCE CHECK + MEMORY GUARD

### TASK 3.14: Memory Status Check

```bash
echo "=============================="
echo "   CLUSTER RESOURCE STATUS    "
echo "=============================="

# Node resources
echo ""
echo "=== NODE MEMORY ==="
kubectl top nodes 2>/dev/null || echo "Metrics server may need a moment..."

# Pod resources by namespace
echo ""
echo "=== TODO-APP PODS ==="
kubectl top pods -n todo-app 2>/dev/null || echo "Waiting for metrics..."

echo ""
echo "=== KAFKA PODS ==="
kubectl top pods -n kafka 2>/dev/null || echo "Waiting for metrics..."

echo ""
echo "=== DAPR SYSTEM PODS ==="
kubectl top pods -n dapr-system 2>/dev/null || echo "Waiting for metrics..."

# Pod count summary
echo ""
echo "=== ALL PODS SUMMARY ==="
echo "todo-app namespace:"
kubectl get pods -n todo-app --no-headers | wc -l
echo "kafka namespace:"
kubectl get pods -n kafka --no-headers | wc -l
echo "dapr-system namespace:"
kubectl get pods -n dapr-system --no-headers | wc -l

echo ""
echo "=============================="
```

**⚠️ DECISION POINT**: If memory > 90%:
- Skip Grafana (Prometheus UI is sufficient)
- Reduce backend to 1 replica
- Reduce frontend to 1 replica

If memory < 80%: Proceed to optional Grafana deployment.

---

## PHASE F: SESSION 3 DOCUMENTATION

### TASK 3.15: Create Session 3 Documentation

Create: `docs/session-3-kafka-observability.md`

```markdown
# H4 Session 3: Kafka Event Streaming + Observability

## Summary
Replaced Redis pub/sub with Apache Kafka (Strimzi) for production-grade event streaming.
Added Prometheus metrics and a dedicated Notification microservice as Kafka consumer.

## Architecture

```
Backend (Dapr) → Kafka → Notification Service (Dapr)
    ↓                         ↓
Prometheus ←── scrapes ──→ Metrics
```

## Components Deployed

### Kafka (Strimzi)
- **Operator**: strimzi-cluster-operator
- **Broker**: todo-kafka (KRaft mode, single-node, no ZooKeeper)
- **Topics**: todo-events (3p), todo-notifications (2p), todo-analytics (2p)

### Dapr Pub/Sub (Kafka)
- Replaced Redis pub/sub with Kafka-backed Dapr component
- Zero application code changes — Dapr abstraction handled the switch
- Events: todo_created, todo_updated, todo_deleted, todo_blocked, todo_flagged

### Notification Service
- FastAPI microservice consuming events from Kafka via Dapr
- Dapr sidecar for automatic subscription management
- Routes events by type for processing

### Prometheus
- Scrapes backend, notification service, and Dapr sidecars
- Custom metrics: http_requests_total, todo_events_published_total, todo_crud_operations_total
- 24h retention, lightweight deployment

## Event Flow
1. User creates/updates/deletes todo via API
2. Backend publishes event to Dapr pub/sub
3. Dapr routes event to Kafka (todo-events topic)
4. Kafka stores event durably (24h retention)
5. Dapr delivers event to Notification Service subscriber
6. Notification Service processes event by type
7. Prometheus scrapes metrics from all services

## Key Achievement
**Redis → Kafka migration with ZERO code changes** — Dapr's pub/sub abstraction
made the infrastructure swap transparent to the application layer.

## Verification Commands

```bash
# Kafka status
kubectl get kafka -n kafka
kubectl get kafkatopics -n kafka

# All pods healthy
kubectl get pods -n todo-app
kubectl get pods -n kafka

# Prometheus targets
kubectl port-forward svc/prometheus 9090:9090 -n todo-app
# Visit: http://localhost:9090/targets

# Event flow test
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app
curl -X POST http://localhost:8000/api/todos -H "Content-Type: application/json" -d '{"title":"test"}'
kubectl logs -n todo-app <notification-pod> -c notification
```

## Next Steps
- Session 4: CI/CD Pipeline + Final Polish
- Bonus: Grafana dashboards (if resources allow)
- Bonus: Distributed tracing with Jaeger
```

---

## DELIVERABLES CHECKLIST

Show me these outputs to confirm Session 3 complete:

### 1. ✅ Kafka cluster running
```bash
kubectl get kafka -n kafka
kubectl get pods -n kafka
```

### 2. ✅ Kafka topics created
```bash
kubectl get kafkatopics -n kafka
```

### 3. ✅ Dapr pub/sub switched to Kafka
```bash
kubectl get components -n todo-app
kubectl describe component pubsub -n todo-app | grep -A5 "Spec"
```

### 4. ✅ Notification service consuming events (2/2 with Dapr)
```bash
kubectl get pods -n todo-app -l app.kubernetes.io/component=notification
```

### 5. ✅ Full event pipeline working
```bash
# Create todo → check notification service logs for received event
```

### 6. ✅ Prometheus scraping metrics
```bash
kubectl port-forward svc/prometheus 9090:9090 -n todo-app &
curl -s "http://localhost:9090/api/v1/targets" | python3 -c "import sys,json; targets=json.load(sys.stdin)['data']['activeTargets']; [print(f'{t[\"labels\"].get(\"job\",\"?\")} - {t[\"health\"]}') for t in targets]"
```

### 7. ✅ Backend /metrics endpoint live
```bash
kubectl port-forward svc/todo-app-backend 8000:8000 -n todo-app &
curl -s http://localhost:8000/metrics | head -20
```

### 8. ✅ Cluster resource status (memory < 90%)
```bash
kubectl top nodes
```

## VALIDATION CRITERIA
- [ ] Strimzi Kafka broker Running (KRaft, single-node) ✅
- [ ] 3 Kafka topics created ✅
- [ ] Dapr pub/sub component type = pubsub.kafka ✅
- [ ] Backend events publishing to Kafka ✅
- [ ] Notification service consuming from Kafka ✅
- [ ] Prometheus scraping all targets ✅
- [ ] /metrics endpoint returning Prometheus data ✅
- [ ] Cluster memory < 90% ✅
- [ ] No CrashLoopBackOff pods ✅

---

**When complete: H4 SESSION 3 DONE! → Ready for Session 4 (CI/CD + Final Documentation + Platinum Submission)**

---

END OF SESSION 3 PROMPT
