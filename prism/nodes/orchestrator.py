from typing import List
from prism.state import PRISMState

VALID_OUTPUTS = {
    "linkedin",
    "twitter",
    "summary",
    "advisory",
    "presentation"
}

def orchestrator_node(state: PRISMState) -> dict:
    selected_outputs = state.get("selected_outputs", [])

    if not selected_outputs:
        raise ValueError("No outputs selected.")

    invalid_outputs = [
        output
        for output in selected_outputs
        if output not in VALID_OUTPUTS
    ]

    if invalid_outputs:
        raise ValueError(
            f"Invalid output(s) selected: {invalid_outputs}"
        )

    return {}

def orchestrator_router(state: PRISMState) -> List[str]:
    """
    LangGraph conditional fan-out router: returns the list of specialist agent
    node names to execute concurrently based on state["selected_outputs"].
    """
    selected = state.get("selected_outputs", [])
    nodes = []
    for out in selected:
        if out in VALID_OUTPUTS:
            nodes.append(f"{out}_node")
    return nodes
