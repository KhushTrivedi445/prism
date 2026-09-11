import os
import time
from dotenv import load_dotenv

load_dotenv()

# Default API Keys from original notebook environment
DEFAULT_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
DEFAULT_HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "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")

os.environ["GROQ_API_KEY"] = DEFAULT_GROQ_API_KEY
os.environ["HUGGINGFACEHUB_API_TOKEN"] = DEFAULT_HF_TOKEN

DEFAULT_MODEL = os.getenv("PRISM_GROQ_MODEL", "openai/gpt-oss-120b")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MAX_REVISIONS = int(os.getenv("PRISM_MAX_REVISIONS", "2"))

OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "prism.db")

os.makedirs(OUTPUTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def get_llm(model: str = None, api_key: str = None, temperature: float = 0.0):
    from langchain_groq import ChatGroq
    chosen_model = model or os.getenv("PRISM_GROQ_MODEL", DEFAULT_MODEL)
    key = api_key or os.getenv("GROQ_API_KEY", DEFAULT_GROQ_API_KEY)
    # Configure with automatic retries and backoff for rate limits
    return ChatGroq(
        model=chosen_model,
        groq_api_key=key,
        temperature=temperature,
        max_retries=6,
        timeout=60.0
    )
