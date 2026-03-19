#!/bin/bash
# H4 Cloud-Native Todo App - Build Images Script
# Builds images directly in minikube's Docker environment

set -e

echo "🔨 H4 Cloud-Native Todo App - Build Images"
echo "==========================================="
echo ""

# Set up minikube docker environment
echo "📦 Setting up minikube Docker environment..."
eval $(minikube docker-env)
echo "✅ Using minikube's Docker"
echo ""

# Build backend
echo "🐍 Building backend image..."
docker build -t todo-backend:v1.0.0 -f docker/backend.Dockerfile .
echo "✅ Backend image built"
echo ""

# Build frontend
echo "⚛️ Building frontend image..."
docker build -t todo-frontend:v1.0.0 -f docker/frontend.Dockerfile .
echo "✅ Frontend image built"
echo ""

# Show images
echo "📋 Built images:"
docker images | grep todo
echo ""

echo "✅ All images built successfully!"
echo ""
echo "To deploy/update, run:"
echo "  kubectl rollout restart deployment/backend -n todo-app"
echo "  kubectl rollout restart deployment/frontend -n todo-app"
