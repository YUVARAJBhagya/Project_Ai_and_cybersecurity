"""Environment configuration module for A4S Evaluation.

This module defines environment variables and their default values used throughout
the A4S evaluation system. These can be overridden by setting actual environment
variables.
"""

import os
from urllib.parse import quote

from httpx import get
from numpy import true_divide

from a4s_eval.utils.logging import get_logger

logger = get_logger()


def handle_bool_var(envvar: str) -> bool:
    return str(envvar).lower() == "true"


API_URL = os.getenv("API_URL", "http://a4s-api:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_URL_PREFIX = f"{API_URL}{API_PREFIX}"
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/cache")

REDIS_SSL_CERT_REQS = handle_bool_var(os.getenv("REDIS_SSL_CERT_REQS", "true"))


def redis_handle_ssl_option(redis_url: str) -> str:
    # Only apply to ssl redis
    if not redis_url.startswith("rediss://"):
        return redis_url

    if not REDIS_SSL_CERT_REQS and ("ssl_cert_reqs" not in redis_url):
        separator = "&" if "?" in redis_url else "?"
        return f"{redis_url}{separator}ssl_cert_reqs=none"

    return redis_url


# Redis configuration
def get_redis_backend_url() -> str:
    """Construct Redis backend URL for Celery from environment variables."""
    # Check if REDIS_BACKEND_URL is provided directly
    redis_url = os.getenv("REDIS_BACKEND_URL")
    if redis_url:
        # Fix SSL configuration if needed
        return redis_handle_ssl_option(redis_url)

    # For AWS, construct from individual components
    redis_host = os.getenv("REDIS_HOST", "redis")

    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
    redis_auth_token = os.getenv("REDIS_AUTH_TOKEN", "")
    redis_auth_token_url = ""
    if redis_auth_token:
        redis_auth_token_url = f":{redis_auth_token}@"

    scheme = "rediss" if redis_ssl else "redis"

    redis_url = f"{scheme}://{redis_auth_token_url}{redis_host}:{redis_port}/1"
    return redis_handle_ssl_option(redis_url)


REDIS_BACKEND_URL = get_redis_backend_url()


# Celery Broker URL - construct from environment variables or use default


def get_fixed_url(broker_url: str) -> str:
    try:
        from urllib.parse import urlparse, urlunparse

        parsed = urlparse(broker_url)
        if parsed.password:
            # Re-encode the password properly
            encoded_password = quote(parsed.password, safe="")
            # Reconstruct the URL with properly encoded password
            netloc = f"{parsed.username}:{encoded_password}@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            fixed_url = urlunparse(
                (
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )
            return fixed_url
    except Exception as e:
        logger.warning(
            f"Failed to fix CELERY_BROKER_URL encoding: {e}, constructing from components"
        )


def get_celery_broker_url():
    """Construct Celery broker URL from environment variables."""
    # Try to get the direct URL first
    broker_url = os.getenv("CELERY_BROKER_URL")
    if broker_url:
        # We are not suppose to fix a broken url, user should send valid url
        return get_fixed_url(broker_url)

    # Construct from separate environment variables
    mq_host = os.getenv("MQ_HOST", "rabbitmq")
    mq_username = os.getenv("MQ_USERNAME", "")
    mq_password = os.getenv("MQ_PASSWORD", "")
    mq_use_ssl = handle_bool_var(os.getenv("MQ_USE_SSL", "false"))
    mq_port = os.getenv("MQ_PORT", "5671")
    encoded_password = quote(mq_password)

    url_prexix = "ampqs://" if mq_use_ssl else "ampq://"

    url_login = mq_username
    if encoded_password:
        url_login += f":{encoded_password}"
    if url_login:
        url_login += "@"
    url_port = f":{mq_port}" if mq_port else ""

    url = f"{url_prexix}{url_login}{mq_host}{url_port}"

    return url


CELERY_BROKER_URL = get_celery_broker_url()
