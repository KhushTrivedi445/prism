import React from 'react';

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-10 pb-20 pt-2">
      
      {/* Title */}
      <div className="space-y-2 border-b border-slate-200 pb-6">
        <div className="inline-flex items-center px-2.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold">
          System Architecture
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          PRISM Architecture & Mechanics
        </h1>
        <p className="text-sm text-slate-600 max-w-2xl leading-relaxed">
          Provenance-Reasoned Intelligent Synthesis for Multi-channel Content
        </p>
      </div>

      {/* Core Concept */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm space-y-4">
        <h2 className="text-base font-semibold text-slate-900">The PRISM Paradigm</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-500">Step 1</span>
            <p className="text-sm font-bold text-slate-900">ONE SOURCE</p>
            <p className="text-xs text-slate-500">Raw PDF, DOCX, or text</p>
          </div>
          <div className="p-4 rounded-md bg-blue-50/50 border border-blue-200 space-y-1">
            <span className="text-[10px] uppercase font-bold text-blue-700">Step 2</span>
            <p className="text-sm font-bold text-blue-900">ONE FACT GRAPH</p>
            <p className="text-xs text-slate-600">Single Source of Truth</p>
          </div>
          <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-1">
            <span className="text-[10px] uppercase font-bold text-slate-500">Step 3</span>
            <p className="text-sm font-bold text-slate-900">MULTI-OUTPUTS</p>
            <p className="text-xs text-slate-500">With 100% Provenance</p>
          </div>
        </div>
      </div>

      {/* Architecture Flow Breakdown */}
      <div className="space-y-4">
        <h2 className="text-base font-semibold text-slate-900">End-to-End Pipeline Workflow</h2>

        <div className="space-y-3">
          {[
            {
              step: "01",
              title: "Ingestion & Normalization",
              desc: "Extracts text from raw documents (PDF, DOCX, TXT) and standardizes formatting, whitespace, and structural sections.",
            },
            {
              step: "02",
              title: "Fact Graph Extraction (Ground Truth Layer)",
              desc: "Extracts structured entities, factual claims (with source spans and confidence ratings), numerical metrics, dates, and recommendations as the single source of truth.",
            },
            {
              step: "03",
              title: "FAISS Vector Indexing & RAG",
              desc: "Splits normalized text into overlapping chunks and builds an in-memory FAISS vector index with sentence-transformers for precision contextual queries.",
            },
            {
              step: "04",
              title: "Multi-Agent Fan-Out",
              desc: "LangGraph state graph routes the Fact Graph concurrently to selected specialist agents (LinkedIn, Twitter/X, Executive Summary, Strategic Advisory, Slide Deck).",
            },
            {
              step: "05",
              title: "Guardrail Consistency Critic & Bounded Revision",
              desc: "Evaluates every generated output against the Fact Graph. If unsupported claims are detected, a targeted revision agent repairs only the failed channel in a bounded 1–2 cycle loop.",
            },
            {
              step: "06",
              title: "Provenance Grounding & Multi-Format Rendering",
              desc: "Maps every generated sentence back to its supporting Fact Graph claim and original source span. Renders PPTX, DOCX, Markdown, and TXT files, then commits run records to SQLite.",
            }
          ].map((item) => (
            <div key={item.step} className="p-4 rounded-md bg-white border border-slate-200 shadow-2xs flex items-start space-x-4">
              <span className="text-xs font-mono font-bold text-blue-700 bg-blue-50 px-2 py-1 rounded border border-blue-200 shrink-0">
                {item.step}
              </span>
              <div>
                <h3 className="text-sm font-semibold text-slate-900">{item.title}</h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Security Architecture */}
      <div className="p-4 rounded-md bg-slate-50 border border-slate-200 space-y-1.5">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
          Security & API Secret Isolation
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          PRISM enforces strict credential isolation: all LLM API tokens, Groq keys, and HuggingFace credentials remain isolated on the FastAPI backend in encrypted environment variables. The React client communicates exclusively via safe REST contracts with zero secret leakage.
        </p>
      </div>

    </div>
  );
}
