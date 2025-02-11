from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class Metric(BaseModel):
    name: str
    score: float
    time: datetime

    model_id: Optional[int] = None
    feature_id: Optional[int] = None
    dataset_id: Optional[int] = None

    class Config:
        # Pydantic uses `isoformat()` for datetime by default
        json_encoders = {
            datetime: lambda v: v.isoformat()  # Converts datetime to ISO 8601 string format
        }
