from prism.state import PRISMState
from prism.schemas import Presentation
from prism.config import get_llm
from prism.nodes.specialists import pptx_renderer_node

def revision_node(state: PRISMState) -> dict:
    failed_output = state.get("failed_output")
    fact_graph = state.get("fact_graph")
    guardrail_result = state.get("guardrail_result")
    tone = state.get("tone", "professional")

    if not failed_output or not guardrail_result:
        return {}

    failed_check = guardrail_result.get("outputs", {}).get(failed_output)
    if not failed_check:
        return {}

    issues = failed_check.get("issues", [])
    if not issues:
        return {}

    # Get the original generated content
    if failed_output == "linkedin":
        original_output = state.get("linkedin_output", "")
    elif failed_output == "twitter":
        original_output = state.get("twitter_output", "")
    elif failed_output == "summary":
        original_output = state.get("summary_output", "")
    elif failed_output == "advisory":
        original_output = state.get("advisory_output", "")
    elif failed_output == "presentation":
        original_output = state.get("presentation_output", {})
    else:
        return {}

    prompt = f"""
You are the Revision Agent for PRISM.

Your task is to revise ONLY the failed output.

Do NOT regenerate other outputs.

The Fact Graph is the single source of truth.

====================
FAILED OUTPUT TYPE
====================
{failed_output}

====================
FACT GRAPH
====================
{fact_graph}

====================
ORIGINAL OUTPUT
====================
{original_output}

====================
GUARDRAIL ISSUES
====================
{issues}

====================
REVISION RULES
====================

1. Fix every issue identified by the Guardrail.

2. Use ONLY information supported by the Fact Graph.

3. Do not introduce new factual claims.

4. Do not invent statistics, features, capabilities,
   benefits, or guarantees.

5. Preserve valid information from the original output.

6. Only change what is necessary to resolve the
   Guardrail issues.

7. Maintain the original purpose and format of the output.

8. Follow the requested tone:
{tone}

9. The revised output must remain suitable for its
   specific format.

10. Return ONLY the revised output.

Do not explain what you changed.
"""

    llm = get_llm()
    new_revision_count = state.get("revision_count", 0) + 1
    updates = {"revision_count": new_revision_count}

    if failed_output == "presentation":
        try:
            presentation_llm = llm.with_structured_output(
                Presentation,
                method="json_schema"
            )
        except Exception:
            presentation_llm = llm.with_structured_output(Presentation)

        revised_presentation = presentation_llm.invoke(prompt)
        if isinstance(revised_presentation, dict):
            pres_dict = revised_presentation
        else:
            pres_dict = revised_presentation.model_dump()

        updates["presentation_output"] = pres_dict
        # Update PPTX rendering
        temp_state = dict(state)
        temp_state["presentation_output"] = pres_dict
        ppt_updates = pptx_renderer_node(temp_state)
        updates.update(ppt_updates)

    else:
        revised_output = llm.invoke(prompt)
        content = revised_output.content

        if failed_output == "linkedin":
            updates["linkedin_output"] = content
        elif failed_output == "twitter":
            updates["twitter_output"] = content
        elif failed_output == "summary":
            updates["summary_output"] = content
        elif failed_output == "advisory":
            updates["advisory_output"] = content

    return updates
