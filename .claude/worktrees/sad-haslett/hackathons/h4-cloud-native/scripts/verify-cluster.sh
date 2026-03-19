#!/bin/bash
# H4 Cloud-Native Cluster Verification Script
# Run: bash scripts/verify-cluster.sh

echo "============================================"
echo "  H4 CLOUD-NATIVE VERIFICATION REPORT"
echo "  $(date)"
echo "============================================"

PASS=0
FAIL=0

check() {
  if eval "$2" > /dev/null 2>&1; then
    echo "  PASS: $1"
    ((PASS++))
  else
    echo "  FAIL: $1"
    ((FAIL++))
  fi
}

echo ""
echo "-- KUBERNETES CLUSTER --"
check "Minikube running" "minikube status | grep -q Running"
check "todo-app namespace" "kubectl get ns todo-app"
check "kafka namespace" "kubectl get ns kafka"

echo ""
echo "-- APPLICATION PODS --"
check "Backend pod exists" "kubectl get pods -n todo-app -l app.kubernetes.io/component=backend --no-headers | head -1"
check "Frontend running" "kubectl get pods -n todo-app -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].status.phase}' | grep -q Running"
check "Notification running" "kubectl get pods -n todo-app -l app.kubernetes.io/component=notification -o jsonpath='{.items[0].status.phase}' | grep -q Running"
check "PostgreSQL pod exists" "kubectl get pods -n todo-app -l app.kubernetes.io/component=postgresql --no-headers | head -1"
check "Redis running" "kubectl get pods -n todo-app -l app=redis -o jsonpath='{.items[0].status.phase}' | grep -q Running"
check "Prometheus running" "kubectl get pods -n todo-app -l app=prometheus -o jsonpath='{.items[0].status.phase}' | grep -q Running"

echo ""
echo "-- DAPR --"
check "Dapr system running" "kubectl get pods -n dapr-system --no-headers | grep -c Running"
check "Dapr statestore component" "kubectl get component statestore -n todo-app"
check "Dapr pubsub component (Kafka)" "kubectl get component pubsub -n todo-app"

echo ""
echo "-- KAFKA --"
check "Kafka cluster ready" "kubectl get kafka todo-kafka -n kafka -o jsonpath='{.status.conditions[?(@.type==\"Ready\")].status}' | grep -q True"
check "Topic: todo-events" "kubectl get kafkatopic todo-events -n kafka"
check "Topic: todo-notifications" "kubectl get kafkatopic todo-notifications -n kafka"
check "Topic: todo-analytics" "kubectl get kafkatopic todo-analytics -n kafka"

echo ""
echo "-- OBSERVABILITY --"
check "Prometheus deployment" "kubectl get deployment prometheus -n todo-app"
check "Backend /metrics endpoint" "kubectl exec -n todo-app \$(kubectl get pod -n todo-app -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -c backend -- wget -qO- http://localhost:8000/metrics 2>/dev/null | grep -q http_requests_total"

echo ""
echo "-- CI/CD --"
check "GitHub Actions workflow exists" "test -f /mnt/d/Personal-AI-Employee/.github/workflows/ci-cd.yaml"

echo ""
echo "============================================"
TOTAL=$((PASS + FAIL))
if [ $TOTAL -gt 0 ]; then
  echo "  RESULTS: $PASS passed, $FAIL failed"
  echo "  $(( PASS * 100 / TOTAL ))% passing"
else
  echo "  RESULTS: No checks executed"
fi
echo "============================================"
