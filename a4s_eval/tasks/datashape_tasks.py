import uuid
import numpy as np

import requests

from a4s_eval.celery_app import celery_app
from a4s_eval.data_model.evaluation import Dataset, DataShape, Feature, FeatureType
from a4s_eval.utils.env import API_URL_PREFIX
from a4s_eval.service.api_client import (
    get_dataset_data,
)


type_mapping = {
    np.int64: FeatureType.INTEGER,
    np.float64: FeatureType.FLOAT,
    str: FeatureType.CATEGORICAL,
}

@celery_app.task
def auto_discover_datashape(
    dataset_pid: uuid.UUID
) -> None:
    df = get_dataset_data(dataset_pid)
    print(df.keys())

    features = []
    for col in df.columns:
        if col == "issue_d" or col == "charged_off":
            continue

        _feature = Feature(
            name=col,
            feature_type=type_mapping[type(df[col][0])],
            min_value=df[col].min(),
            max_value=df[col].max(),
        )
        features.append(_feature)
        print(_feature)
        print(type(df[col][0]), type_mapping[type(df[col][0])], df[col].min())
        
    date = Feature(
        name="issue_d",
        feature_type=FeatureType.DATE,
        min_value=0,
        max_value=0,
    )
    target = Feature(
        name="charged_off",
        feature_type=FeatureType.CATEGORICAL,
        min_value=0,
        max_value=0,
    )

    datashape = DataShape(
        features=features,
        date=date,
        target=target
    )

    print(datashape.model_dump_json())