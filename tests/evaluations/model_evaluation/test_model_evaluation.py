import uuid

import numpy as np
import pandas as pd
import pytest
import onnxruntime as ort

from a4s_eval.data_model.evaluation import Dataset, DataShape, Model
from a4s_eval.evaluations.model_evaluation.perf_evaluation import (
    empty_model_evaluator,
)


@pytest.fixture
def data_shape() -> DataShape:
    metadata = pd.read_csv("tests/data/lcld_v2_metadata_api.csv").to_dict(
        orient="records"
    )

    for record in metadata:
        record["pid"] = uuid.uuid4()

    data_shape = {
        "features": [
            item
            for item in metadata
            if item.get("name") not in ["charged_off", "issue_d"]
        ],
        "target": next(rec for rec in metadata if rec.get("name") == "charged_off"),
        "date": next(rec for rec in metadata if rec.get("name") == "issue_d"),
    }

    return DataShape.model_validate(data_shape)


@pytest.fixture
def test_dataset(data_shape: DataShape) -> Dataset:
    data = pd.read_csv("./tests/data/lcld_v2_test_400.csv")
    data["issue_d"] = pd.to_datetime(data["issue_d"])
    return Dataset(pid=uuid.uuid4(), shape=data_shape, data=data)


@pytest.fixture
def ref_dataset(data_shape: DataShape) -> Dataset:
    data = pd.read_csv("./tests/data/lcld_v2_train_800.csv")
    data["issue_d"] = pd.to_datetime(data["issue_d"])
    return Dataset(
        pid=uuid.uuid4(),
        shape=data_shape,
        data=data,
    )


@pytest.fixture
def ref_model(ref_dataset: Dataset) -> Model:
    model = ort.InferenceSession('./tests/data/lcld_v2_random_forest.onnx')
    return Model(
        pid=uuid.uuid4(),
        model=model,
        dataset=ref_dataset,
    )


def test_smoke(ref_model: Model, test_dataset: Dataset):
    metrics = empty_model_evaluator(ref_model, test_dataset)
    assert len(metrics) == 0

