import re
from prism.state import PRISMState

def normalization_node(state: PRISMState) -> dict:
    text = state.get("source_text", "")
    if not text:
        raise ValueError("Source text is empty.")

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces/tabs with a single space
    text = re.sub(r"[ \t]+", " ", text)

    # Replace 3 or more consecutive newlines with 2 newlines
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    # Remove unnecessary spaces around newlines
    text = re.sub(r" *\n *", "\n", text)

    return {"normalized_text": text}
