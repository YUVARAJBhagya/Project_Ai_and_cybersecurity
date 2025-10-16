from datetime import datetime
import numpy as np
import pandas as pd

from a4s_eval.data_model.evaluation import DataShape, Dataset, Model
from a4s_eval.data_model.measure import Measure
from a4s_eval.metric_registries.model_metric_registry import model_metric
from a4s_eval.service.model_functional import FunctionalModel


@model_metric(name="accuracy")
def accuracy(
    datashape: DataShape,
    model: Model,
    dataset: Dataset,
    functional_model: FunctionalModel,
) -> list[Measure]:
    
    #my code
    feature_columns = [feature.name for feature in datashape.features]#creates the list of names of all features in datashape
    X = dataset.data[feature_columns]

# Get the actual values and predict the outputs using the model
    y_true = dataset.data[datashape.target.name]
    y_predicted = functional_model.predict(X.to_numpy())

    accuracy_score = np.mean(y_true == y_predicted)
    timestamp = datetime.now()

    return [Measure(name="accuracy", score=accuracy_score, time=timestamp)]