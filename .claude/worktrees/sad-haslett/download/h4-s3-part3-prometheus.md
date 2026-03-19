# H4 Session 3 Part 3: Prometheus Metrics + Documentation

## ROLE
You are an elite hackathon technical lead. Execute precisely, minimize token usage.

## CONTEXT
- Parts 1-2 complete: Kafka running, Notification service consuming events.
- Project: `/mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/`
- Backend /metrics currently returns 404. Fix it.

## OBJECTIVE
Add Prometheus metrics to backend + deploy Prometheus server + session docs. ~1 hour.

---

## TASK 1: Add Prometheus Metrics to Backend

Create `backend/metrics/prometheus_metrics.py`:
```python
"""Prometheus metrics for Todo backend."""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
import time, re

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status_code'])
TODO_EVENTS = Counter('todo_events_published_total', 'Events published to Kafka', ['event_type'])
TODO_OPS = Counter('todo_crud_operations_total', 'CRUD operations', ['operation'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Request duration', ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        start = time.time()
        response = await call_next(request)
        path = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '{id}', request.url.path)
        REQUEST_COUNT.labels(method=request.method, endpoint=path, status_code=response.status_code).inc()
        REQUEST_DURATION.labels(method=request.method, endpoint=path).observe(time.time() - start)
        return response

def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

**Integrate into main.py** — Add:
```python
from backend.metrics.prometheus_metrics import PrometheusMiddleware, metrics_endpoint
app.add_middleware(PrometheusMiddleware)

@app.get("/metrics")
async def get_metrics():
    return metrics_endpoint()
```

**Add `prometheus_client>=0.20.0` to requirements.txt.**

Also instrument event publishing — wherever events are published, add:
```python
from backend.metrics.prometheus_metrics import TODO_EVENTS, TODO_OPS
TODO_EVENTS.labels(event_type="todo_created").inc()
TODO_OPS.labels(operation="create").inc()
```

## TASK 2: Rebuild Backend v1.2.0

```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/
docker build -t todo-backend:v1.2.0 -f docker/backend.Dockerfile .
minikube image load todo-backend:v1.2.0
kubectl set image deployment/todo-app-backend -n todo-app backend=todo-backend:v1.2.0
kubectl rollout status deployment/todo-app-backend -n todo-app --timeout=120s

# Test /metrics
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000 &
sleep 3
curl -s http://localhost:8000/metrics | head -20
kill %1 2>/dev/null
```

## TASK 3: Deploy Prometheus

Create `k8s/base/13-prometheus.yaml`:
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
    scrape_configs:
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
      - job_name: 'dapr-sidecars'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names: ['todo-app']
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_dapr_io_enabled]
            regex: "true"
            action: keep
          - source_labels: [__meta_kubernetes_pod_ip, __meta_kubernetes_pod_annotation_dapr_io_metrics_port]
            separator: ":"
            target_label: __address__
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: todo-app
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
        args: ['--config.file=/etc/prometheus/prometheus.yml', '--storage.tsdb.retention.time=24h']
        ports:
        - containerPort: 9090
        resources:
          requests: { cpu: 100m, memory: 256Mi }
          limits: { cpu: 300m, memory: 512Mi }
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: data
          mountPath: /prometheus
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
spec:
  type: ClusterIP
  ports:
  - port: 9090
    targetPort: 9090
  selector:
    app: prometheus
```

```bash
kubectl apply -f k8s/base/13-prometheus.yaml
kubectl wait --for=condition=available deployment/prometheus -n todo-app --timeout=120s
```

## TASK 4: Verify Prometheus

```bash
kubectl port-forward -n todo-app svc/prometheus 9090:9090 &
sleep 3
curl -s "http://localhost:9090/api/v1/targets" | python3 -c "
import sys,json
targets=json.load(sys.stdin)['data']['activeTargets']
for t in targets:
    print(f\"{t['labels'].get('job','?')} - {t['health']}\")
"
kill %1 2>/dev/null
```

## TASK 5: Create Session 3 Documentation

Create `docs/session-3-kafka-observability.md` documenting:
- Kafka deployment (Strimzi KRaft single-node)
- Redis → Kafka Dapr pub/sub switch (zero code changes)
- Notification microservice as Kafka consumer
- Prometheus metrics and scraping config
- All verification commands

## FINAL DELIVERABLES:
```bash
echo "=== FULL H4 SESSION 3 STATUS ==="
kubectl get kafka -n kafka
kubectl get kafkatopics -n kafka
kubectl get components -n todo-app
kubectl get pods -n todo-app
kubectl get pods -n kafka
kubectl top nodes
```

**Session 3 COMPLETE → Ready for Session 4 (CI/CD + Platinum Submission)**
