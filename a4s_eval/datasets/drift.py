from datetime import datetime
import pandas as pd
from scipy.stats import wasserstein_distance
from scipy.spatial.distance import jensenshannon

from a4s_eval.data_model.dataset import Feature, FeatureType
from a4s_eval.data_model.metric import Metric
from a4s_eval.data_model.project import Project
from a4s_eval.utils.dates import DateIterator


def numerical_drift_test(x_ref: pd.Series, x_new: pd.Series) -> float:
    return wasserstein_distance(x_ref, x_new)


def categorical_drift_test(x_ref: pd.Series, x_new: pd.Series) -> float:
    return jensenshannon(x_ref, x_new)


def numerical_drift_metric(
    x_ref: pd.Series, x_new: pd.Series, time: datetime
) -> Metric:
    drift = numerical_drift_test(x_ref, x_new)
    return Metric(
        name="wasserstein_distance",
        score=drift,
        time=time,
    )


def feature_drift_test(
    x_ref: pd.Series,
    x_new: pd.Series,
    feature_type: FeatureType,
    date: pd.Timestamp,
) -> Metric:
    if feature_type == FeatureType.INTEGER or feature_type == FeatureType.FLOAT:
        return Metric(
            name="wasserstein_distance",
            score=numerical_drift_test(x_ref, x_new),
            time=date.to_pydatetime(),
        )

    elif feature_type == FeatureType.CATEGORICAL:
        return Metric(
            name="jensenshannon",
            score=numerical_drift_test(x_ref, x_new),
            time=date.to_pydatetime(),
        )
    else:
        raise ValueError(f"Feature type {feature_type} not supported")


def data_drift_test(
    project: Project,
    x_ref: pd.DataFrame,
    x_new: pd.DataFrame,
    features: list[Feature],
    date_feature: Feature,
) -> list[Metric]:
    metrics = []
    for end_date, x_curr in DateIterator(
        date_round="1 D",
        window=project.window_size,
        freq=project.frequency,
        df=x_new,
        date_feature=date_feature.name,
    ):
        x_curr_distribution = pd.concat([x_ref, x_curr], axis=0)

        for feature in features:
            feature_type = feature.feature_type
            x_ref_feature = x_ref[feature.name]
            x_new_feature = x_curr_distribution[feature.name]

            metric = feature_drift_test(
                x_ref_feature, x_new_feature, feature_type, end_date
            )
            metric.feature_id = feature.id
            metric.dataset_id = project.dataset.id
            metrics.append(metric)
    
    return metrics
