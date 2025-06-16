import json
from typing import Annotated, Any, Callable
import uuid
from pydantic import BaseModel
import requests
import pandas as pd

from a4s_eval.utils.env import API_URL_PREFIX
from fastapi import Depends

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



def get_dataset_data(dataset_pid: str) -> pd.DataFrame:

    resp = requests.get(f"{API_URL_PREFIX}/datasets/{dataset_pid}/data", stream=True)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")
    if "parquet" in content_type:
        return pd.read_parquet(resp.raw)
    elif "csv" in content_type:
        return pd.read_csv(resp.raw)
    else:
        raise ValueError("Unsupported dataset format")


class DatasetDto(BaseModel):
    pid: uuid.UUID
    data: str

class ModelDto(BaseModel):
    pid: uuid.UUID
    data: str
    dataset: DatasetDto

class EvaluationDto(BaseModel):

    pid: uuid.UUID
    dataset: DatasetDto
    model: ModelDto


def get_evaluation_request(evaluation_pid: uuid.UUID) -> dict[str, Any]:
    resp = requests.get(f"{API_URL_PREFIX}/evaluations/{evaluation_pid}?include=dataset,model")
    resp.raise_for_status()
    return resp.json()


def get_evaluation(
    evaluation_pid: uuid.UUID,
) -> EvaluationDto:
    return EvaluationDto.model_validate(get_evaluation_request(evaluation_pid))


