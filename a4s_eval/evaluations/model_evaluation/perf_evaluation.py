import pandas as pd

from a4s_eval.data_model.evaluation import Dataset, FeatureType, Model
from a4s_eval.data_model.metric import Metric
from a4s_eval.evaluations.model_evaluation.registry import model_evaluator


@model_evaluator(name="Empty model evaluator")
def empty_model_evaluator(reference: Model, evaluate: Dataset) -> list[Metric]:
    return []
