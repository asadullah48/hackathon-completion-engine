# H4 SPECIFICATION: CLOUD-NATIVE TODO APP DEPLOYMENT
**Platinum Tier - Production Kubernetes Deployment**

---

## PROJECT OVERVIEW

**Project Name:** H4 - Cloud-Native Todo App Deployment
**Developer:** Asadullah Shafique (@asadullah48)
**Base Project:** H3 Advanced Todo (Gold Tier)
**Target Tier:** Platinum 💎
**Estimated Time:** 12-15 hours (4 sessions × 3-4 hours)
**Start Date:** February 2026
**Completion Date:** TBD

---

## MISSION STATEMENT

Deploy the H3 Advanced Todo application to a production-grade Kubernetes cluster with:
- Container orchestration (Kubernetes)
- Service mesh (Dapr)
- Event streaming (Kafka)
- Full observability (Prometheus, Grafana, Jaeger)
- CI/CD automation (GitHub Actions)
- Production hardening (scaling, health checks, secrets)

**Success Criteria:** Application runs reliably in K8s with monitoring, scales automatically, and deploys via CI/CD.

---

## ARCHITECTURE OVERVIEW

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                     KUBERNETES CLUSTER                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    INGRESS CONTROLLER                    │  │
│  │            (nginx-ingress / Traefik)                     │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────────────┴────────────────────────────────────┐  │
│  │                  APPLICATION PODS                        │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Frontend   │  │   Backend    │  │  AI Service  │  │  │
│  │  │   Next.js    │  │   FastAPI    │  │  (Suggestions)│  │  │
│  │  │              │  │              │  │              │  │  │
│  │  │ + Dapr       │  │ + Dapr       │  │ + Dapr       │  │  │
│  │  │   Sidecar    │  │   Sidecar    │  │   Sidecar    │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │  │
│  │         │                 │                 │          │  │
│  │         └─────────────────┼─────────────────┘          │  │
│  │                           │                            │  │
│  └───────────────────────────┼────────────────────────────┘  │
│                              │                               │
│  ┌───────────────────────────┼────────────────────────────┐  │
│  │              DAPR CONTROL PLANE                        │  │
│  │     (Service Invocation, Pub/Sub, State Store)        │  │
│  └───────────────────────────┼────────────────────────────┘  │
│                              │                               │
│  ┌───────────────────────────┼────────────────────────────┐  │
│  │                  DATA LAYER                            │  │
│  │                                                         │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ PostgreSQL   │  │    Kafka     │  │    Redis     │ │  │
│  │  │ (StatefulSet)│  │ (StatefulSet)│  │ (Deployment) │ │  │
│  │  │              │  │              │  │              │ │  │
│  │  │ PersistentVol│  │ Zookeeper    │  │ State Store  │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              OBSERVABILITY STACK                         │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │  Prometheus  │  │   Grafana    │  │    Jaeger    │  │  │
│  │  │  (Metrics)   │  │ (Dashboards) │  │  (Tracing)   │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                           │  │
│  │  ┌──────────────┐  ┌──────────────┐                     │  │
│  │  │     Loki     │  │ AlertManager │                     │  │
│  │  │    (Logs)    │  │  (Alerts)    │                     │  │
│  │  └──────────────┘  └──────────────┘                     │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

| Component | Technology | Purpose | K8s Resource |
|-----------|------------|---------|--------------|
| Frontend | Next.js 14 | Web UI | Deployment + Service |
| Backend | FastAPI | REST API | Deployment + Service |
| AI Service | Python | Suggestions | Deployment + Service |
| Database | PostgreSQL 15 | Data persistence | StatefulSet + PVC |
| Cache | Redis 7 | Session/state | Deployment + Service |
| Message Queue | Kafka 3.x | Event streaming | StatefulSet + PVC |
| Service Mesh | Dapr 1.12 | Inter-service comm | DaprComponent |
| Ingress | nginx-ingress | External routing | Ingress |
| Monitoring | Prometheus | Metrics collection | Deployment |
| Dashboards | Grafana | Visualization | Deployment |
| Tracing | Jaeger | Distributed tracing | Deployment |
| Logging | Loki | Log aggregation | Deployment |

---

## PLATINUM TIER REQUIREMENTS

### Must Have (Core Requirements)
- [ ] Kubernetes deployment manifests for all services
- [ ] Docker images for frontend, backend, AI service
- [ ] Dapr sidecar integration for service mesh
- [ ] Kafka for event-driven communication
- [ ] PostgreSQL StatefulSet with persistent storage
- [ ] Redis for caching and session state
- [ ] Horizontal Pod Autoscaler (HPA) configuration
- [ ] Health checks (liveness, readiness probes)
- [ ] ConfigMaps for configuration
- [ ] Secrets for sensitive data (DB passwords, API keys)
- [ ] Service discovery via K8s DNS
- [ ] Load balancing via K8s Services
- [ ] Ingress for external access

### Should Have (Production Hardening)
- [ ] Helm charts for templated deployment
- [ ] GitHub Actions CI/CD pipeline
- [ ] Prometheus metrics collection
- [ ] Grafana dashboards (4+ dashboards)
- [ ] Jaeger distributed tracing
- [ ] Loki log aggregation
- [ ] AlertManager for notifications
- [ ] Resource limits and requests
- [ ] Network policies for security
- [ ] Pod disruption budgets
- [ ] Rolling update strategy

### Nice to Have (Advanced Features)
- [ ] GitOps with ArgoCD
- [ ] Istio/Linkerd service mesh (alternative to Dapr)
- [ ] Chaos engineering tests (Chaos Monkey)
- [ ] Performance benchmarks (k6, Locust)
- [ ] Multi-region deployment
- [ ] Disaster recovery plan
- [ ] Cost optimization analysis
- [ ] Security scanning (Trivy, Snyk)

---

## SESSION BREAKDOWN

### Session 1: Containerization & Local K8s (3-4 hours)

**Objectives:**
- Create Dockerfiles for all services
- Build and push images to container registry
- Set up local Kubernetes (Minikube/Kind)
- Deploy basic services to local cluster

**Deliverables:**
```
hackathons/h4-cloud-native/
├── docker/
│   ├── frontend/
│   │   └── Dockerfile
│   ├── backend/
│   │   └── Dockerfile
│   └── ai-service/
│       └── Dockerfile
├── k8s/
│   ├── namespace.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── ai-service/
│       ├── deployment.yaml
│       └── service.yaml
└── scripts/
    ├── build-images.sh
    └── deploy-local.sh
```

**Tasks:**
1. Create multi-stage Dockerfile for Next.js frontend
2. Create Dockerfile for FastAPI backend
3. Create Dockerfile for AI suggestion service
4. Set up local container registry or use Docker Hub
5. Create Kubernetes namespace and basic deployments
6. Verify services communicate within cluster
7. Create local development scripts

**Success Criteria:**
- All 3 services running in local K8s cluster
- Services can communicate via K8s DNS
- Health checks passing
- 20+ tests validating deployment

---

### Session 2: Data Layer & Dapr Integration (3-4 hours)

**Objectives:**
- Deploy PostgreSQL as StatefulSet
- Deploy Redis for caching
- Set up Kafka for event streaming
- Integrate Dapr for service mesh

**Deliverables:**
```
hackathons/h4-cloud-native/
├── k8s/
│   ├── postgres/
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   ├── pvc.yaml
│   │   └── configmap.yaml
│   ├── redis/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── kafka/
│   │   ├── zookeeper-statefulset.yaml
│   │   ├── kafka-statefulset.yaml
│   │   └── topics.yaml
│   └── dapr/
│       ├── components/
│       │   ├── statestore.yaml
│       │   ├── pubsub.yaml
│       │   └── configuration.yaml
│       └── subscriptions/
│           └── todo-events.yaml
└── migrations/
    └── init.sql
```

**Tasks:**
1. Create PostgreSQL StatefulSet with PVC
2. Configure database initialization scripts
3. Deploy Redis for session/cache
4. Deploy Kafka cluster with Zookeeper
5. Install Dapr in Kubernetes cluster
6. Configure Dapr components (state store, pub/sub)
7. Update application code for Dapr SDK
8. Test event-driven communication

**Success Criteria:**
- PostgreSQL persists data across pod restarts
- Redis caching operational
- Kafka topics created and events flowing
- Dapr sidecars injected and healthy
- 40+ tests passing

---

### Session 3: Observability & Production Hardening (3-4 hours)

**Objectives:**
- Deploy Prometheus for metrics
- Set up Grafana dashboards
- Configure Jaeger for tracing
- Add production hardening features

**Deliverables:**
```
hackathons/h4-cloud-native/
├── k8s/
│   ├── monitoring/
│   │   ├── prometheus/
│   │   │   ├── deployment.yaml
│   │   │   ├── configmap.yaml
│   │   │   └── servicemonitor.yaml
│   │   ├── grafana/
│   │   │   ├── deployment.yaml
│   │   │   └── dashboards/
│   │   │       ├── application.json
│   │   │       ├── infrastructure.json
│   │   │       ├── kafka.json
│   │   │       └── dapr.json
│   │   └── jaeger/
│   │       └── deployment.yaml
│   ├── hpa/
│   │   ├── frontend-hpa.yaml
│   │   ├── backend-hpa.yaml
│   │   └── ai-service-hpa.yaml
│   ├── network-policies/
│   │   └── default-deny.yaml
│   └── secrets/
│       └── sealed-secrets.yaml
└── dashboards/
    └── *.json
```

**Tasks:**
1. Deploy Prometheus with ServiceMonitor
2. Create Grafana dashboards (4 minimum)
3. Deploy Jaeger for distributed tracing
4. Add OpenTelemetry instrumentation
5. Configure HPA for auto-scaling
6. Add resource limits and requests
7. Create network policies
8. Set up secrets management

**Success Criteria:**
- Prometheus collecting metrics from all services
- Grafana dashboards showing real-time data
- Traces visible in Jaeger UI
- HPA scaling pods based on load
- 60+ tests passing

---

### Session 4: CI/CD & Helm Charts (3-4 hours)

**Objectives:**
- Create Helm charts for deployment
- Set up GitHub Actions CI/CD
- Configure production deployment pipeline
- Complete documentation

**Deliverables:**
```
hackathons/h4-cloud-native/
├── helm/
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-dev.yaml
│       ├── values-staging.yaml
│       ├── values-prod.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── frontend/
│           ├── backend/
│           ├── ai-service/
│           ├── postgres/
│           ├── redis/
│           ├── kafka/
│           ├── ingress.yaml
│           └── secrets.yaml
├── .github/
│   └── workflows/
│       ├── ci.yaml
│       ├── cd-staging.yaml
│       └── cd-production.yaml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   ├── RUNBOOK.md
│   └── TROUBLESHOOTING.md
├── README.md
└── COMPLETION_REPORT.md
```

**Tasks:**
1. Create Helm chart structure
2. Template all Kubernetes manifests
3. Create environment-specific values files
4. Set up GitHub Actions workflows
5. Configure staging deployment pipeline
6. Configure production deployment pipeline
7. Write comprehensive documentation
8. Create runbook for operations

**Success Criteria:**
- Helm chart deploys complete application
- CI pipeline runs tests on PR
- CD pipeline deploys to staging/production
- Complete documentation
- 80+ tests passing
- Platinum tier certification

---

## TECHNOLOGY STACK

### Container & Orchestration
| Technology | Version | Purpose |
|------------|---------|---------|
| Docker | 24.x | Containerization |
| Kubernetes | 1.28+ | Orchestration |
| Minikube | 1.32+ | Local development |
| kubectl | 1.28+ | CLI management |
| Helm | 3.13+ | Package management |

### Service Mesh & Communication
| Technology | Version | Purpose |
|------------|---------|---------|
| Dapr | 1.12+ | Service mesh, pub/sub |
| Kafka | 3.6+ | Event streaming |
| Redis | 7.2+ | Caching, state store |

### Data Layer
| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15+ | Primary database |
| Redis | 7.2+ | Cache layer |

### Observability
| Technology | Version | Purpose |
|------------|---------|---------|
| Prometheus | 2.48+ | Metrics collection |
| Grafana | 10.2+ | Dashboards |
| Jaeger | 1.52+ | Distributed tracing |
| Loki | 2.9+ | Log aggregation |
| OpenTelemetry | 1.x | Instrumentation |

### CI/CD
| Technology | Version | Purpose |
|------------|---------|---------|
| GitHub Actions | - | CI/CD pipeline |
| Docker Hub | - | Container registry |
| ArgoCD | 2.9+ | GitOps (optional) |

---

## KUBERNETES MANIFESTS SPECIFICATION

### Namespace
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: todo-app
  labels:
    app: todo-app
    environment: production
```

### Frontend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: todo-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "frontend"
        dapr.io/app-port: "3000"
    spec:
      containers:
      - name: frontend
        image: todo-app/frontend:latest
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: NEXT_PUBLIC_API_URL
          valueFrom:
            configMapKeyRef:
              name: frontend-config
              key: api_url
```

### Backend Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: todo-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: backend
        image: todo-app/backend:latest
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: backend-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: backend-config
              key: redis_url
```

### PostgreSQL StatefulSet
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: todo-app
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: "tododb"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secrets
              key: password
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: todo-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## DAPR CONFIGURATION

### State Store Component (Redis)
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: redis:6379
  - name: redisPassword
    secretKeyRef:
      name: redis-secrets
      key: password
```

### Pub/Sub Component (Kafka)
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
    value: kafka:9092
  - name: consumerGroup
    value: todo-app-group
  - name: authRequired
    value: "false"
```

### Event Subscription
```yaml
apiVersion: dapr.io/v1alpha1
kind: Subscription
metadata:
  name: todo-events-subscription
  namespace: todo-app
spec:
  topic: todo-events
  route: /api/events/todo
  pubsubname: pubsub
  scopes:
  - backend
  - ai-service
```

---

## CI/CD PIPELINE

### GitHub Actions CI Workflow
```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.12'

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '20'

    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        cd frontend && npm ci

    - name: Run backend tests
      run: |
        cd backend
        pytest tests/ -v --cov=. --cov-report=xml

    - name: Run frontend tests
      run: |
        cd frontend
        npm run test:ci

    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}

    - name: Build and push frontend
      uses: docker/build-push-action@v5
      with:
        context: ./frontend
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/todo-frontend:${{ github.sha }}

    - name: Build and push backend
      uses: docker/build-push-action@v5
      with:
        context: ./backend
        push: true
        tags: ${{ secrets.DOCKER_USERNAME }}/todo-backend:${{ github.sha }}

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Deploy to staging
      run: |
        helm upgrade --install todo-app ./helm/todo-app \
          --namespace todo-staging \
          --values ./helm/todo-app/values-staging.yaml \
          --set image.tag=${{ github.sha }}
```

---

## MONITORING & ALERTING

### Prometheus ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: todo-app-monitor
  namespace: todo-app
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboard (Application Metrics)
```json
{
  "dashboard": {
    "title": "Todo App - Application Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{app=\"backend\"}[5m])"
          }
        ]
      },
      {
        "title": "Response Time (p95)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{app=\"backend\"}[5m]))"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{app=\"backend\",status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Pod CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_cpu_usage_seconds_total{namespace=\"todo-app\"}"
          }
        ]
      }
    ]
  }
}
```

---

## TESTING REQUIREMENTS

### Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| Container Tests | 15 | Dockerfile validation, image build |
| K8s Manifests | 20 | YAML validation, deployment |
| Integration | 25 | Service communication |
| E2E | 15 | Full workflow testing |
| Load | 5 | Performance under load |
| Chaos | 5 | Resilience testing |
| **Total** | **85** | Platinum tier target |

### Test Commands
```bash
# Container tests
docker build -t todo-frontend:test ./frontend
docker build -t todo-backend:test ./backend

# K8s manifest validation
kubectl apply --dry-run=client -f k8s/

# Helm lint
helm lint ./helm/todo-app

# Integration tests
pytest tests/integration/ -v

# E2E tests
pytest tests/e2e/ -v

# Load tests
k6 run tests/load/script.js
```

---

## SUCCESS METRICS

### Platinum Tier Certification Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| Total Tests | 85+ | pytest + k6 |
| Test Coverage | 80%+ | pytest-cov |
| Deployment Time | <5 min | CI/CD pipeline |
| Pod Startup | <30 sec | K8s probes |
| HPA Response | <60 sec | Load test |
| P95 Latency | <200ms | Prometheus |
| Availability | 99.9% | Uptime check |
| Error Rate | <0.1% | Prometheus |

### Documentation Checklist
- [ ] README.md with quick start
- [ ] ARCHITECTURE.md with diagrams
- [ ] DEPLOYMENT.md with step-by-step
- [ ] RUNBOOK.md for operations
- [ ] TROUBLESHOOTING.md for common issues
- [ ] API documentation (OpenAPI)
- [ ] Grafana dashboard screenshots

---

## TIMELINE

| Session | Duration | Deliverables | Tests |
|---------|----------|--------------|-------|
| Session 1 | 3-4 hours | Containerization + Local K8s | 20+ |
| Session 2 | 3-4 hours | Data Layer + Dapr | 40+ |
| Session 3 | 3-4 hours | Observability + Hardening | 60+ |
| Session 4 | 3-4 hours | CI/CD + Helm + Docs | 85+ |
| **Total** | **12-15 hours** | **Platinum Tier** | **85+** |

---

## RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| K8s complexity | High | High | Start with Minikube, incremental deployment |
| Dapr learning curve | Medium | Medium | Use official examples, fallback to direct HTTP |
| Kafka setup | Medium | Medium | Use Strimzi operator, have Redis fallback |
| CI/CD failures | Low | High | Staged rollouts, manual approval gates |
| Resource limits | Medium | Medium | Start generous, optimize based on metrics |

---

## REFERENCES

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Dapr Documentation](https://docs.dapr.io/)
- [Helm Documentation](https://helm.sh/docs/)
- [Prometheus Operator](https://prometheus-operator.dev/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

*H4 Specification - Platinum Tier Cloud-Native Deployment*
*Panaversity Hackathon Series*
