#!/bin/bash
# H4 Cloud-Native Todo App - Deploy Script

set -e

echo "🚀 H4 Cloud-Native Todo App - Deploy"
echo "====================================="
echo ""

# Apply all manifests
echo "📦 Applying Kubernetes manifests..."
kubectl apply -f k8s/base/00-namespace.yaml
kubectl apply -f k8s/base/01-configmap.yaml
kubectl apply -f k8s/base/02-secret.yaml
kubectl apply -f k8s/base/03-postgresql.yaml
echo ""

# Wait for PostgreSQL
echo "⏳ Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgresql -n todo-app --timeout=300s
echo "✅ PostgreSQL is ready"
echo ""

# Deploy application
echo "📦 Deploying backend and frontend..."
kubectl apply -f k8s/base/04-backend.yaml
kubectl apply -f k8s/base/05-frontend.yaml
echo ""

# Wait for deployments
echo "⏳ Waiting for backend..."
kubectl wait --for=condition=available deployment/backend -n todo-app --timeout=300s
echo "✅ Backend is ready"
echo ""

echo "⏳ Waiting for frontend..."
kubectl wait --for=condition=available deployment/frontend -n todo-app --timeout=300s
echo "✅ Frontend is ready"
echo ""

# Show status
echo "📋 Deployment Status:"
kubectl get pods -n todo-app
echo ""

echo "✅ Deployment complete!"
echo ""
echo "To access the app, run:"
echo "  minikube service frontend -n todo-app"
