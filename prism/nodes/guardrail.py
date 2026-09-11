from prism.state import PRISMState
from prism.schemas import GuardrailResult
from prism.config import get_llm, MAX_REVISIONS
from prism.utils import invoke_structured_llm

def guardrail_node(state: PRISMState) -> dict:
    fact_graph = state.get("fact_graph")
    selected_outputs = state.get("selected_outputs", [])

    generated_outputs = {}
    if "linkedin" in selected_outputs and state.get("linkedin_output"):
        generated_outputs["linkedin"] = state["linkedin_output"]
    if "twitter" in selected_outputs and state.get("twitter_output"):
        generated_outputs["twitter"] = state["twitter_output"]
    if "summary" in selected_outputs and state.get("summary_output"):
        generated_outputs["summary"] = state["summary_output"]
    if "advisory" in selected_outputs and state.get("advisory_output"):
        generated_outputs["advisory"] = state["advisory_output"]
    if "presentation" in selected_outputs and state.get("presentation_output"):
        generated_outputs["presentation"] = state["presentation_output"]

    llm = get_llm()

    prompt = f"""
You are the Guardrail / Consistency Critic Agent for PRISM.

Your ONLY job is to determine whether each generated output
contains factual claims that are unsupported by the Fact Graph.

The Fact Graph is the SINGLE SOURCE OF TRUTH.

====================
FACT GRAPH
====================
{fact_graph}

====================
GENERATED OUTPUTS
====================
{generated_outputs}

====================
STRICT VALIDATION RULES
====================

1. Check every generated output independently.

2. A factual statement is VALID only if its meaning is directly
   supported by one or more facts in the Fact Graph.

3. Do NOT require exact wording.
   Legitimate paraphrasing is allowed.

4. Do NOT infer additional capabilities, benefits, statistics,
   performance improvements, or guarantees.

5. If the Fact Graph says:
   "X maintains consistency across generated outputs"

   then the output may say:
   "X maintains consistency across generated outputs."

   It may also use a reasonable paraphrase with the SAME meaning.

6. However, do NOT automatically infer:
   "X produces reliable content"
   "X improves productivity"
   "X saves time"
   "X guarantees accuracy"

   unless those claims are explicitly supported.

7. Numbers, percentages, measurements, performance claims,
   guarantees, and specific benefits require explicit support.

8. If a statement is merely descriptive wording that does not
   introduce a new factual claim, do not mark it as an error.

9. Recommendations in advisory content should not be treated
   as factual claims unless they are presented as established facts.

10. If an output contains even ONE unsupported factual claim,
    mark that output as FAIL.

11. If an output contains no unsupported factual claims,
    mark it as PASS.

12. overall_status must be:
       PASS -> only when ALL selected outputs are PASS
       FAIL -> when ANY selected output is FAIL

13. For every FAIL, explain the exact unsupported claim in the issues list.

14. Do not invent issues.

15. Be conservative:
    Only mark FAIL when you can identify a specific unsupported
    factual claim.

Return ONLY the structured GuardrailResult as valid JSON.
"""

    result = invoke_structured_llm(llm, GuardrailResult, prompt)

    if isinstance(result, dict):
        res_dict = result
    else:
        res_dict = result.model_dump()

    return {"guardrail_result": res_dict}


def failed_output_detection_node(state: PRISMState) -> dict:
    guardrail_result = state.get("guardrail_result")
    if not guardrail_result:
        raise ValueError("Guardrail result is missing.")

    failed_outputs = []
    for output_name, result in guardrail_result.get("outputs", {}).items():
        if result.get("status") == "FAIL":
            failed_outputs.append(output_name)

    if not failed_outputs:
        return {"failed_output": None}

    # Handle one failed output at a time for revision
    return {"failed_output": failed_outputs[0]}


def guardrail_router(state: PRISMState) -> str:
    guardrail_result = state.get("guardrail_result")
    if not guardrail_result:
        raise ValueError("Guardrail result is missing.")

    overall_status = guardrail_result.get("overall_status", "PASS")
    revision_count = state.get("revision_count", 0)

    if overall_status == "FAIL" and revision_count < MAX_REVISIONS:
        return "fail"
    else:
        return "pass"
