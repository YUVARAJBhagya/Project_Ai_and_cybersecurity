import os

API_URL = os.getenv("API_URL", "http://a4s-api:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_URL_PREFIX = f"{API_URL}{API_PREFIX}"
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/cache")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")
REDIS_BACKEND_URL = os.getenv("REDIS_BACKEND_URL", "redis://redis:6379/1")
