"""Prometheus metrics for Todo backend."""
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
import re

REQUEST_COUNT = Counter(
    'http_requests_total', 'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)
TODO_EVENTS = Counter(
    'todo_events_published_total', 'Events published to Kafka',
    ['event_type']
)
TODO_OPS = Counter(
    'todo_crud_operations_total', 'CRUD operations',
    ['operation']
)
REQUEST_DURATION = Histogram(
    'http_request_duration_seconds', 'Request duration',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/metrics":
            return await call_next(request)
        start = time.time()
        response = await call_next(request)
        path = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{id}', request.url.path
        )
        REQUEST_COUNT.labels(
            method=request.method, endpoint=path,
            status_code=response.status_code
        ).inc()
        REQUEST_DURATION.labels(
            method=request.method, endpoint=path
        ).observe(time.time() - start)
        return response


def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
