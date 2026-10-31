# H4 Session 1: Kubernetes Deployment

## Summary

Successfully deployed H3 Advanced Todo app to Kubernetes (Minikube).

**Deployment Date:** 2026-02-02

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes (Minikube)                     │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────┐              │
│  │  Frontend (x2)   │    │  Backend (x2)    │              │
│  │  Next.js 14      │───▶│  FastAPI         │              │
│  │  Port: 3000      │    │  Port: 8000      │              │
│  │  LoadBalancer    │    │  ClusterIP       │              │
│  └──────────────────┘    └────────┬─────────┘              │
│                                    │                        │
│                          ┌────────▼─────────┐              │
│                          │  PostgreSQL (x1) │              │
│                          │  Port: 5432      │              │
│                          │  StatefulSet     │              │
│                          │  5Gi PVC         │              │
│                          └──────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## Resources Created

| Resource Type | Name | Replicas | Status |
|---------------|------|----------|--------|
| Namespace | todo-app | - | ✅ Created |
| ConfigMap | todo-app-config | - | ✅ Created |
| Secret | todo-app-secrets | - | ✅ Created |
| StatefulSet | postgresql | 1 | ✅ Running |
| Deployment | backend | 2 | ✅ Running |
| Deployment | frontend | 2 | ✅ Running |
| Service | postgresql | 1 | ✅ ClusterIP (Headless) |
| Service | backend | 1 | ✅ ClusterIP |
| Service | frontend | 1 | ✅ LoadBalancer |
| PersistentVolumeClaim | postgresql-data | 5Gi | ✅ Bound |

## Images Built

| Image | Tag | Size |
|-------|-----|------|
| todo-backend | v1.0.0 | ~65 MB |
| todo-frontend | v1.0.0 | ~50 MB |

## Configuration

### Environment Variables (ConfigMap)

- `DATABASE_URL`: PostgreSQL connection string
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend
- `ENVIRONMENT`: development
- `LOG_LEVEL`: INFO
- `CORS_ORIGINS`: * (allow all for development)

### Secrets

- PostgreSQL credentials (user/password/database)
- Application secret key

## Verification Commands

```bash
# Check all pods
kubectl get pods -n todo-app

# Check services
kubectl get svc -n todo-app

# Check deployments
kubectl get deployments -n todo-app

# View backend logs
kubectl logs -n todo-app -l app=backend --tail=20

# View frontend logs
kubectl logs -n todo-app -l app=frontend --tail=20

# Test backend health
kubectl exec -n todo-app deployment/backend -c backend -- \
  python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"

# Access frontend (opens browser)
minikube service frontend -n todo-app
```

## Access Points

### Development (Minikube)

```bash
# Start minikube tunnel for LoadBalancer services
minikube tunnel

# Get frontend URL
minikube service frontend -n todo-app --url

# Port-forward backend for direct API access
kubectl port-forward -n todo-app svc/backend 8080:8000
```

### Endpoints

- **Frontend**: http://localhost:3000 (via minikube service)
- **Backend API**: http://backend:8000 (internal) / http://localhost:8080 (port-forward)
- **API Docs**: http://localhost:8080/docs (port-forward)

## Health Checks

| Service | Endpoint | Method | Expected |
|---------|----------|--------|----------|
| Backend | /health | GET | `{"status":"healthy","service":"h4-cloud-native-todo-api"}` |
| Frontend | / | GET | 200 OK |
| PostgreSQL | pg_isready | exec | exit 0 |

## Features Deployed

✅ All H3 Gold Tier features:
- CRUD operations for todos
- Constitutional validation
- HITL approval workflow
- Recurring todos
- Todo templates (5 built-in)
- Team collaboration
- User management
- Todo assignments
- AI-powered suggestions
- Calendar integration

## Known Issues / Notes

1. Frontend LoadBalancer shows `<pending>` for EXTERNAL-IP - use `minikube service` or `minikube tunnel`
2. Backend requires `email-validator` for Pydantic email fields
3. Build images inside minikube Docker environment for best compatibility:
   ```bash
   eval $(minikube docker-env)
   docker build -t todo-backend:v1.0.0 -f docker/backend.Dockerfile .
   ```

## Next Steps (Session 2)

- [ ] Add Helm chart for templated deployment
- [ ] Implement Kustomize overlays (dev/staging/prod)
- [ ] Add Horizontal Pod Autoscaler (HPA)
- [ ] Configure Ingress controller
- [ ] Add health monitoring with Prometheus/Grafana
- [ ] Implement GitOps with ArgoCD

## Session 1 Checklist

- [x] Copy H3 as base for H4
- [x] Create directory structure (k8s/, docker/, helm/, docs/)
- [x] Create backend Dockerfile (multi-stage build)
- [x] Create frontend Dockerfile (multi-stage build)
- [x] Update next.config.js for standalone output
- [x] Add PostgreSQL support (psycopg2-binary)
- [x] Add email-validator for Pydantic
- [x] Build Docker images
- [x] Create Kubernetes manifests
  - [x] Namespace
  - [x] ConfigMap
  - [x] Secret
  - [x] PostgreSQL StatefulSet
  - [x] Backend Deployment + Service
  - [x] Frontend Deployment + Service
- [x] Deploy to Minikube
- [x] Verify all pods running
- [x] Test backend health endpoint
- [x] Test templates API

**Session 1 Status: ✅ COMPLETE**
