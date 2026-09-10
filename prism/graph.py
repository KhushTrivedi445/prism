from langgraph.graph import StateGraph, START, END
from prism.state import PRISMState

# Import all pipeline nodes
from prism.nodes.ingestion import ingestion_node
from prism.nodes.normalization import normalization_node
from prism.nodes.fact_graph import fact_graph_node
from prism.nodes.rag_nodes import rag_chunking_node, rag_vector_store_node, rag_retriever_node
from prism.nodes.orchestrator import orchestrator_node, orchestrator_router
from prism.nodes.specialists import (
    linkedin_node,
    twitter_node,
    summary_node,
    advisory_node,
    presentation_node
)
from prism.nodes.guardrail import (
    guardrail_node,
    failed_output_detection_node,
    guardrail_router
)
from prism.nodes.revision import revision_node
from prism.nodes.provenance import provenance_node
from prism.nodes.rendering import render_node
from prism.nodes.persistence import persistence_node

def build_prism_graph():
    workflow = StateGraph(PRISMState)

    # 1. Ingestion & Preprocessing
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("normalization", normalization_node)
    workflow.add_node("fact_graph", fact_graph_node)

    # 2. RAG Infrastructure
    workflow.add_node("rag_chunking", rag_chunking_node)
    workflow.add_node("rag_vector_store", rag_vector_store_node)
    workflow.add_node("rag_retriever", rag_retriever_node)

    # 3. Orchestration
    workflow.add_node("orchestrator", orchestrator_node)

    # 4. Specialist Agents
    workflow.add_node("linkedin_node", linkedin_node)
    workflow.add_node("twitter_node", twitter_node)
    workflow.add_node("summary_node", summary_node)
    workflow.add_node("advisory_node", advisory_node)
    workflow.add_node("presentation_node", presentation_node)

    # 5. Guardrail Critic & Revision
    workflow.add_node("guardrail", guardrail_node)
    workflow.add_node("failed_output_detection", failed_output_detection_node)
    workflow.add_node("revision", revision_node)

    # 6. Provenance, Rendering & Persistence
    workflow.add_node("provenance", provenance_node)
    workflow.add_node("render", render_node)
    workflow.add_node("persist", persistence_node)

    # --- Edge Connections ---
    # Sequential ingestion & preparation
    workflow.add_edge(START, "ingestion")
    workflow.add_edge("ingestion", "normalization")
    workflow.add_edge("normalization", "fact_graph")
    workflow.add_edge("fact_graph", "rag_chunking")
    workflow.add_edge("rag_chunking", "rag_vector_store")
    workflow.add_edge("rag_vector_store", "rag_retriever")
    workflow.add_edge("rag_retriever", "orchestrator")

    # Dynamic Fan-Out from Orchestrator based on selected_outputs
    workflow.add_conditional_edges(
        "orchestrator",
        orchestrator_router,
        {
            "linkedin_node": "linkedin_node",
            "twitter_node": "twitter_node",
            "summary_node": "summary_node",
            "advisory_node": "advisory_node",
            "presentation_node": "presentation_node"
        }
    )

    # Fan-In: All specialist nodes converge to the Guardrail
    workflow.add_edge("linkedin_node", "guardrail")
    workflow.add_edge("twitter_node", "guardrail")
    workflow.add_edge("summary_node", "guardrail")
    workflow.add_edge("advisory_node", "guardrail")
    workflow.add_edge("presentation_node", "guardrail")

    # Guardrail Router: Pass -> Provenance, Fail -> Failed Output Detection
    workflow.add_conditional_edges(
        "guardrail",
        guardrail_router,
        {
            "pass": "provenance",
            "fail": "failed_output_detection"
        }
    )

    # Revision Loop
    workflow.add_edge("failed_output_detection", "revision")
    workflow.add_edge("revision", "guardrail")

    # Terminal rendering & persistence pipeline
    workflow.add_edge("provenance", "render")
    workflow.add_edge("render", "persist")
    workflow.add_edge("persist", END)

    return workflow.compile()

# Global compiled graph
prism_app = build_prism_graph()
