import os
import uuid
import json
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body

try:
    from backend.api.schemas import GenerateRequest, RunDetail
except ImportError:
    from api.schemas import GenerateRequest, RunDetail

from prism.state import PRISMState
from prism.graph import prism_app
from prism.persistence.db import get_run
from prism.config import OUTPUTS_DIR

router = APIRouter()
UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
os.makedirs(UPLOADS_DIR, exist_ok=True)

@router.post("/generate", response_model=RunDetail)
def generate_content(request: GenerateRequest):
    """
    JSON generation endpoint for direct source text input.
    """
    if not request.input_text or not request.input_text.strip():
        raise HTTPException(status_code=400, detail="Source text cannot be empty.")

    if not request.selected_outputs:
        raise HTTPException(status_code=400, detail="Please select at least one output channel.")

    if request.model:
        os.environ["PRISM_GROQ_MODEL"] = request.model

    run_id = f"run_{uuid.uuid4().hex[:8]}"

    initial_state: PRISMState = {
        "input_type": "text",
        "file_path": None,
        "input_text": request.input_text.strip(),
        "source_text": "",
        "normalized_text": "",
        "fact_graph": {},
        "tone": request.tone,
        "audience": request.audience,
        "objective": request.objective or "Multi-channel synthesis",
        "selected_outputs": request.selected_outputs,
        "linkedin_output": None,
        "twitter_output": None,
        "summary_output": None,
        "advisory_output": None,
        "presentation_output": None,
        "pptx_path": None,
        "guardrail_result": None,
        "failed_output": None,
        "revision_count": 0,
        "provenance": [],
        "rag_chunks": [],
        "rag_vector_store": None,
        "rag_retriever": None,
        "run_id": run_id,
        "rendered_assets": {}
    }

    try:
        final_state = prism_app.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis pipeline error: {str(e)}")

    saved_run = get_run(run_id)
    if not saved_run:
        raise HTTPException(status_code=500, detail="Failed to retrieve persisted run.")

    return saved_run


@router.post("/generate/upload", response_model=RunDetail)
def generate_from_upload(
    file: UploadFile = File(...),
    tone: str = Form("Professional"),
    audience: str = Form("Enterprise Executives"),
    objective: Optional[str] = Form("Multi-channel synthesis"),
    selected_outputs: str = Form("[\"linkedin\",\"summary\",\"presentation\"]"),
    model: Optional[str] = Form("openai/gpt-oss-120b")
):
    """
    Multipart form-data generation endpoint for PDF, DOCX, and TXT files.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format '{ext}'. Allowed: .pdf, .docx, .txt")

    file_id = str(uuid.uuid4())[:8]
    dest_path = os.path.join(UPLOADS_DIR, f"{file_id}_{file.filename}")
    
    contents = file.file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    try:
        parsed_outputs = json.loads(selected_outputs)
        if isinstance(parsed_outputs, str):
            parsed_outputs = [parsed_outputs]
    except Exception:
        parsed_outputs = [s.strip() for s in selected_outputs.split(",") if s.strip()]

    if not parsed_outputs:
        raise HTTPException(status_code=400, detail="Please select at least one output channel.")

    if model:
        os.environ["PRISM_GROQ_MODEL"] = model

    run_id = f"run_{uuid.uuid4().hex[:8]}"

    initial_state: PRISMState = {
        "input_type": "file",
        "file_path": dest_path,
        "input_text": None,
        "source_text": "",
        "normalized_text": "",
        "fact_graph": {},
        "tone": tone,
        "audience": audience,
        "objective": objective or "Multi-channel synthesis",
        "selected_outputs": parsed_outputs,
        "linkedin_output": None,
        "twitter_output": None,
        "summary_output": None,
        "advisory_output": None,
        "presentation_output": None,
        "pptx_path": None,
        "guardrail_result": None,
        "failed_output": None,
        "revision_count": 0,
        "provenance": [],
        "rag_chunks": [],
        "rag_vector_store": None,
        "rag_retriever": None,
        "run_id": run_id,
        "rendered_assets": {}
    }

    try:
        final_state = prism_app.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File synthesis error: {str(e)}")

    saved_run = get_run(run_id)
    if not saved_run:
        raise HTTPException(status_code=500, detail="Failed to retrieve persisted run.")

    return saved_run
