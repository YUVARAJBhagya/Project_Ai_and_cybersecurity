from pydantic import BaseModel, Field


class Model(BaseModel):
    id: int
    name: str
    file_path: str | None = Field(default=None)
