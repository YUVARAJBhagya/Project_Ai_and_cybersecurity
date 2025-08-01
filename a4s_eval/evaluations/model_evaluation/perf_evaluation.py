import pandas as pd
import numpy as np

from a4s_eval.data_model.evaluation import Dataset, FeatureType, Model
from a4s_eval.data_model.metric import Metric
from a4s_eval.evaluations.model_evaluation.registry import model_evaluator
from a4s_eval.evaluations.model_evaluation.metrics import prediction_metric_test


@model_evaluator(name="Empty model evaluator")
def empty_model_evaluator(reference: Model, evaluate: Dataset, y_pred_proba: np.ndarray) -> list[Metric]:
    return []


@model_evaluator(name="Performance evaluator")
def model_perf_evaluator(reference: Model, evaluate: Dataset, y_pred_proba: np.ndarray) -> list[Metric]:
    date = pd.to_datetime(evaluate.data[evaluate.shape.date.name]).max()
    y_true = evaluate.data[evaluate.shape.target.name].to_numpy()

    metrics = prediction_metric_test(
        y_true, 
        y_pred_proba, 
        date
    )    

    return metrics
