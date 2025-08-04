"""Environment configuration module for A4S Evaluation.

This module defines environment variables and their default values used throughout
the A4S evaluation system. These can be overridden by setting actual environment
variables.
"""

import os

API_URL = os.getenv("API_URL", "http://a4s-api:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_URL_PREFIX = f"{API_URL}{API_PREFIX}"
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/cache")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "")
REDIS_BACKEND_URL = os.getenv("REDIS_BACKEND_URL", "redis://redis:6379/1")

# S3 bucket names - automatically adapt based on environment
# In development: "datasets", "models"
# In production: "a4s-data-prod-datasets", "a4s-data-prod-models"
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

if IS_PRODUCTION:
    S3_DATASETS_BUCKET = os.getenv("S3_DATASETS_BUCKET", "a4s-data-prod-datasets")
    S3_MODELS_BUCKET = os.getenv("S3_MODELS_BUCKET", "a4s-data-prod-models")
else:
    S3_DATASETS_BUCKET = os.getenv("S3_DATASETS_BUCKET", "datasets")
    S3_MODELS_BUCKET = os.getenv("S3_MODELS_BUCKET", "models")
