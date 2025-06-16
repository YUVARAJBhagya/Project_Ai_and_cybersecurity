


import io
from unittest.mock import Mock, patch, MagicMock

from a4s_eval.service.api_client import get_dataset_data, get_evaluation
import uuid


TEST_UUIDS = {
    "evaluation": uuid.UUID("afb49e3f-813d-4260-9919-ee179d1090e6"),
    "test_dataset": uuid.UUID("750ec557-fd8c-4f94-92b9-28796591fd40"),
    "train_dataset": uuid.UUID("d830c991-88a5-4cb3-906a-9aa6e2a8c63f"),
    "model": uuid.UUID("08947de5-bcc2-4fee-8717-deb3f8bc86f9")
}

def test_get_evaluation():

    mock_data = {
        "pid": str(TEST_UUIDS["evaluation"]),
        "dataset": {
            "pid": str(TEST_UUIDS["test_dataset"]),
            "data": ""
        },
        "model": {
            "pid": str(TEST_UUIDS["model"]),
            "data": "",
            "dataset": {
                "pid": str(TEST_UUIDS["train_dataset"]),
                "data": "",
            }
        }
    }

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_data
    with patch('requests.get', return_value=mock_response):
        evaluation = get_evaluation(TEST_UUIDS["evaluation"])

        # Now evaluation should be an EvaluationDto object built from mock_response
        assert evaluation.pid == TEST_UUIDS["evaluation"]



def test_get_dataset():

    test_uuid = TEST_UUIDS["evaluation"]
    with open("./tests/data/lcld_v2_train_800.csv", "r") as f:
        csv_data = f.read()


    # Prepare mock response
    mock_resp = MagicMock()
    mock_resp.headers = {"Content-Type": "text/csv"}
    mock_resp.status_code = 200
    mock_resp.raw = io.StringIO(csv_data)
    # mock_resp.raise_for_status = MagicMock()

    # Set the mock return value
    # mock_get.return_value = mock_resp
    with patch('requests.get', return_value=mock_resp):
        df = get_dataset_data(TEST_UUIDS["train_dataset"])

        assert len(df) == 800
