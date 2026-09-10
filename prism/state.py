from typing import TypedDict, List, Dict, Any, Optional

class PRISMState(TypedDict):
    input_type: str              # "file" or "text"
    file_path: Optional[str]
    input_text: Optional[str]

    source_text: str
    normalized_text: str
    fact_graph: Dict[str, Any]

    tone: str
    selected_outputs: List[str]

    linkedin_output: Optional[str]
    twitter_output: Optional[str]
    summary_output: Optional[str]
    advisory_output: Optional[str]
    presentation_output: Optional[Dict[str, Any]]
    pptx_path: Optional[str]

    guardrail_result: Optional[Dict[str, Any]]
    failed_output: Optional[str]
    revision_count: int
    provenance: List[Dict[str, Any]]

    rag_chunks: List[str]
    rag_vector_store: Any
    rag_retriever: Any

    # Additional execution & persistence metadata
    run_id: Optional[str]
    audience: Optional[str]
    objective: Optional[str]
    rendered_assets: Optional[Dict[str, str]]
