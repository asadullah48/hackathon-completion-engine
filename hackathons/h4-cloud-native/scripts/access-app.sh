#!/bin/bash
# H4 Cloud-Native Todo App Access Script

echo "🚀 H4 Cloud-Native Todo App Access"
echo "=================================="
echo ""

# Check minikube status
if ! minikube status > /dev/null 2>&1; then
    echo "❌ Minikube is not running. Start it with: minikube start"
    exit 1
fi

echo "✅ Minikube is running"
echo ""

# Check pods
echo "📦 Pod Status:"
kubectl get pods -n todo-app
echo ""

# Get frontend URL
echo "🌐 Getting frontend URL..."
echo "   (This will open a tunnel - keep this terminal open)"
echo ""
echo "   Press Ctrl+C to stop when done testing."
echo ""

minikube service frontend -n todo-app
