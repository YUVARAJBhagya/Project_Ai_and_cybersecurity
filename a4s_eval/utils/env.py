"""Environment configuration module for A4S Evaluation.

 This module constructs connection URLs for AWS services from environment variables.

Architecture:
- Static config (hosts, ports): Environment variables from Terraform
- Sensitive data (passwords, tokens): AWS Secrets Manager via ECS secrets
- URLs: Constructed from components for flexibility
"""

import os
from urllib.parse import quote, urlparse, urlunparse
from a4s_eval.utils.logging import get_logger

logger = get_logger()

# Application Configuration
API_URL = os.getenv("API_URL", "http://a4s-api:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_URL_PREFIX = f"{API_URL}{API_PREFIX}"
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/cache")


# Redis Configuration
def get_redis_backend_url() -> str:
    """Construct Redis URL for Celery from environment variables."""
    if redis_url := os.getenv("REDIS_BACKEND_URL"):
        if redis_url.startswith("rediss://") and "ssl_cert_reqs" not in redis_url:
            separator = "&" if "?" in redis_url else "?"
            return f"{redis_url}{separator}ssl_cert_reqs=none"
        return redis_url

    host = os.getenv("REDIS_HOST")
    if not host:
        return "redis://redis:6379/1"  # Local development default

    port = os.getenv("REDIS_PORT", "6379")
    use_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
    use_auth = os.getenv("REDIS_AUTH_ENABLED", "false").lower() == "true"
    auth_token = os.getenv("REDIS_AUTH_TOKEN", "")

    scheme = "rediss" if use_ssl else "redis"
    auth_part = f":{auth_token}@" if use_auth and auth_token else ""
    ssl_params = "?ssl_cert_reqs=none" if use_ssl else ""

    return f"{scheme}://{auth_part}{host}:{port}/1{ssl_params}"


REDIS_BACKEND_URL = get_redis_backend_url()


# MQ Configuration
def get_celery_broker_url() -> str:
    """Construct RabbitMQ URL for Celery from environment variables."""
    # Direct override for local development
    if broker_url := os.getenv("CELERY_BROKER_URL"):
        return _fix_password_encoding(broker_url)

    # Amazon MQ configuration
    username = os.getenv("MQ_USERNAME", "guest")
    password = os.getenv("MQ_PASSWORD", "guest")
    use_ssl = os.getenv("MQ_USE_SSL", "false").lower() == "true"

    # Choose endpoint (prefer SSL if requested)
    endpoint = (
        os.getenv("MQ_AMQPS_ENDPOINT")
        if use_ssl
        else os.getenv("MQ_AMQP_ENDPOINT") or os.getenv("MQ_AMQPS_ENDPOINT")
    )

    if not endpoint:
        return "amqp://guest:guest@localhost:5672//"

    # Auto-detect scheme from endpoint or use preference
    scheme = "amqps" if endpoint.startswith("amqps://") or use_ssl else "amqp"

    # Clean endpoint and extract host:port
    clean_endpoint = endpoint.replace("amqps://", "").replace("amqp://", "")
    host, port = (
        clean_endpoint.split(":", 1)
        if ":" in clean_endpoint
        else (clean_endpoint, "5671" if scheme == "amqps" else "5672")
    )

    # URL encode password and construct URL
    encoded_password = quote(password, safe="")
    return f"{scheme}://{username}:{encoded_password}@{host}:{port}"


def _fix_password_encoding(url: str) -> str:
    """Fix URL encoding for passwords with special characters."""
    try:
        parsed = urlparse(url)
        if not parsed.password:
            return url

        encoded_password = quote(parsed.password, safe="")
        netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
        if parsed.port:
            netloc += f":{parsed.port}"

        return urlunparse(
            (
                parsed.scheme,
                netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment,
            )
        )
    except Exception as e:
        logger.warning(f"Failed to fix URL encoding: {e}")
        return url


CELERY_BROKER_URL = get_celery_broker_url()
