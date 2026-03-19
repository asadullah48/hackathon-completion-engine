# H4 Session 3 Part 2: Notification Microservice (Kafka Consumer)

## ROLE
You are an elite hackathon technical lead. Execute precisely, minimize token usage.

## CONTEXT
- H4 Session 3 Part 1 complete: Kafka running, Dapr pub/sub switched to Kafka.
- Project: `/mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/`
- Backend publishes 5 event types to Kafka via Dapr.

## OBJECTIVE
Create a Notification microservice that consumes events from Kafka via Dapr. ~45 min.

---

## TASK 1: Create Notification Service

Create `backend/services/notification_service.py`:
```python
"""Notification Service - Consumes Kafka events via Dapr pub/sub."""
from fastapi import FastAPI, Request
from datetime import datetime
import logging, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("notification-service")
app = FastAPI(title="Todo Notification Service", version="1.0.0")

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "notification-service"}

@app.get("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which Kafka topics to subscribe to."""
    return [
        {"pubsubname": "pubsub", "topic": "todo-events", "route": "/events/todo"},
        {"pubsubname": "pubsub", "topic": "todo-notifications", "route": "/events/notifications"},
    ]

@app.post("/events/todo")
async def handle_todo_event(request: Request):
    try:
        event = await request.json()
        event_data = event.get("data", event)
        event_type = event_data.get("eventType", "unknown")
        logger.info(f"📬 {event_type}: {json.dumps(event_data, indent=2, default=str)}")
        return {"success": True}
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/events/notifications")
async def handle_notification(request: Request):
    event = await request.json()
    logger.info(f"🔔 Notification: {json.dumps(event, indent=2, default=str)}")
    return {"success": True}
```

## TASK 2: Create Dockerfile

Create `docker/notification.Dockerfile`:
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY backend/services/notification_service.py /app/main.py
EXPOSE 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

```bash
cd /mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/
docker build -t todo-notification:v1.0.0 -f docker/notification.Dockerfile .
minikube image load todo-notification:v1.0.0
```

## TASK 3: Deploy to Kubernetes

Create `k8s/base/12-notification-service.yaml`:
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
    spec:
      containers:
      - name: notification
        image: todo-notification:v1.0.0
        imagePullPolicy: Never
        ports:
        - containerPort: 8001
        resources:
          requests: { cpu: 50m, memory: 128Mi }
          limits: { cpu: 200m, memory: 256Mi }
        livenessProbe:
          httpGet: { path: /health, port: 8001 }
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet: { path: /health, port: 8001 }
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: todo-notification
  namespace: todo-app
spec:
  type: ClusterIP
  ports:
  - port: 8001
    targetPort: 8001
  selector:
    app.kubernetes.io/component: notification
    app.kubernetes.io/instance: todo-app
```

```bash
kubectl apply -f k8s/base/12-notification-service.yaml
kubectl wait --for=condition=available deployment/todo-notification -n todo-app --timeout=120s
kubectl get pods -n todo-app -l app.kubernetes.io/component=notification
# Should show 2/2 (app + dapr sidecar)
```

## TASK 4: Test Full Pipeline (Backend → Kafka → Notification)

```bash
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000 &
sleep 3

NOTIF_POD=$(kubectl get pod -n todo-app -l app.kubernetes.io/component=notification -o jsonpath='{.items[0].metadata.name}')

# Create a todo
curl -s -X POST http://localhost:8000/api/todos -H "Content-Type: application/json" \
  -d '{"title":"Full Pipeline Kafka Test","category":"testing","priority":"high"}'

sleep 5

# Check notification service received the event
echo "=== NOTIFICATION SERVICE LOGS ==="
kubectl logs -n todo-app $NOTIF_POD -c notification --tail=15

kill %1 2>/dev/null
```

## DELIVERABLES:
```bash
kubectl get pods -n todo-app
# Notification pod should show 2/2
kubectl logs -n todo-app $NOTIF_POD -c notification --tail=10
kubectl top nodes
```

**When done: Part 2 complete → Start new session for Part 3**
