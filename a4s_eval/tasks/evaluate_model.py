
import numpy as np
import onnxruntime as rt
import pandas as pd
import requests

from a4s_eval.data_model.metric import Metric
from a4s_eval.data_model.project import Project
from a4s_eval.models.metrics import prediction_test
from a4s_eval.utils.env import API_URL
from a4s_eval.utils.files import auto_get_read_dataset_file
from a4s_eval.utils.logging import get_logger


def post_metrics(project_id: int, metrics: list[Metric]) -> None:
    response = requests.post(
        f"{API_URL}/api/projects/{project_id}/metrics",
        json=[m.model_dump(mode="json") for m in metrics],
    )
    if response.status_code == 201:
        get_logger().info("Metrics sent successfully")
    else:
        get_logger().error(f"Failed to send metrics {response.status_code}")


def evaluate_dataset(project_id: int) -> None:
    get_logger().info(f"Starting evaluation for project {project_id}")

    # Retrieve the data

    # Run the evaluations
    response = requests.get(f"{API_URL}/api/projects/{project_id}")

    if response.status_code == 200:
        project = Project(**response.json())  # Convert API response to Pydantic object

        x_ref = auto_get_read_dataset_file(project.dataset.train_file_path)
        x_new = auto_get_read_dataset_file(project.dataset.test_file_path)

        x_ref[project.dataset.date_feature.name] = pd.to_datetime(
            x_ref[project.dataset.date_feature.name]
        )
        x_new[project.dataset.date_feature.name] = pd.to_datetime(
            x_new[project.dataset.date_feature.name]
        )

        x_test = x_new[[f.name for f in project.dataset.features]].to_numpy()

        sess = rt.InferenceSession(
            "random_forest.onnx", providers=["CPUExecutionProvider"]
        )

        input_name = sess.get_inputs()[0].name
        label_name = sess.get_outputs()[1].name
        pred_onx = sess.run([label_name], {input_name: x_test})[0]
        pred_proba = np.array([list(d.values()) for d in pred_onx])

        metrics = prediction_test(
            project,
            x_new,
            project.dataset.date_feature,
            project.dataset.target,
            pred_proba,
        )

        for m in metrics:
            m.dataset_id = project.dataset.id
        get_logger().info(f"Saving {len(metrics)} metrics.")

        post_metrics(project_id, metrics)
    else:
        get_logger().error(f"Failed to fetch data {response.status_code}")


if __name__ == "__main__":
    evaluate_dataset(1)
    get_logger().info("Task done, exiting.")
