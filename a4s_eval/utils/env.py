"""Environment configuration module for A4S Evaluation.

This module defines environment variables and their default values used throughout
the A4S evaluation system. These can be overridden by setting actual environment
variables.
"""

import os
from urllib.parse import quote
from a4s_eval.utils.logging import get_logger

logger = get_logger()

API_URL = os.getenv("API_URL", "http://a4s-api:8000")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
API_URL_PREFIX = f"{API_URL}{API_PREFIX}"
CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/cache")


# Redis configuration
def get_redis_backend_url():
    """Construct Redis backend URL with SSL and auth support for AWS"""
    # Try direct URL first
    redis_url = os.getenv("REDIS_BACKEND_URL")
    if redis_url:
        return redis_url

    # For AWS, construct from individual components
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_ssl = os.getenv("REDIS_SSL", "false").lower() == "true"
    redis_auth_enabled = os.getenv("REDIS_AUTH_ENABLED", "false").lower() == "true"
    redis_auth_token = os.getenv("REDIS_AUTH_TOKEN", "")

    if redis_host:
        logger.debug(
            f"Constructing Redis URL: host={redis_host}, port={redis_port}, ssl={redis_ssl}, auth={redis_auth_enabled}"
        )

        if redis_ssl:
            # For SSL Redis, we need to add ssl_cert_reqs parameter for Celery
            scheme = "rediss"
            ssl_params = "?ssl_cert_reqs=none"

            if redis_auth_enabled and redis_auth_token:
                return f"{scheme}://:{redis_auth_token}@{redis_host}:{redis_port}/1{ssl_params}"
            else:
                return f"{scheme}://{redis_host}:{redis_port}/1{ssl_params}"
        else:
            # Non-SSL Redis
            scheme = "redis"
            if redis_auth_enabled and redis_auth_token:
                return f"{scheme}://:{redis_auth_token}@{redis_host}:{redis_port}/1"
            else:
                return f"{scheme}://{redis_host}:{redis_port}/1"

    # Fallback to default for local development
    return "redis://redis:6379/1"


REDIS_BACKEND_URL = get_redis_backend_url()


# Celery Broker URL - construct from environment variables or use default
def get_celery_broker_url():
    """Construct Celery broker URL from environment variables."""
    # Try to get the direct URL first
    broker_url = os.getenv("CELERY_BROKER_URL")
    if broker_url:
        logger.debug(f"Using direct CELERY_BROKER_URL: {broker_url}")
        return broker_url

    # Construct from separate environment variables
    mq_username = os.getenv("MQ_USERNAME", "guest")
    mq_password = os.getenv("MQ_PASSWORD", "guest")
    mq_amqps_endpoint = os.getenv("MQ_AMQPS_ENDPOINT")
    mq_amqp_endpoint = os.getenv("MQ_AMQP_ENDPOINT")
    mq_use_ssl = os.getenv("MQ_USE_SSL", "false").lower() == "true"

    logger.debug(f"MQ_USERNAME: {mq_username}")
    logger.debug(f"MQ_PASSWORD: {'*' * len(mq_password) if mq_password else 'None'}")
    logger.debug(f"MQ_AMQPS_ENDPOINT: {mq_amqps_endpoint}")
    logger.debug(f"MQ_AMQP_ENDPOINT: {mq_amqp_endpoint}")
    logger.debug(f"MQ_USE_SSL: {mq_use_ssl}")

    # URL encode the password to handle special characters
    encoded_password = quote(mq_password) if mq_password else "guest"
    logger.debug(
        f"Encoded password: {'*' * len(encoded_password) if encoded_password != 'guest' else 'guest'}"
    )

    # Choose endpoint based on SSL preference or what's available
    if mq_use_ssl and mq_amqps_endpoint:
        logger.debug(f"Using dedicated AMQPS endpoint: {mq_amqps_endpoint}")
        endpoint = mq_amqps_endpoint.replace("amqps://", "")  # Remove scheme if present
        if ":" in endpoint:
            hostname, port = endpoint.split(":", 1)
            result = f"amqps://{mq_username}:{encoded_password}@{hostname}:{port}"
        else:
            result = f"amqps://{mq_username}:{encoded_password}@{endpoint}:5671"
        logger.debug(f"Constructed AMQPS URL: {result}")
        return result
    elif mq_amqp_endpoint:
        logger.debug(f"Using AMQP endpoint: {mq_amqp_endpoint}")

        if mq_amqp_endpoint.startswith("amqps://"):
            # This is actually an AMQPS endpoint
            endpoint = mq_amqp_endpoint.replace("amqps://", "")
            if ":" in endpoint:
                hostname, port = endpoint.split(":", 1)
                result = f"amqps://{mq_username}:{encoded_password}@{hostname}:{port}"
            else:
                result = f"amqps://{mq_username}:{encoded_password}@{endpoint}:5671"
            logger.debug(f"Constructed AMQPS URL from AMQP endpoint: {result}")
            return result
        else:
            # This is a regular AMQP endpoint
            endpoint = mq_amqp_endpoint.replace("amqp://", "")
            if ":" in endpoint:
                hostname, port = endpoint.split(":", 1)
                result = f"amqp://{mq_username}:{encoded_password}@{hostname}:{port}"
            else:
                result = f"amqp://{mq_username}:{encoded_password}@{endpoint}:5672"
            logger.debug(f"Constructed AMQP URL: {result}")
            return result
    else:
        # Default for development
        logger.debug("No MQ endpoints found, using default localhost")
        return "amqp://guest:guest@localhost:5672//"


CELERY_BROKER_URL = get_celery_broker_url()
