import uuid
import numpy as np

from a4s_eval.celery_app import celery_app
from a4s_eval.data_model.evaluation import DataShape, Feature, FeatureType
from a4s_eval.service.api_client import (
    get_dataset_data,
    get_datashape_request,
    put_datashape,
    put_datashape_status,
)


type_mapping = {
    np.int64: FeatureType.INTEGER,
    np.float64: FeatureType.FLOAT,
    str: FeatureType.CATEGORICAL,
}


@celery_app.task
def auto_discover_datashape(datashape_pid: uuid.UUID) -> None:
    data = get_datashape_request(datashape_pid)
    dataset_pid = data["dataset_pid"]
    df = get_dataset_data(dataset_pid)

    features = []
    for col in df.columns:
        if col == "issue_d" or col == "charged_off":
            continue

        _feature = Feature(
            pid=uuid.uuid4(),
            name=col,
            feature_type=type_mapping[type(df[col][0])],
            min_value=df[col].min(),
            max_value=df[col].max(),
        )
        features.append(_feature)
        print(_feature)
        print(type(df[col][0]), type_mapping[type(df[col][0])], df[col].min())

    date = Feature(
        pid=uuid.uuid4(),
        name="issue_d",
        feature_type=FeatureType.DATE,
        min_value=0,
        max_value=0,
    )
    target = Feature(
        pid=uuid.uuid4(),
        name="charged_off",
        feature_type=FeatureType.CATEGORICAL,
        min_value=0,
        max_value=0,
    )

    datashape = DataShape(features=features, date=date, target=target)

    print(datashape)
    put_datashape(datashape_pid, datashape)
    put_datashape_status(datashape_pid, "auto")
