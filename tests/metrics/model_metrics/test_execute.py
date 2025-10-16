import uuid

import pandas as pd
from a4s_eval.metric_registries.model_metric_registry import model_metric_registry
from a4s_eval.metric_registries.model_metric_registry import ModelMetric
from a4s_eval.service.model_functional import FunctionalModel
from a4s_eval.service.model_load import load_model
import pytest

from a4s_eval.data_model.evaluation import (
    Dataset,
    DataShape,
    Model,
    ModelConfig,
    ModelFramework,
)

from tests.save_measures_utils import save_measures


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
def test_dataset(test_data: pd.DataFrame, data_shape: DataShape) -> Dataset:
    data = test_data
    data["issue_d"] = pd.to_datetime(data["issue_d"])
    return Dataset(pid=uuid.uuid4(), shape=data_shape, data=data)


@pytest.fixture
def ref_dataset(train_data, data_shape: DataShape) -> Dataset:
    data = train_data
    data["issue_d"] = pd.to_datetime(data["issue_d"])
    return Dataset(
        pid=uuid.uuid4(),
        shape=data_shape,
        data=data,
    )


@pytest.fixture
def ref_model(ref_dataset: Dataset) -> Model:
    return Model(
        pid=uuid.uuid4(),
        model=None,
        dataset=ref_dataset,
    )


@pytest.fixture
def functional_model() -> FunctionalModel:
    model_config = ModelConfig(
        path="./tests/data/lcld_v2_tabtransformer.pt", framework=ModelFramework.TORCH
    )
    return load_model(model_config)


def test_non_empty_registry():
    assert len(model_metric_registry._functions) > 0


@pytest.mark.parametrize("metric_entry", model_metric_registry)
def test_data_metric_registry_contains_evaluator_by_batch(
    metric_entry: tuple[str, ModelMetric],
    data_shape: DataShape,
    reference_model: Model,
    test_dataset: Dataset,
    functional_model: FunctionalModel,
):
    
    #My code
    
    # Create an empty list to store measure results for each batch
    
    batch_measures: list[Measure] = []

    
    BATCH_SIZE = 100
    
    
    # Loop through the dataset in batches of size BATCH_SIZE and extract the current batch of data for processing
    for batch_start in range(0, len(test_dataset.data), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(test_dataset.data))
        batch_slice = test_dataset.data.iloc[batch_start:batch_end]
        
        batch_dataset = Dataset(
            pid=uuid.uuid4(),
            shape=test_dataset.shape,
            data=batch_slice,
        )

        batch_measure = metric_entry[1](
            data_shape, reference_model, batch_dataset, functional_model
        )[0]
        batch_measures.append(batch_measure)

    metric_name = metric_entry[0] + "_by_batch"
    save_measures(metric_name, batch_measures)
    
    
    # Draw a plot showing how the metric score changes across batches

    draw_plot(
        metric_name,
        x=None,
        y="score",
        title=f"{metric_entry[0]} by batch",
        x_label=f"Batch index ({BATCH_SIZE} samples)",
        y_label=metric_entry[0],
    )

    assert len(batch_measures) > 0
