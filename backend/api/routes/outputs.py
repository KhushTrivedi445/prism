import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from prism.persistence.db import get_run
from prism.config import OUTPUTS_DIR

router = APIRouter()

@router.get("/runs/{run_id}/outputs")
def get_run_outputs(run_id: str):
    run_data = get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found.")
    return {
        "run_id": run_id,
        "outputs": run_data.get("generated_outputs", {}),
        "rendered_assets": run_data.get("rendered_assets", {})
    }

@router.get("/runs/{run_id}/provenance")
def get_run_provenance(run_id: str):
    run_data = get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found.")
    return {
        "run_id": run_id,
        "provenance": run_data.get("provenance", [])
    }

@router.get("/runs/{run_id}/fact-graph")
def get_run_fact_graph(run_id: str):
    run_data = get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found.")
    return {
        "run_id": run_id,
        "fact_graph": run_data.get("fact_graph", {})
    }

@router.get("/runs/{run_id}/guardrail")
def get_run_guardrail(run_id: str):
    run_data = get_run(run_id)
    if not run_data:
        raise HTTPException(status_code=404, detail="Run not found.")
    return {
        "run_id": run_id,
        "guardrail_result": run_data.get("guardrail_result", {}),
        "revision_count": run_data.get("revision_count", 0)
    }

@router.get("/outputs/{filename}/download")
def download_rendered_output(filename: str):
    clean_name = os.path.basename(filename)
    file_path = os.path.join(OUTPUTS_DIR, clean_name)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{clean_name}' not found.")

    ext = os.path.splitext(clean_name)[1].lower()
    media_types = {
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".md": "text/markdown",
        ".txt": "text/plain",
        ".pdf": "application/pdf"
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        filename=clean_name,
        media_type=media_type
    )
