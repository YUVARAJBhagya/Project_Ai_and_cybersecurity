import enum
from pydantic import BaseModel


class FeatureType(str, enum.Enum):
    INTEGER = "integer"
    FLOAT = "float"
    CATEGORICAL = "categorical"


class Feature(BaseModel):
    id: int
    name: str
    feature_type: FeatureType
    min_value: float
    max_value: float


class Dataset(BaseModel):
    id: int

    name: str
    train_file_path: str
    test_file_path: str

    features: list[Feature]
    target: Feature
    date_feature: Feature
