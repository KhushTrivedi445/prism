from fastapi import APIRouter, HTTPException, Query
from typing import List

try:
    from backend.api.schemas import RunSummary, RunDetail
except ImportError:
    from api.schemas import RunSummary, RunDetail

from prism.persistence.db import list_runs, get_run, delete_run

router = APIRouter()

@router.get("/runs", response_model=List[RunSummary])
def get_all_runs(limit: int = Query(50, ge=1, le=200)):
    """
    List historical PRISM runs from SQLite database.
    """
    return list_runs(limit=limit)

@router.get("/runs/{run_id}", response_model=RunDetail)
def get_run_by_id(run_id: str):
    """
    Get complete details of a specific PRISM run.
    """
    run_data = get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return run_data

@router.delete("/runs/{run_id}")
def remove_run(run_id: str):
    """
    Delete a run record from SQLite.
    """
    success = delete_run(run_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return {"status": "deleted", "run_id": run_id}
