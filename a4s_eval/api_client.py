from pydantic import BaseModel
import requests

from a4s_eval.utils.env import API_URL_PREFIX

class EvaluationStatusUpdateDTO(BaseModel):
    status: str


class MetricDTO(BaseModel):
    name: str
    value: float | str

def store_metric(evaluation_id, name, value):
    payload = MetricDTO(name=name, value=value).model_dump()
    # return requests.post(f"{API_URL_PREFIX}/evaluations/{evaluation_id}/metrics", json=payload)

def fetch_pending_evaluation():
    resp = requests.get(f"{API_URL_PREFIX}/evaluations?status=pending")
    if resp.status_code != 200:
        return None
    evaluations = resp.json()
    for eval in evaluations:
        if claim_evaluation(eval['pid']):
            return eval['pid']
    return None

def claim_evaluation(evaluation_pid):
    payload = EvaluationStatusUpdateDTO(status="running").model_dump()
    resp = requests.patch(f"{API_URL_PREFIX}/evaluations/{evaluation_pid}", json=payload)
    return resp.status_code == 200

def mark_completed(evaluation_pid):
    payload = EvaluationStatusUpdateDTO(status="completed").model_dump()
    return requests.patch(f"{API_URL_PREFIX}/evaluations/{evaluation_pid}", json=payload)

def mark_failed(evaluation_pid):
    payload = EvaluationStatusUpdateDTO(status="failed").model_dump()
    return requests.patch(f"{API_URL_PREFIX}/evaluations/{evaluation_pid}", json=payload)

