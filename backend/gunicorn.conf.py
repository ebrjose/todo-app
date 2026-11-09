"""Gunicorn settings. Loaded automatically from the working directory (/app).

Every value can be overridden with an environment variable, so the same image
works in docker compose and in Kubernetes with different sizes.
"""

import os

wsgi_app = "config.wsgi:application"
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Processes per container. In Kubernetes, scale with replicas rather than workers.
workers = int(os.environ.get("WEB_CONCURRENCY", "3"))

# Kill a worker stuck on a request for longer than this many seconds.
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "30"))
# On SIGTERM, give in-flight requests this long to finish (keep it under
# the pod's terminationGracePeriodSeconds, 30 s by default).
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "20"))

# Worker heartbeat files in RAM: the default /tmp can be slow on container disks.
worker_tmp_dir = "/dev/shm"

# Logs to stdout/stderr so `docker logs` / `kubectl logs` show them.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("GUNICORN_LOG_LEVEL", "info")
