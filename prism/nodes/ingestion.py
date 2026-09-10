import os
from langchain_community.document_loaders import PyPDFLoader
from prism.state import PRISMState

def ingestion_node(state: PRISMState) -> dict:
    if state.get("input_type") == "text":
        if not state.get("input_text"):
            raise ValueError("Input text is empty.")
        source_text = state["input_text"]

    elif state.get("input_type") == "file":
        file_path = state.get("file_path")
        if not file_path:
            raise ValueError("File path is missing.")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            pages = loader.load()
            source_text = "\n\n".join(page.page_content for page in pages)
        elif ext in [".docx", ".doc"]:
            import docx
            doc = docx.Document(file_path)
            source_text = "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        else:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                source_text = f.read()

    else:
        raise ValueError("input_type must be either 'text' or 'file'.")

    return {"source_text": source_text}
