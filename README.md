# PRISM — Provenance-Reasoned Intelligent Synthesis for Multi-Channel Content

**PRISM** is an enterprise-grade multi-channel content synthesis platform. It takes a single raw source document (PDF, DOCX, or text), extracts a structured **Fact Graph** as the single source of truth, fans out to specialist agents (LinkedIn, Twitter/X, Executive Summary, Strategic Advisory, Slide Deck Presentation), validates all outputs via a **Guardrail Consistency Critic**, performs targeted **Bounded Revisions**, and stores verifiable **Claim-to-Source Provenance** links in a local **SQLite** database.

---

## 🏗️ Architecture

```
React + Vite + Tailwind CSS (Port 3000)
              │
              │ REST API (JSON & Multipart Form-Data)
              ▼
    FastAPI Backend (Port 8000)
              │
              ▼
   LangGraph PRISM Pipeline
              │
    ┌─────────┼─────────────────────────┐
    │         │          │       │      │
    ▼         ▼          ▼       ▼      ▼
 LinkedIn  Twitter/X  Summary Advisory Slides (PPTX)
    │         │          │       │      │
    └─────────┴──────────┴───────┴──────┘
                         │
                         ▼
           Guardrail Consistency Critic
                         │
                  PASS / FAIL
                 /            \
                ▼              ▼
          Render Stage    Revision Loop (Max 1–2 cycles)
                │              │
                │              └──→ Back to Guardrail
                ▼
          Persist Stage
                │
                ▼
        SQLite Database (data/prism.db)
```

---

## 🔒 Security: Backend-Only API Secrets

All provider API credentials (`GROQ_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`) are isolated strictly on the **FastAPI backend** in `backend/.env`.
- **Zero client leakage**: Frontend receives only safe public model metadata (`GET /api/models`).
- No API keys are stored in React code, Vite envs, localStorage, HTML, or browser responses.

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+ / npm**

### 2. Backend Setup & Launch

```powershell
# Install backend Python dependencies
py -3.11 -m pip install -r backend/requirements.txt

# Start the FastAPI backend (Port 8000)
py -3.11 -m uvicorn backend.main:app --port 8000 --host 0.0.0.0 --reload
```
*Backend API Docs available at: `http://localhost:8000/docs`*

### 3. Frontend Setup & Launch

```powershell
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server (Port 3000)
npm run dev
```
*Frontend Application available at: `http://localhost:3000`*

---

## 📡 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and database connectivity |
| `GET` | `/api/models` | Safe public catalog of available synthesis models |
| `POST` | `/api/generate` | Synthesize content from raw source text (JSON) |
| `POST` | `/api/generate/upload` | Synthesize content from uploaded document (.pdf, .docx, .txt) |
| `GET` | `/api/runs` | List persisted synthesis runs from SQLite |
| `GET` | `/api/runs/{run_id}` | Retrieve complete details, outputs, and Fact Graph for a run |
| `GET` | `/api/runs/{run_id}/outputs` | Get generated text and slide deck representations |
| `GET` | `/api/runs/{run_id}/fact-graph` | Get structured Fact Graph JSON |
| `GET` | `/api/runs/{run_id}/guardrail` | Get Guardrail consistency check results & revision count |
| `GET` | `/api/runs/{run_id}/provenance` | Get claim-to-source-span provenance mappings |
| `GET` | `/api/outputs/{filename}/download` | Download rendered PPTX, DOCX, MD, and TXT files |
| `DELETE` | `/api/runs/{run_id}` | Delete a run from SQLite |

---

## 🧪 Automated Testing

To run the automated test suite verifying ingestion, persistence, provenance, multi-format rendering, and full LangGraph workflow execution:

```powershell
py -3.11 test_prism.py
```

---

## 📂 Project Structure

```
Prism/
├── backend/                        # FastAPI Backend Application
│   ├── main.py                     # App entrypoint, CORS, router inclusions
│   ├── .env                        # Backend secrets (GROQ_API_KEY, etc.)
│   ├── requirements.txt            # Backend dependencies
│   ├── api/
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   └── routes/
│   │       ├── health.py           # Health check endpoint
│   │       ├── models.py           # Safe model metadata
│   │       ├── generation.py       # Synthesis & upload endpoints
│   │       ├── runs.py             # SQLite runs management
│   │       └── outputs.py          # Assets & download endpoints
│   ├── uploads/                    # Uploaded source documents
│   └── outputs/                    # Rendered PPTX, DOCX, Markdown, Text
│
├── frontend/                       # React + Vite + Tailwind CSS Application
│   ├── src/
│   │   ├── api/client.js           # API Client communicating with FastAPI
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Brand header & real-time server health
│   │   │   ├── GeneratorForm.jsx   # Document input, channel & model selectors
│   │   │   ├── ProgressStepper.jsx # Real-time progressive step tracker
│   │   │   ├── FactGraphViewer.jsx # Interactive Fact Graph & Raw JSON view
│   │   │   ├── OutputCards.jsx     # Multi-channel content cards + Copy/Download
│   │   │   ├── PresentationViewer.jsx # Slide Deck viewer & PPTX downloader
│   │   │   ├── GuardrailBadge.jsx  # Guardrail Pass/Fail & revision audit
│   │   │   ├── ProvenanceDrawer.jsx# Truth grounding inspector modal
│   │   │   └── HistoryTable.jsx    # SQLite runs list & run inspector
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── RunsPage.jsx
│   │   │   └── AboutPage.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── prism/                          # Core PRISM Pipeline (Preserved Intact)
│   ├── config.py                   # Engine configuration & LLM retry logic
│   ├── state.py                    # PRISMState TypedDict
│   ├── schemas.py                  # Pydantic models (FactGraph, Slide, Guardrail)
│   ├── graph.py                    # Compiled LangGraph StateGraph
│   ├── rag/tools.py                # FAISS vector store & search_source tool
│   ├── nodes/                      # Pipeline nodes (Specialists, Guardrail, Render, etc.)
│   └── persistence/db.py           # SQLite storage layer
│
├── agent_flow.ipynb                # [READ-ONLY reference notebook]
├── app.py                          # [Streamlit fallback prototype retained]
├── test_prism.py                   # [Comprehensive test suite]
└── README.md
```
