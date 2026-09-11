from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    input_type: str = Field(default="text", description="'text' or 'file'")
    input_text: Optional[str] = Field(default=None, description="Raw source text to synthesize")
    tone: str = Field(default="Professional", description="Tone of voice")
    audience: str = Field(default="Enterprise Executives", description="Target audience")
    objective: Optional[str] = Field(default="Multi-channel synthesis", description="Strategic objective")
    selected_outputs: List[str] = Field(default=["linkedin", "summary", "presentation"], description="Output channels to generate")
    model: Optional[str] = Field(default="openai/gpt-oss-120b", description="Model identifier to use")

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    description: str
    context_window: str
    recommended: bool

class RunSummary(BaseModel):
    run_id: str
    created_at: str
    input_type: str
    tone: str
    audience: str
    selected_outputs: List[str]
    revision_count: int

class RunDetail(BaseModel):
    run_id: str
    created_at: str
    input_type: str
    source_text: str
    normalized_text: str
    tone: str
    audience: str
    objective: Optional[str]
    selected_outputs: List[str]
    fact_graph: Dict[str, Any]
    generated_outputs: Dict[str, Any]
    guardrail_result: Dict[str, Any]
    revision_count: int
    provenance: List[Dict[str, Any]]
    rendered_assets: Dict[str, str]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    database: str
    prism_engine: str
