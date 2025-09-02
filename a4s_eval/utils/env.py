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
    redis_host = os.getenv("REDIS_HOST")

    if not redis_host:
        return "redis://redis:6379/1"


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
def get_celery_broker_url():
    """Construct Celery broker URL from environment variables."""
    # Try to get the direct URL first
    broker_url = os.getenv("CELERY_BROKER_URL")
    if broker_url:
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

    # Construct from separate environment variables
    mq_username = os.getenv("MQ_USERNAME", "guest")
    mq_password = os.getenv("MQ_PASSWORD", "guest")
    mq_amqps_endpoint = os.getenv("MQ_AMQPS_ENDPOINT")
    mq_amqp_endpoint = os.getenv("MQ_AMQP_ENDPOINT")
    mq_use_ssl = os.getenv("MQ_USE_SSL", "false").lower() == "true"

    # URL encode the password to handle special characters
    encoded_password = quote(mq_password) if mq_password else "guest"

    # Choose endpoint based on SSL preference or what's available
    if mq_use_ssl and mq_amqps_endpoint:
        endpoint = mq_amqps_endpoint.replace("amqps://", "")  # Remove scheme if present
        if ":" in endpoint:
            hostname, port = endpoint.split(":", 1)
            result = f"amqps://{mq_username}:{encoded_password}@{hostname}:{port}"
        else:
            result = f"amqps://{mq_username}:{encoded_password}@{endpoint}:5671"
        return result
    elif mq_amqp_endpoint:
        if mq_amqp_endpoint.startswith("amqps://"):
            # This is actually an AMQPS endpoint
            endpoint = mq_amqp_endpoint.replace("amqps://", "")
            if ":" in endpoint:
                hostname, port = endpoint.split(":", 1)
                result = f"amqps://{mq_username}:{encoded_password}@{hostname}:{port}"
            else:
                result = f"amqps://{mq_username}:{encoded_password}@{endpoint}:5671"
            return result
        else:
            # This is a regular AMQP endpoint
            endpoint = mq_amqp_endpoint.replace("amqp://", "")
            if ":" in endpoint:
                hostname, port = endpoint.split(":", 1)
                result = f"amqp://{mq_username}:{encoded_password}@{hostname}:{port}"
            else:
                result = f"amqp://{mq_username}:{encoded_password}@{endpoint}:5672"
            return result
    else:
        # Default for development
        logger.debug("No MQ endpoints found, using default localhost")
        return "amqp://guest:guest@localhost:5672//"


CELERY_BROKER_URL = get_celery_broker_url()
