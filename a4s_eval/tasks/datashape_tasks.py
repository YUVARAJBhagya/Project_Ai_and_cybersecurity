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
from a4s_eval.utils.logging import get_logger


type_mapping = {
    "int64": FeatureType.INTEGER,
    "float64": FeatureType.FLOAT,
    "object": FeatureType.DATE,
}


@celery_app.task
def auto_discover_datashape(datashape_pid: uuid.UUID) -> None:
    try:
        data = get_datashape_request(datashape_pid)
        dataset_pid = data["dataset_pid"]
        df = get_dataset_data(dataset_pid)

        date = None
        features = []
        for col in df.columns:
            col_type = str(df[col].dtype)
            _feature = Feature(
                pid=uuid.uuid4(),
                name=col,
                feature_type=type_mapping[col_type],
                min_value=df[col].min(),
                max_value=df[col].max(),
            )
            if type_mapping[col_type] == FeatureType.DATE:
                _feature.min_value = 0
                _feature.max_value = 0
                date = _feature
                continue  # Skip date features for now
            features.append(_feature)

        datashape = DataShape(features=features, date=date, target=None)

        get_logger().debug(datashape.model_dump_json())
        put_datashape(datashape_pid, datashape)
        put_datashape_status(datashape_pid, "auto")
    except Exception as e:
        get_logger().error(
            f"Error during auto-discovery of datashape {datashape_pid}: {e}"
        )
        put_datashape_status(datashape_pid, "failed")
