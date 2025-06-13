from celery import Celery, group
from a4s_eval.api_client import (
    fetch_pending_evaluation,
    store_metric,
    mark_completed,
    mark_failed
)
import time

from a4s_eval.utils import env

celery_app = Celery(__name__, broker=env.CELERY_BROKER_URL, backend=env.REDIS_BACKEND_URL)
# celery_app.config_from_object("celeryconfig")

@celery_app.task
def poll_and_run_evaluation():
    eval_id = fetch_pending_evaluation()
    if not eval_id:
        eval_id = 1

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
