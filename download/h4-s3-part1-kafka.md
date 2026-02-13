# H4 Session 3 Part 1: Kafka Deployment + Switch from Redis

## ROLE
You are an elite hackathon technical lead. Execute precisely, minimize token usage.

## CONTEXT
- H4 Sessions 1-2 complete. All pods healthy with Dapr sidecars.
- Minikube: 6GB RAM (only ~2.5GB headroom). BE MEMORY-CONSCIOUS.
- Project: `/mnt/d/Personal-AI-Employee/hackathons/h4-cloud-native/`
- Current Dapr pub/sub: Redis. Target: Kafka.

## OBJECTIVE
Deploy Kafka (Strimzi) + switch Dapr pub/sub from Redis to Kafka. ~1 hour.

---

## TASK 1: Pre-flight + Memory Check
```bash
kubectl top nodes 2>/dev/null
kubectl get pods -n todo-app
# If memory > 80%, scale to 1 replica each:
# kubectl scale deployment todo-app-backend -n todo-app --replicas=1
# kubectl scale deployment todo-app-frontend -n todo-app --replicas=1
```

## TASK 2: Install Strimzi Operator
```bash
kubectl create namespace kafka
kubectl apply -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka
kubectl wait --for=condition=available deployment/strimzi-cluster-operator -n kafka --timeout=300s
```

## TASK 3: Deploy Single-Node Kafka (KRaft, NO ZooKeeper)

Create `k8s/base/09-kafka.yaml`:
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
  roles: [controller, broker]
  storage:
    type: jbod
    volumes:
      - id: 0
        type: persistent-claim
        size: 5Gi
        deleteClaim: true
        class: standard
  resources:
    requests: { cpu: 250m, memory: 512Mi }
    limits: { cpu: 500m, memory: 1Gi }
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
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      num.partitions: 3
      log.retention.hours: 24
  entityOperator:
    topicOperator:
      resources:
        requests: { cpu: 50m, memory: 128Mi }
        limits: { cpu: 200m, memory: 256Mi }
    userOperator:
      resources:
        requests: { cpu: 50m, memory: 128Mi }
        limits: { cpu: 200m, memory: 256Mi }
```

```bash
kubectl apply -f k8s/base/09-kafka.yaml
echo "⏳ Waiting for Kafka (2-5 min)..."
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka
kubectl get pods -n kafka
```

## TASK 4: Create Kafka Topics

Create `k8s/base/10-kafka-topics.yaml`:
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
    retention.ms: "86400000"
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
```

```bash
kubectl apply -f k8s/base/10-kafka-topics.yaml
kubectl get kafkatopics -n kafka
```

## TASK 5: Switch Dapr Pub/Sub from Redis to Kafka

Create `k8s/base/11-dapr-pubsub-kafka.yaml`:
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
  - name: initialOffset
    value: "newest"
  - name: disableTls
    value: "true"
```

```bash
kubectl delete component pubsub -n todo-app 2>/dev/null
kubectl apply -f k8s/base/11-dapr-pubsub-kafka.yaml
kubectl rollout restart deployment/todo-app-backend -n todo-app
kubectl rollout restart deployment/todo-app-frontend -n todo-app
kubectl rollout status deployment/todo-app-backend -n todo-app --timeout=120s
```

## TASK 6: Verify Kafka Event Flow
```bash
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000 &
sleep 3
curl -s -X POST http://localhost:8000/api/todos -H "Content-Type: application/json" \
  -d '{"title":"Kafka Test","category":"work","priority":"high"}' | python3 -m json.tool

BACKEND_POD=$(kubectl get pod -n todo-app -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
kubectl logs -n todo-app $BACKEND_POD -c daprd --tail=20 | grep -i "kafka\|publish"
kill %1 2>/dev/null
```

## DELIVERABLES (show me):
```bash
kubectl get kafka -n kafka
kubectl get kafkatopics -n kafka
kubectl describe component pubsub -n todo-app | grep -A5 "Spec"
kubectl get pods -n todo-app
kubectl get pods -n kafka
kubectl top nodes
```

**When done: Part 1 complete → Start new session for Part 2**
