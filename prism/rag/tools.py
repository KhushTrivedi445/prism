from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.tools import tool
from prism.config import EMBEDDING_MODEL_NAME

_embeddings_cache = None

def get_embeddings():
    global _embeddings_cache
    if _embeddings_cache is None:
        _embeddings_cache = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME
        )
    return _embeddings_cache

def get_text_splitter(chunk_size: int = 1000, chunk_overlap: int = 150):
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

_active_retriever = None

def set_active_retriever(retriever):
    global _active_retriever
    _active_retriever = retriever

@tool
def search_source(query: str) -> str:
    """
    Search the original source document for information relevant
    to the given query and return the most relevant passages.
    """
    if not query.strip():
        raise ValueError("Search query cannot be empty.")

    if _active_retriever is None:
        return "No active retriever available to search source passages."

    docs = _active_retriever.invoke(query)
    if not docs:
        return "No relevant information was found in the source."

    results = []
    for i, doc in enumerate(docs, 1):
        results.append(f"Source Passage {i}:\n{doc.page_content}")

    return "\n\n".join(results)
