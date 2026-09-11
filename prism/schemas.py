from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, model_validator

class Entity(BaseModel):
    name: str = Field(default="Entity", description="Name of the entity")
    type: str = Field(default="General", description="Type or category of the entity")

    @model_validator(mode='before')
    @classmethod
    def normalize_entity(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data, "type": "Concept"}
        if isinstance(data, dict):
            name = data.get("name") or data.get("entity") or data.get("item") or data.get("title") or data.get("term") or "Entity"
            ent_type = data.get("type") or data.get("category") or data.get("kind") or "Concept"
            return {"name": str(name), "type": str(ent_type)}
        return data


class Claim(BaseModel):
    text: str = Field(default="", description="A factual claim explicitly supported by the source")
    source_span: str = Field(
        default="",
        description="The source text or passage that supports this claim"
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence that the claim is correctly extracted, between 0 and 1"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_claim(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"text": data, "source_span": data, "confidence": 1.0}
        if isinstance(data, dict):
            text = data.get("text") or data.get("claim") or data.get("statement") or data.get("fact") or data.get("point") or ""
            source = data.get("source_span") or data.get("source") or data.get("span") or data.get("context") or text
            conf = data.get("confidence", 1.0)
            try:
                conf = float(conf)
            except Exception:
                conf = 1.0
            return {"text": str(text), "source_span": str(source), "confidence": conf}
        return data


class Metric(BaseModel):
    name: str = Field(default="Metric", description="Name of the metric or numerical measure")
    value: str = Field(default="", description="Value of the metric")
    context: str = Field(default="", description="What the metric refers to")
    source_span: str = Field(
        default="",
        description="The source text supporting this metric"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_metric(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": "Metric", "value": data, "context": data, "source_span": data}
        if isinstance(data, dict):
            name = data.get("name") or data.get("metric") or data.get("title") or data.get("measure") or "Metric"
            value = data.get("value") or data.get("amount") or data.get("number") or data.get("stat") or ""
            context = data.get("context") or data.get("description") or str(value)
            source = data.get("source_span") or data.get("source") or data.get("span") or str(context)
            return {"name": str(name), "value": str(value), "context": str(context), "source_span": str(source)}
        return data


class DateInfo(BaseModel):
    date: str = Field(default="", description="Date or time information")
    event: str = Field(default="", description="Event associated with the date")
    source_span: str = Field(
        default="",
        description="The source text supporting this date"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_date(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"date": data, "event": data, "source_span": data}
        if isinstance(data, dict):
            date = data.get("date") or data.get("time") or data.get("year") or data.get("period") or ""
            event = data.get("event") or data.get("description") or str(date)
            source = data.get("source_span") or data.get("source") or data.get("span") or str(event)
            return {"date": str(date), "event": str(event), "source_span": str(source)}
        return data


class Recommendation(BaseModel):
    text: str = Field(default="", description="Recommendation explicitly stated or supported by the source")
    source_span: str = Field(
        default="",
        description="The source text supporting this recommendation"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_recommendation(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"text": data, "source_span": data}
        if isinstance(data, dict):
            text = data.get("text") or data.get("recommendation") or data.get("advice") or data.get("action") or data.get("tip") or data.get("type") or ""
            source = data.get("source_span") or data.get("source") or data.get("span") or text
            return {"text": str(text), "source_span": str(source)}
        return data


class Quote(BaseModel):
    text: str = Field(default="", description="Important quote from the source")
    speaker: Optional[str] = Field(
        default=None,
        description="Person or entity associated with the quote"
    )
    source_span: str = Field(
        default="",
        description="The source text containing the quote"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_quote(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"text": data, "source_span": data, "speaker": None}
        if isinstance(data, dict):
            text = data.get("text") or data.get("quote") or data.get("statement") or ""
            source = data.get("source_span") or data.get("source") or text
            speaker = data.get("speaker") or data.get("author") or data.get("person")
            return {"text": str(text), "source_span": str(source), "speaker": speaker}
        return data


class FactGraph(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    metrics: List[Metric] = Field(default_factory=list)
    dates: List[DateInfo] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    quotes: List[Quote] = Field(default_factory=list)
    synopsis: str = Field(
        default="",
        description="A neutral synopsis of the source based only on extracted facts"
    )

    @model_validator(mode='before')
    @classmethod
    def normalize_fact_graph(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        res = dict(data)
        # Normalize risks if list of dicts
        if "risks" in res and isinstance(res["risks"], list):
            norm_risks = []
            for r in res["risks"]:
                if isinstance(r, str):
                    norm_risks.append(r)
                elif isinstance(r, dict):
                    val = r.get("risk") or r.get("type") or r.get("text") or r.get("description") or str(r)
                    norm_risks.append(str(val))
            res["risks"] = norm_risks
        # Normalize synopsis if list
        if "synopsis" in res and isinstance(res["synopsis"], list):
            res["synopsis"] = " ".join(str(s) for s in res["synopsis"])
        return res


class Slide(BaseModel):
    slide_number: int = Field(default=1, description="The slide number")
    title: str = Field(default="Key Takeaways", description="The title of the slide")
    content: List[str] = Field(default_factory=list, description="Bullet points or key content for the slide")


class Presentation(BaseModel):
    title: str = Field(default="Executive Overview", description="The overall presentation title")
    slides: List[Slide] = Field(default_factory=list, description="List of presentation slides")


class OutputCheck(BaseModel):
    status: str = Field(
        default="PASS",
        description="PASS if the output is fully supported by the Fact Graph, otherwise FAIL"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of factual consistency issues found in the output"
    )


class GuardrailResult(BaseModel):
    overall_status: str = Field(
        default="PASS",
        description="PASS if all checked outputs are consistent, otherwise FAIL"
    )
    outputs: Dict[str, OutputCheck] = Field(
        default_factory=dict,
        description="Consistency check result for each generated output"
    )


class ProvenanceItem(BaseModel):
    output_channel: str = Field(description="Channel name, e.g. linkedin, twitter, summary, advisory, presentation")
    output_statement: str = Field(description="Specific sentence or statement in generated output")
    claim_text: str = Field(description="Matched supporting claim from Fact Graph")
    source_span: str = Field(description="Original source text snippet proving the claim")
    confidence: float = Field(default=0.95, description="Confidence score")
