from langchain_community.vectorstores import FAISS
from prism.state import PRISMState
from prism.rag.tools import get_text_splitter, get_embeddings, set_active_retriever

def rag_chunking_node(state: PRISMState) -> dict:
    normalized_text = state.get("normalized_text", "")
    if not normalized_text:
        raise ValueError("Normalized text is empty.")

    text_splitter = get_text_splitter()
    chunks = text_splitter.split_text(normalized_text)

    if not chunks:
        chunks = [normalized_text]

    return {"rag_chunks": chunks}

def rag_vector_store_node(state: PRISMState) -> dict:
    chunks = state.get("rag_chunks", [])
    if not chunks:
        raise ValueError("RAG chunks are empty.")

    embeddings = get_embeddings()
    vector_store = FAISS.from_texts(
        texts=chunks,
        embedding=embeddings
    )

    return {"rag_vector_store": vector_store}

def rag_retriever_node(state: PRISMState) -> dict:
    vector_store = state.get("rag_vector_store")
    if not vector_store:
        raise ValueError("RAG vector store is missing.")

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    set_active_retriever(retriever)
    return {"rag_retriever": retriever}
