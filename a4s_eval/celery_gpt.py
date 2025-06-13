### Directory Structure

# fastapi_celery_eval/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py              # FastAPI entry (optional for triggering manually)
# │   ├── tasks.py             # Celery tasks using external API
# │   ├── api_client.py        # Utility for interacting with evaluation API
# │   └── schemas.py           # Pydantic DTOs
# ├── celery_worker.py         # Worker startup script
# ├── celeryconfig.py          # Celery settings
# └── requirements.txt

# --- app/schemas.py ---
from pydantic import BaseModel
from typing import Union

class MetricDTO(BaseModel):
    name: str
    value: Union[float, str]

class EvaluationStatusUpdateDTO(BaseModel):
    status: str

# --- app/api_client.py ---
import requests
from app.schemas import MetricDTO, EvaluationStatusUpdateDTO

API_URL = "http://api:8000/api/v1/evaluations"

def fetch_pending_evaluation():
    resp = requests.get(f"{API_URL}?status=pending")
    if resp.status_code != 200:
        return None
    evaluations = resp.json()
    for eval in evaluations:
        if claim_evaluation(eval['id']):
            return eval['id']
    return None

def claim_evaluation(eval_id):
    payload = EvaluationStatusUpdateDTO(status="running").dict()
    resp = requests.patch(f"{API_URL}/{eval_id}", json=payload)
    return resp.status_code == 200

def store_metric(evaluation_id, name, value):
    payload = MetricDTO(name=name, value=value).dict()
    return requests.post(f"{API_URL}/{evaluation_id}/metrics", json=payload)

def mark_completed(evaluation_id):
    payload = EvaluationStatusUpdateDTO(status="completed").dict()
    return requests.patch(f"{API_URL}/{evaluation_id}", json=payload)

def mark_failed(evaluation_id):
    payload = EvaluationStatusUpdateDTO(status="failed").dict()
    return requests.patch(f"{API_URL}/{evaluation_id}", json=payload)

# --- app/tasks.py ---
from celery import Celery, group
from app.api_client import (
    fetch_pending_evaluation,
    store_metric,
    mark_completed,
    mark_failed
)
import time

celery_app = Celery(__name__, broker="redis://localhost:6379/0")
celery_app.config_from_object("celeryconfig")

@celery_app.task
def poll_and_run_evaluation():
    eval_id = fetch_pending_evaluation()
    if not eval_id:
        return

    tasks = group([
        compute_accuracy.s(eval_id),
        compute_f1.s(eval_id),
        compute_conf_matrix.s(eval_id),
    ])
    (tasks | finalize_evaluation.s(eval_id)).apply_async()

@celery_app.task
def compute_accuracy(evaluation_id):
    time.sleep(1)
    store_metric(evaluation_id, "accuracy", 0.92)

@celery_app.task
def compute_f1(evaluation_id):
    time.sleep(1)
    store_metric(evaluation_id, "f1", 0.88)

@celery_app.task
def compute_conf_matrix(evaluation_id):
    time.sleep(1)
    store_metric(evaluation_id, "confusion_matrix", "[[50,10],[5,100]]")

@celery_app.task
def finalize_evaluation(results, evaluation_id):
    try:
        mark_completed(evaluation_id)
    except Exception:
        mark_failed(evaluation_id)

# --- celery_worker.py ---
from app.tasks import celery_app

celery_app.worker_main()

# --- celeryconfig.py ---
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
