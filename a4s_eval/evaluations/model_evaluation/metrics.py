import numpy as np
import pandas as pd
from pandas import Timestamp
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score,
)

from a4s_eval.data_model.dataset import Feature
from a4s_eval.data_model.metric import Metric
from a4s_eval.data_model.project import Project
from a4s_eval.utils.dates import DateIterator


def robust_roc_auc_score(y_true: np.ndarray, y_pred_proba: np.ndarray) -> np.ndarray:
    if y_pred_proba.shape[1] == 2:
        y_pred_proba = y_pred_proba[:, 1]
    return roc_auc_score(y_true, y_pred_proba)


pred_classification_metric = {
    "F1": f1_score,
    "MCC": matthews_corrcoef,
    "Accuracy": accuracy_score,
    "Precision": precision_score,
    "Recall": recall_score,
}
str2proba_classification_metric = {"ROCAUC": robust_roc_auc_score}


def prediction_metric_test(
    y_true: np.ndarray, y_pred_proba: np.ndarray, current_time: Timestamp
) -> list[Metric]:
    out = []
    y_pred = np.argmax(y_pred_proba, axis=1)
    for name, score_f in pred_classification_metric.items():
        out.append(
            Metric(
                name=name,
                score=score_f(y_true, y_pred),
                time=current_time,
            )
        )

    for name, score_f in str2proba_classification_metric.items():
        out.append(
            Metric(
                name=name,
                score=score_f(y_true, y_pred_proba),
                time=current_time,
            )
        )

    return out


def prediction_test(
    project: Project,
    x_new: pd.DataFrame,
    date_feature: Feature,
    target_feature: Feature,
    y_new_pred_proba: np.ndarray,
) -> list[Metric]:
    metrics = []
    for end_date, x_curr in DateIterator(
        date_round="1 D",
        window=project.window_size,
        freq=project.frequency,
        df=x_new,
        date_feature=date_feature.name,
    ):
        y_curr = x_curr[target_feature.name].to_numpy()
        y_curr_pred_proba = y_new_pred_proba[x_curr.index]

        metrics_curr = prediction_metric_test(y_curr, y_curr_pred_proba, end_date)
        metrics.extend(metrics_curr)

    return metrics
