from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Entity(BaseModel):
    name: str = Field(description="Name of the entity")
    type: str = Field(description="Type or category of the entity")


class Claim(BaseModel):
    text: str = Field(description="A factual claim explicitly supported by the source")
    source_span: str = Field(
        description="The source text or passage that supports this claim"
    )
    confidence: float = Field(
        description="Confidence that the claim is correctly extracted, between 0 and 1"
    )


class Metric(BaseModel):
    name: str = Field(description="Name of the metric or numerical measure")
    value: str = Field(description="Value of the metric")
    context: str = Field(description="What the metric refers to")
    source_span: str = Field(
        description="The source text supporting this metric"
    )


class DateInfo(BaseModel):
    date: str = Field(description="Date or time information")
    event: str = Field(description="Event associated with the date")
    source_span: str = Field(
        description="The source text supporting this date"
    )


class Recommendation(BaseModel):
    text: str = Field(description="Recommendation explicitly stated or supported by the source")
    source_span: str = Field(
        description="The source text supporting this recommendation"
    )


class Quote(BaseModel):
    text: str = Field(description="Important quote from the source")
    speaker: Optional[str] = Field(
        default=None,
        description="Person or entity associated with the quote"
    )
    source_span: str = Field(
        description="The source text containing the quote"
    )


class FactGraph(BaseModel):
    entities: List[Entity] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    metrics: List[Metric] = Field(default_factory=list)
    dates: List[DateInfo] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    quotes: List[Quote] = Field(default_factory=list)
    synopsis: str = Field(
        description="A neutral synopsis of the source based only on extracted facts"
    )


class Slide(BaseModel):
    slide_number: int = Field(description="The slide number")
    title: str = Field(description="The title of the slide")
    content: List[str] = Field(description="Bullet points or key content for the slide")


class Presentation(BaseModel):
    title: str = Field(description="The overall presentation title")
    slides: List[Slide] = Field(description="List of presentation slides")


class OutputCheck(BaseModel):
    status: str = Field(
        description="PASS if the output is fully supported by the Fact Graph, otherwise FAIL"
    )
    issues: List[str] = Field(
        description="List of factual consistency issues found in the output"
    )


class GuardrailResult(BaseModel):
    overall_status: str = Field(
        description="PASS if all checked outputs are consistent, otherwise FAIL"
    )
    outputs: Dict[str, OutputCheck] = Field(
        description="Consistency check result for each generated output"
    )


class ProvenanceItem(BaseModel):
    output_channel: str = Field(description="Channel name, e.g. linkedin, twitter, summary, advisory, presentation")
    output_statement: str = Field(description="Specific sentence or statement in generated output")
    claim_text: str = Field(description="Matched supporting claim from Fact Graph")
    source_span: str = Field(description="Original source text snippet proving the claim")
    confidence: float = Field(default=0.95, description="Confidence score")
