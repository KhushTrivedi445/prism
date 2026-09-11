from fastapi import APIRouter
from typing import List

try:
    from backend.api.schemas import ModelInfo
except ImportError:
    from api.schemas import ModelInfo

router = APIRouter()

AVAILABLE_MODELS = [
    ModelInfo(
        id="openai/gpt-oss-120b",
        name="GPT-OSS 120B (Groq)",
        provider="Groq Cloud",
        description="State-of-the-art 120B model for deep structured extraction and synthesis",
        context_window="32k tokens",
        recommended=True
    ),
    ModelInfo(
        id="openai/gpt-oss-20b",
        name="GPT-OSS 20B (Groq)",
        provider="Groq Cloud",
        description="Fast, high-accuracy reasoning and structured synthesis model",
        context_window="32k tokens",
        recommended=False
    ),
    ModelInfo(
        id="groq/compound",
        name="Groq Compound",
        provider="Groq Cloud",
        description="Compound reasoning agent model optimized for multi-channel workflows",
        context_window="64k tokens",
        recommended=False
    ),
    ModelInfo(
        id="qwen/qwen3.8-27b",
        name="Qwen 3.8 27B",
        provider="Groq Cloud",
        description="High-performance multilingual structured generation model",
        context_window="32k tokens",
        recommended=False
    )
]

@router.get("/models", response_model=List[ModelInfo])
def list_models():
    """
    Returns public model catalog. API keys and secrets are NEVER exposed.
    """
    return AVAILABLE_MODELS
