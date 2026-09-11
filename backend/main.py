import os
import sys

# Ensure both backend/ and project root are in sys.path
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))

for path in [CURRENT_DIR, ROOT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(os.path.join(CURRENT_DIR, ".env"))

try:
    from backend.api.routes.health import router as health_router
    from backend.api.routes.models import router as models_router
    from backend.api.routes.generation import router as generation_router
    from backend.api.routes.runs import router as runs_router
    from backend.api.routes.outputs import router as outputs_router
except ImportError:
    from api.routes.health import router as health_router
    from api.routes.models import router as models_router
    from api.routes.generation import router as generation_router
    from api.routes.runs import router as runs_router
    from api.routes.outputs import router as outputs_router

from prism.persistence.db import init_db

init_db()

app = FastAPI(
    title="PRISM API",
    description="Provenance-Reasoned Intelligent Synthesis for Multi-channel Content — REST API",
    version="1.0.0"
)

# Configure CORS for React frontend (Vite default is 3000 or 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(models_router, prefix="/api", tags=["Models"])
app.include_router(generation_router, prefix="/api", tags=["Generation"])
app.include_router(runs_router, prefix="/api", tags=["Runs"])
app.include_router(outputs_router, prefix="/api", tags=["Outputs"])

@app.get("/")
def root():
    return {
        "system": "PRISM Multi-Channel Synthesis Platform",
        "docs": "/docs",
        "api": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
