import uuid
from fastapi import APIRouter

from a4s_eval.tasks.datashape_tasks import auto_discover_datashape

router = APIRouter(tags=["datashapes"])


@router.get("/datashape/autodiscover")
async def autodiscover(
    dataset_pid: uuid.UUID,
    datashape_pid: uuid.UUID | None = None,
) -> dict[str, str]:
    auto_discover_datashape(dataset_pid)
    return {"message": "discovery started."}
