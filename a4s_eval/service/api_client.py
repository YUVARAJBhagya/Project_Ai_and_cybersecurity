import uuid
from io import BytesIO
from typing import Any

import pandas as pd
import requests
from pydantic import BaseModel

from a4s_eval.data_model.evaluation import Evaluation
from a4s_eval.data_model.metric import Metric
from a4s_eval.utils.env import API_URL_PREFIX


class EvaluationStatusUpdateDTO(BaseModel):
    status: str


class MetricDTO(BaseModel):
    name: str
    value: float | str


def fetch_pending_evaluations() -> list[uuid.UUID]:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== FETCH_PENDING_EVALUATIONS START ===")
        logger.info(f"1. About to call API: {API_URL_PREFIX}/evaluations?status=pending")
        
        resp = requests.get(f"{API_URL_PREFIX}/evaluations?status=pending", timeout=30)
        logger.info(f"2. API call completed. Status: {resp.status_code}")
        
        if resp.status_code != 200:
            logger.error(f"3. API returned non-200 status: {resp.status_code}")
            return []
        
        evaluations = resp.json()
        logger.info(f"4. Parsed evaluations: {evaluations}")
        
        claimed_pids = []
        logger.info(f"5. Processing {len(evaluations)} evaluations...")
        
        for i, e in enumerate(evaluations):
            logger.info(f"6.{i+1} Processing evaluation: {e}")
            try:
                if claim_evaluation(e["evaluation_pid"]):
                    claimed_pids.append(uuid.UUID(e["evaluation_pid"]))
                    logger.info(f"7.{i+1} Successfully claimed evaluation: {e['evaluation_pid']}")
                else:
                    logger.warning(f"8.{i+1} Failed to claim evaluation: {e['evaluation_pid']}")
            except Exception as e:
                logger.error(f"ERROR processing evaluation {e}: {str(e)}")
        
        logger.info(f"9. Final claimed_pids: {claimed_pids}")
        return claimed_pids
        
    except Exception as e:
        logger.error(f"ERROR in fetch_pending_evaluations: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []
    finally:
        logger.info("=== FETCH_PENDING_EVALUATIONS END ===")


def claim_evaluation(evaluation_pid: uuid.UUID) -> bool:
    print(f"Claiming evaluation {evaluation_pid}")
    resp = requests.put(
        f"{API_URL_PREFIX}/evaluations/{evaluation_pid}?status=processing"
    )
    print(f"Claim response status: {resp.status_code}")
    success = resp.status_code == 200
    if success:
        print(f"Successfully claimed evaluation {evaluation_pid}")
    else:
        print(f"Failed to claim evaluation {evaluation_pid}")
    return success


def mark_completed(evaluation_pid: uuid.UUID) -> requests.Response:
    return requests.put(f"{API_URL_PREFIX}/evaluations/{evaluation_pid}?status=done")


def mark_failed(evaluation_pid: uuid.UUID) -> None:
    payload = EvaluationStatusUpdateDTO(status="failed").model_dump()
    return requests.put(f"{API_URL_PREFIX}/evaluations/{evaluation_pid}", json=payload)


def get_dataset_data(dataset_pid: str) -> pd.DataFrame:
    resp = requests.get(f"{API_URL_PREFIX}/datasets/{dataset_pid}/data", stream=True)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "")

    if "parquet" in content_type:
        content_buffer = BytesIO(resp.content)
        content_buffer.seek(0)
        return pd.read_parquet(content_buffer)
    elif "csv" in content_type:
        content_buffer = BytesIO(resp.content)
        content_buffer.seek(0)
        return pd.read_csv(content_buffer)
    else:
        raise ValueError("Unsupported dataset format")


def get_evaluation_request(evaluation_pid: uuid.UUID) -> dict[str, Any]:
    resp = requests.get(
        f"{API_URL_PREFIX}/evaluations/{evaluation_pid}?include=project,dataset,model,datashape"
    )
    resp.raise_for_status()
    return resp.json()


def get_evaluation(
    evaluation_pid: uuid.UUID,
) -> Evaluation:
    return Evaluation.model_validate(get_evaluation_request(evaluation_pid))


def post_metrics(evaluation_pid: uuid.UUID, metrics: list[Metric]) -> requests.Response:
    print(
        f"post_metrics called with {len(metrics)} metrics for evaluation {evaluation_pid}"
    )

    payload = [metric.model_dump() for metric in metrics]
    print(f"Payload prepared, size: {len(payload)}")

    if len(payload) > 0:
        print(f"Sample payload item: {payload[0]}")

    url = f"{API_URL_PREFIX}/evaluations/{evaluation_pid}/metrics"
    print(f"Posting to URL: {url}")

    response = requests.post(url, json=payload)

    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response content: {response.text}")

    if response.status_code != 201:
        print(f"ERROR: Expected status 201, got {response.status_code}")
        print(f"Response content: {response.content}")
        raise ValueError(response.content)

    return response
