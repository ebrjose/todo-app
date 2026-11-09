FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN groupadd --system --gid 1000 app \
 && useradd --system --uid 1000 --gid app --home-dir /app app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=app:app . .
RUN chmod +x entrypoint.sh \
 && DJANGO_SECRET_KEY=collectstatic python manage.py collectstatic --noinput

# Numeric UID so Kubernetes can verify runAsNonRoot without reading /etc/passwd.
USER 1000:1000
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
# Settings live in gunicorn.conf.py.
CMD ["gunicorn"]
