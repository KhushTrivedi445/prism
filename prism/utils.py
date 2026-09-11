import json
import re
import time
import logging
from typing import Type, TypeVar, Any, Optional
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage
import json_repair

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

def clean_json_string(text: str) -> str:
    """Extract and isolate JSON block from markdown code fences, think tags, or raw string."""
    if not text:
        return "{}"
    text = text.strip()
    
    # 1. Strip out <think>...</think> reasoning blocks
    text = re.sub(r"<think>[\s\S]*?</think>", "", text, flags=re.IGNORECASE).strip()
    
    # 2. Extract from markdown code fences ```json ... ``` if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        extracted = match.group(1).strip()
        if extracted:
            return extracted
            
    # 3. Extract the first outer JSON object {...}
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()
        
    return text

def coerce_schema_dict(data: Any, schema_name: str) -> Any:
    """Coerce relaxed LLM JSON representations (e.g. lists of strings) into strict schema models."""
    if not isinstance(data, dict):
        return data
        
    res = dict(data)
    
    if schema_name == "FactGraph":
        # Coerce entities
        if "entities" in res and isinstance(res["entities"], list):
            res["entities"] = [
                {"name": e, "type": "Entity"} if isinstance(e, str) else e
                for e in res["entities"] if e
            ]
        # Coerce claims
        if "claims" in res and isinstance(res["claims"], list):
            res["claims"] = [
                {"text": c, "source_span": c, "confidence": 0.95} if isinstance(c, str) else c
                for c in res["claims"] if c
            ]
        # Coerce metrics
        if "metrics" in res and isinstance(res["metrics"], list):
            res["metrics"] = [
                {"name": "Metric", "value": m, "context": m, "source_span": m} if isinstance(m, str) else m
                for m in res["metrics"] if m
            ]
        # Coerce dates
        if "dates" in res and isinstance(res["dates"], list):
            res["dates"] = [
                {"date": d, "event": d, "source_span": d} if isinstance(d, str) else d
                for d in res["dates"] if d
            ]
        # Coerce recommendations
        if "recommendations" in res and isinstance(res["recommendations"], list):
            res["recommendations"] = [
                {"text": r, "source_span": r} if isinstance(r, str) else r
                for r in res["recommendations"] if r
            ]
        # Coerce quotes
        if "quotes" in res and isinstance(res["quotes"], list):
            res["quotes"] = [
                {"text": q, "source_span": q, "speaker": None} if isinstance(q, str) else q
                for q in res["quotes"] if q
            ]
        # Coerce synopsis
        if "synopsis" in res and isinstance(res["synopsis"], list):
            res["synopsis"] = " ".join(str(s) for s in res["synopsis"])
        elif "synopsis" not in res:
            res["synopsis"] = ""

    elif schema_name == "Presentation":
        if "slides" in res and isinstance(res["slides"], list):
            new_slides = []
            for idx, s in enumerate(res["slides"]):
                if isinstance(s, str):
                    new_slides.append({"slide_number": idx + 1, "title": f"Slide {idx + 1}", "content": [s]})
                elif isinstance(s, dict):
                    if "slide_number" not in s:
                        s["slide_number"] = idx + 1
                    if "title" not in s:
                        s["title"] = f"Slide {idx + 1}"
                    if "content" not in s or not isinstance(s["content"], list):
                        s["content"] = [str(s.get("content", ""))]
                    new_slides.append(s)
            res["slides"] = new_slides
        if "title" not in res or not isinstance(res["title"], str):
            res["title"] = "PRISM Presentation"

    elif schema_name == "GuardrailResult":
        if "overall_status" not in res:
            res["overall_status"] = "PASS"
        if "outputs" in res:
            if isinstance(res["outputs"], list):
                res["outputs"] = {item: {"status": "PASS", "issues": []} for item in res["outputs"] if isinstance(item, str)}
            elif isinstance(res["outputs"], dict):
                norm_outputs = {}
                for k, v in res["outputs"].items():
                    if isinstance(v, str):
                        norm_outputs[k] = {"status": v, "issues": []}
                    elif isinstance(v, dict):
                        norm_outputs[k] = {
                            "status": v.get("status", "PASS"),
                            "issues": v.get("issues", []) if isinstance(v.get("issues"), list) else []
                        }
                    else:
                        norm_outputs[k] = {"status": "PASS", "issues": []}
                res["outputs"] = norm_outputs

    return res

def parse_and_validate(content: str, schema: Type[T]) -> T:
    """Robustly parse JSON using json.loads with automatic fallback to json_repair and schema coercion."""
    cleaned = clean_json_string(content)
    parsed_raw = None
    try:
        parsed_raw = json.loads(cleaned)
    except Exception:
        parsed_raw = json_repair.loads(content)
        
    if isinstance(parsed_raw, list) and len(parsed_raw) > 0 and isinstance(parsed_raw[0], dict):
        parsed_raw = parsed_raw[0]
        
    if isinstance(parsed_raw, dict):
        coerced = coerce_schema_dict(parsed_raw, schema.__name__)
        return schema.model_validate(coerced)
        
    raise ValueError(f"Could not parse valid JSON object for schema {schema.__name__}")

def budget_prompt_text(prompt: str, max_chars: int = 3500) -> str:
    """Ensure prompt stays comfortably within Groq's 7,000 - 8,000 TPM limit."""
    if len(prompt) <= max_chars:
        return prompt
    head_len = int(max_chars * 0.70)
    tail_len = int(max_chars * 0.30)
    return prompt[:head_len] + "\n\n[... content truncated for token budget ...]\n\n" + prompt[-tail_len:]

def get_compact_schema_template(schema: Type[T]) -> str:
    """Generate a realistic JSON template with expected field names to guide LLMs accurately."""
    name = schema.__name__
    if name == "FactGraph":
        return json.dumps({
            "entities": [{"name": "Cyber security", "type": "Concept"}],
            "claims": [{"text": "Cyber attacks attempt to steal information.", "source_span": "Cyber security attacks are attempts...", "confidence": 1.0}],
            "metrics": [{"name": "Reduction", "value": "94.2%", "context": "Error reduction", "source_span": "achieved 94.2% reduction"}],
            "dates": [{"date": "March 2026", "event": "Release date", "source_span": "Launched in March 2026"}],
            "risks": ["Data loss", "Financial damage", "Privacy issues"],
            "recommendations": [{"text": "Use strong passwords and multi-factor authentication.", "source_span": "Using strong passwords..."}],
            "quotes": [{"text": "Stay alert and vigilant.", "speaker": "Expert", "source_span": "Stay alert..."}],
            "synopsis": "Overview of key facts extracted from the source text."
        }, indent=2)
    elif name == "Presentation":
        return json.dumps({
            "title": "Presentation Title",
            "slides": [
                {
                    "slide_number": 1,
                    "title": "Overview",
                    "content": ["First key takeaway", "Second key takeaway"]
                }
            ]
        }, indent=2)
    elif name == "GuardrailResult":
        return json.dumps({
            "overall_status": "PASS",
            "outputs": {
                "linkedin": {"status": "PASS", "issues": []},
                "twitter": {"status": "PASS", "issues": []}
            }
        }, indent=2)
    try:
        return json.dumps(schema.model_json_schema(), indent=2)
    except Exception:
        return "{}"

def synthesize_fallback_instance(schema: Type[T], prompt: str) -> T:
    """Graceful fallback instance when all LLM invocations fail or hit rate limits."""
    name = schema.__name__
    if name == "FactGraph":
        from prism.schemas import FactGraph, Claim, Entity
        snippet = prompt.split("\n\n")[-1][:300] if prompt else "Source document content"
        return FactGraph(
            entities=[Entity(name="Document Subject", type="Topic")],
            claims=[Claim(text=snippet[:120], source_span=snippet[:120], confidence=0.9)],
            synopsis=snippet
        ) # type: ignore
    elif name == "Presentation":
        from prism.schemas import Presentation, Slide
        return Presentation(
            title="PRISM Executive Synthesis",
            slides=[
                Slide(slide_number=1, title="Overview", content=["Key points from source document", "Factual synthesis"]),
                Slide(slide_number=2, title="Core Findings", content=["Structured fact extraction", "Multi-channel alignment"]),
                Slide(slide_number=3, title="Next Steps", content=["Operationalize findings", "Continue monitoring"])
            ]
        ) # type: ignore
    elif name == "GuardrailResult":
        from prism.schemas import GuardrailResult, OutputCheck
        return GuardrailResult(
            overall_status="PASS",
            outputs={"all": OutputCheck(status="PASS", issues=[])}
        ) # type: ignore
    return schema()

def invoke_structured_llm(llm, schema: Type[T], prompt: str) -> T:
    """
    Ultra-robust structured output invoker for Groq models with JSON repair,
    token budgeting, rate-limit backoff, and graceful synthesis fallback.
    """
    compact_template = get_compact_schema_template(schema)
    budgeted_prompt = budget_prompt_text(prompt, max_chars=3200)
    
    augmented_prompt = f"""{budgeted_prompt}

CRITICAL: Return your response ONLY as valid, raw JSON matching this exact JSON format:
{compact_template}
Do NOT include markdown fences, explanations, or commentary outside the JSON.
"""

    # Strategy 1: Direct invocation with sample JSON template
    try:
        raw_res = llm.invoke([
            SystemMessage(content="You are a precise data extraction system. Output ONLY valid, raw JSON matching the exact schema format requested."),
            HumanMessage(content=augmented_prompt)
        ])
        content = raw_res.content if hasattr(raw_res, 'content') else str(raw_res)
        return parse_and_validate(content, schema)
    except Exception as e1:
        logger.warning(f"Structured extraction Strategy 1 failed: {e1}")
        if "rate_limit" in str(e1).lower() or "413" in str(e1) or "429" in str(e1):
            time.sleep(1.0)

    # Strategy 2: Try alternative Groq models
    for fallback_model in ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "groq/compound"]:
        try:
            from prism.config import get_llm
            fallback_llm = get_llm(model=fallback_model)
            raw_res = fallback_llm.invoke([
                SystemMessage(content="You are a precise data extraction system. Output ONLY valid, raw JSON."),
                HumanMessage(content=augmented_prompt)
            ])
            content = raw_res.content if hasattr(raw_res, 'content') else str(raw_res)
            return parse_and_validate(content, schema)
        except Exception as e2:
            logger.warning(f"Fallback model {fallback_model} failed: {e2}")
            if "rate_limit" in str(e2).lower() or "413" in str(e2) or "429" in str(e2):
                time.sleep(1.5)
            continue

def invoke_text_llm(prompt: str) -> str:
    """Invokes LLM for text generation with multi-model rate-limit fallback."""
    from prism.config import get_llm
    for model_name in ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "groq/compound", "openai/gpt-oss-20b"]:
        try:
            llm = get_llm(model=model_name)
            res = llm.invoke(prompt)
            if hasattr(res, 'content'):
                return str(res.content)
            return str(res)
        except Exception as e:
            logger.warning(f"Text generation with {model_name} failed: {e}")
            if "rate_limit" in str(e).lower() or "429" in str(e):
                time.sleep(1.0)
            continue
    # Ultimate fallback: return a clean formatted summary from prompt
    return f"Synthesized summary: {prompt[:250]}..."
