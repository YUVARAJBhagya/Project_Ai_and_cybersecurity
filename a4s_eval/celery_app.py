from celery import Celery
import logging

from a4s_eval.utils import env

import requests

def is_running_on_aws():
    try:
        response = requests.get("http://169.254.169.254/latest/meta-data/", timeout=0.1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Add logging to debug Redis URL
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"CELERY REDIS BACKEND URL: {env.REDIS_BACKEND_URL}")
logger.info("=== CELERY APP INITIALIZATION ===")

celery_app: Celery = Celery(
    __name__, broker=env.CELERY_BROKER_URL, backend=env.REDIS_BACKEND_URL
)

logger.info("=== CELERY APP CREATED ===")

# Configure Celery settings for 30-minute task execution with heartbeat
celery_config = {
    "task_acks_late": True,  # Acknowledge task only after completion
    "worker_prefetch_multiplier": 1,  # Process one task at a time
    "task_soft_time_limit": 1800,  # 30 minutes soft limit
    "task_time_limit": 2100,  # 35 minutes hard limit (buffer for cleanup)
}

# Only add SSL configuration in production
if is_running_on_aws():
    celery_config["broker_transport_options"] = {
        "ssl": {
            "cert_reqs": 0,  # CERT_NONE as integer
            "ca_certs": None,
            "certfile": None,
            "keyfile": None,
        }
    }

celery_app.conf.update(celery_config)

logger.info("=== CELERY CONFIGURATION COMPLETED ===")
