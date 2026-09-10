from prism.state import PRISMState
from prism.persistence.db import save_run

def persistence_node(state: PRISMState) -> dict:
    run_id = save_run(state)
    return {"run_id": run_id}
