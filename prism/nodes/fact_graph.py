from prism.state import PRISMState
from prism.schemas import FactGraph
from prism.config import get_llm
from prism.utils import invoke_structured_llm

def fact_graph_node(state: PRISMState) -> dict:
    text = state.get("normalized_text")
    if not text:
        raise ValueError("Normalized text is empty.")

    llm = get_llm()

    prompt = f"""
You are the Fact Graph Extraction Agent for PRISM.

Your job is to extract structured factual information from the
source document.

The extracted Fact Graph will become the SINGLE SOURCE OF TRUTH
for all downstream content generation.

====================
EXTRACTION RULES
====================

1. Extract ONLY information explicitly supported by the source.

2. Do NOT invent, assume, infer, or add information that is not
   present in the source.

3. Identify important entities and their types.

4. Extract important factual claims.

5. For EVERY claim, include the source text that supports it
   in the source_span field.

6. Assign a confidence score between 0 and 1 for every claim.

7. Extract important numerical information such as:
   - percentages
   - counts
   - measurements
   - financial values
   - performance metrics
   - statistics

8. For EVERY metric, include the source text that supports it.

9. Extract important dates and the events associated with them.

10. Extract explicitly mentioned risks.

11. Extract explicitly mentioned recommendations.

12. Extract important direct quotes when present.
    Do not invent quotes.

13. Create a neutral synopsis of the source.
    The synopsis must contain only information supported by
    the extracted facts.

14. If a category is not present in the source, return an empty
    list for that category.

15. Do NOT write marketing content.

16. Do NOT rewrite facts to make them sound better.

17. Preserve numerical values exactly as they appear in the source.

18. The source_span fields must contain enough source text to
    clearly justify the corresponding claim, metric, date,
    recommendation, or quote.

====================
SOURCE DOCUMENT
====================

{text}

Return ONLY the structured FactGraph as valid JSON.
"""

    fact_graph = invoke_structured_llm(llm, FactGraph, prompt)

    if isinstance(fact_graph, dict):
        fg_dict = fact_graph
    else:
        fg_dict = fact_graph.model_dump()

    return {"fact_graph": fg_dict}
