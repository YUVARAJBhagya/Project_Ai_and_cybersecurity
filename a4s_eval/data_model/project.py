from pydantic import BaseModel

from a4s_eval.data_model.dataset import Dataset


class Project(BaseModel):
    name: str
    frequency: str
    window_size: str
    # dataset_id: int
    # model_id: int

    dataset: Dataset