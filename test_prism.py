import os
import sys
import unittest
from prism.state import PRISMState
from prism.persistence.db import save_run, get_run, list_runs, init_db
from prism.nodes.ingestion import ingestion_node
from prism.nodes.normalization import normalization_node
from prism.nodes.provenance import provenance_node
from prism.nodes.rendering import render_node
from prism.graph import prism_app

SAMPLE_TEXT = """
PRISM is an AI-powered content generation system.
It takes a source document and creates multiple content formats.
PRISM uses a centralized Fact Graph to maintain consistency across generated outputs.
The system reduces multi-channel authoring time by 75% and guarantees 100% provenance verification.
"""

def create_base_state(selected_outputs=None, input_text=SAMPLE_TEXT) -> PRISMState:
    if selected_outputs is None:
        selected_outputs = ["linkedin", "summary"]
    return {
        "input_type": "text",
        "file_path": None,
        "input_text": input_text,
        "source_text": "",
        "normalized_text": "",
        "fact_graph": {},
        "tone": "professional",
        "audience": "Enterprise Executives",
        "objective": "Multi-channel synthesis",
        "selected_outputs": selected_outputs,
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
        "run_id": "test_run_01",
        "rendered_assets": {}
    }

def run_e2e_tests():
    print("\n=======================================================")
    print("       STARTING PRISM COMPREHENSIVE TEST SUITE        ")
    print("=======================================================\n")

    # 1. Ingestion & Normalization Unit Test
    print("[TEST 1/6] Ingestion & Normalization Node...")
    state = create_base_state()
    state.update(ingestion_node(state))
    state.update(normalization_node(state))
    assert len(state["normalized_text"]) > 0, "Normalized text should not be empty"
    print("  -> Ingestion & Normalization passed!")

    # 2. Database Persistence Unit Test
    print("\n[TEST 2/6] SQLite Persistence Layer...")
    init_db()
    test_save_state = create_base_state(selected_outputs=["linkedin"])
    test_save_state["linkedin_output"] = "PRISM provides grounded content."
    test_save_state["fact_graph"] = {"synopsis": "AI synthesis system"}
    run_id = save_run(test_save_state)
    retrieved = get_run(run_id)
    assert retrieved is not None, "Failed to retrieve saved run"
    assert retrieved["run_id"] == run_id
    assert "linkedin" in retrieved["selected_outputs"]
    runs = list_runs()
    assert len(runs) > 0
    print(f"  -> SQLite persistence passed! Saved & retrieved run: {run_id}")

    # 3. Provenance Engine Test
    print("\n[TEST 3/6] Provenance Mapping Engine...")
    prov_state = create_base_state(selected_outputs=["linkedin", "summary"])
    prov_state["fact_graph"] = {
        "claims": [
            {
                "text": "PRISM uses a centralized Fact Graph.",
                "source_span": "PRISM uses a centralized Fact Graph to maintain consistency across generated outputs.",
                "confidence": 0.98
            },
            {
                "text": "The system reduces authoring time by 75%.",
                "source_span": "The system reduces multi-channel authoring time by 75%.",
                "confidence": 0.95
            }
        ],
        "metrics": [],
        "dates": [],
        "risks": [],
        "recommendations": [],
        "quotes": [],
        "synopsis": "PRISM content generation engine."
    }
    prov_state["linkedin_output"] = "PRISM uses a centralized Fact Graph to keep content aligned.\nIt reduces authoring time by 75%."
    prov_state["summary_output"] = "The system is powered by a centralized Fact Graph."
    prov_state.update(provenance_node(prov_state))
    assert len(prov_state["provenance"]) > 0, "Provenance records should be generated"
    first_prov = prov_state["provenance"][0]
    print(f"  -> Generated {len(prov_state['provenance'])} provenance links.")
    print(f"     Example link: '{first_prov['output_statement']}' -> '{first_prov['claim_text']}'")
    print(f"     Source span: '{first_prov['source_span']}' (Conf: {first_prov['confidence']})")
    print("  -> Provenance engine passed!")

    # 4. Rendering Engine Test
    print("\n[TEST 4/6] Multi-Format Rendering Engine (PPTX, DOCX, Markdown, Text)...")
    render_state = create_base_state(selected_outputs=["linkedin", "summary", "presentation"])
    render_state["run_id"] = "test_render_01"
    render_state["linkedin_output"] = "PRISM test LinkedIn post."
    render_state["summary_output"] = "PRISM test Executive Summary."
    render_state["presentation_output"] = {
        "title": "PRISM System Architecture",
        "slides": [
            {"slide_number": 1, "title": "Introduction", "content": ["AI Synthesis", "Single Source of Truth"]},
            {"slide_number": 2, "title": "Architecture", "content": ["Fact Graph", "Guardrail Critic"]}
        ]
    }
    render_state.update(render_node(render_state))
    assets = render_state.get("rendered_assets", {})
    assert "linkedin_md" in assets and os.path.exists(assets["linkedin_md"])
    assert "summary_docx" in assets and os.path.exists(assets["summary_docx"])
    assert "presentation" in assets and os.path.exists(assets["presentation"])
    print(f"  -> Rendered assets successfully: {list(assets.keys())}")
    print("  -> Rendering engine passed!")

    # 5. Full LangGraph End-to-End Pipeline Execution
    print("\n[TEST 5/6] Full LangGraph End-to-End Execution (LinkedIn + Summary + Presentation)...")
    e2e_state = create_base_state(selected_outputs=["linkedin", "summary", "presentation"])
    print("  -> Invoking prism_app.invoke()... (Extracting Fact Graph, generating specialist outputs, checking Guardrail, rendering, persisting)")
    
    final_state = prism_app.invoke(e2e_state)

    print("\n  [PIPELINE EXECUTION COMPLETE]")
    print(f"  -> Generated Fact Graph synopsis: {final_state['fact_graph'].get('synopsis', 'N/A')}")
    print(f"  -> Fact Graph Claims extracted: {len(final_state['fact_graph'].get('claims', []))}")
    print(f"  -> LinkedIn Output length: {len(final_state.get('linkedin_output') or '')} chars")
    print(f"  -> Summary Output length: {len(final_state.get('summary_output') or '')} chars")
    print(f"  -> Presentation Slide Count: {len(final_state.get('presentation_output', {}).get('slides', []))}")
    print(f"  -> Guardrail Status: {final_state.get('guardrail_result', {}).get('overall_status', 'N/A')}")
    print(f"  -> Total Revisions: {final_state.get('revision_count', 0)}")
    print(f"  -> Provenance Links: {len(final_state.get('provenance', []))}")
    print(f"  -> Persisted Run ID: {final_state.get('run_id')}")

    assert final_state.get("linkedin_output") is not None
    assert final_state.get("summary_output") is not None
    assert final_state.get("presentation_output") is not None
    assert final_state.get("guardrail_result") is not None
    assert len(final_state.get("provenance", [])) > 0
    print("  -> Full LangGraph pipeline execution passed!")

    # 6. Verify Persisted Run in SQLite
    print("\n[TEST 6/6] Verifying Persisted Run in Database...")
    db_record = get_run(final_state["run_id"])
    assert db_record is not None
    assert db_record["guardrail_result"]["overall_status"] in ["PASS", "FAIL"]
    print(f"  -> Successfully verified database record for run: {final_state['run_id']}")

    print("\n=======================================================")
    print("         ALL PRISM TESTS PASSED SUCCESSFULLY!         ")
    print("=======================================================\n")

if __name__ == "__main__":
    run_e2e_tests()
