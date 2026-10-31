# H4 Cloud-Native Deployment Guide

## Overview

H4 transforms the H3 Advanced Todo application into a fully cloud-native deployment on Kubernetes with Helm charts, autoscaling, and comprehensive monitoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Kubernetes (Minikube)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐  │
│  │   Ingress   │───▶│  Frontend   │    │     Monitoring      │  │
│  │   (nginx)   │    │  (Next.js)  │    │  ┌───────────────┐  │  │
│  │             │    │  2 replicas │    │  │  Prometheus   │  │  │
│  │ todo.local  │    │  HPA: 2-5   │    │  │  + Grafana    │  │  │
│  └──────┬──────┘    └─────────────┘    │  │  + Alerts     │  │  │
│         │                               │  └───────────────┘  │  │
│         │           ┌─────────────┐    └─────────────────────┘  │
│         └──────────▶│   Backend   │                             │
│                     │  (FastAPI)  │                             │
│                     │  2 replicas │                             │
│                     │  HPA: 2-10  │                             │
│                     └──────┬──────┘                             │
│                            │                                     │
│                     ┌──────▼──────┐                             │
│                     │ PostgreSQL  │                             │
│                     │ StatefulSet │                             │
│                     │  + PVC 5Gi  │                             │
│                     └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Docker Desktop (running)
- Minikube v1.38+
- Helm v3.20+
- kubectl

### Deploy

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# 3. Build and load images
docker build -t todo-backend:v1.0.0 -f docker/backend.Dockerfile .
docker build -t todo-frontend:v1.0.0 -f docker/frontend.Dockerfile .
minikube image load todo-backend:v1.0.0
minikube image load todo-frontend:v1.0.0

# 4. Deploy with Helm
helm upgrade --install todo-app ./helm/todo-app -n todo-app --create-namespace

# 5. Deploy monitoring (optional)
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
```

### Access

```bash
# Add to /etc/hosts
echo "$(minikube ip) todo.local" | sudo tee -a /etc/hosts

# Or use port-forward
kubectl port-forward -n todo-app svc/todo-app-backend 8000:8000
kubectl port-forward -n todo-app svc/todo-app-frontend 3000:3000

# Monitoring
kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80
# Grafana: admin / admin123
```

## Helm Chart

### Values Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `frontend.replicaCount` | 2 | Frontend replicas |
| `frontend.autoscaling.enabled` | true | Enable HPA |
| `frontend.autoscaling.maxReplicas` | 5 | Max frontend pods |
| `backend.replicaCount` | 2 | Backend replicas |
| `backend.autoscaling.maxReplicas` | 10 | Max backend pods |
| `postgresql.persistence.size` | 5Gi | Database storage |
| `ingress.enabled` | true | Enable ingress |
| `monitoring.enabled` | true | Enable ServiceMonitors |

### Custom Values

```bash
helm upgrade todo-app ./helm/todo-app -n todo-app \
  --set backend.replicaCount=3 \
  --set frontend.autoscaling.maxReplicas=10
```

## Monitoring

### Alerts Configured
1. **TodoAppBackendDown** - Backend unavailable > 1min (critical)
2. **TodoAppHighCPU** - CPU > 80% for 5min (warning)
3. **TodoAppHighMemory** - Memory > 80% for 5min (warning)
4. **TodoAppPodRestarting** - >3 restarts/hour (warning)

### Dashboards
- Kubernetes cluster overview (built-in)
- Node metrics (built-in)
- Pod resource usage (built-in)

## Scaling

### Manual Scaling
```bash
kubectl scale deployment todo-app-backend -n todo-app --replicas=5
```

### HPA Behavior
- Target CPU: 70%
- Scale up: Immediate when threshold exceeded
- Scale down: 5 minute stabilization window

## Troubleshooting

```bash
# Check pods
kubectl get pods -n todo-app

# Check logs
kubectl logs -n todo-app -l app.kubernetes.io/component=backend

# Describe failing pod
kubectl describe pod <pod-name> -n todo-app

# Check HPA status
kubectl get hpa -n todo-app

# Check ingress
kubectl describe ingress todo-app -n todo-app
```

## Image Sizes
- `todo-frontend:v1.0.0` - 213MB
- `todo-backend:v1.0.0` - 274MB
