import React, { useState, useEffect } from 'react';

const STEPS = [
  { id: 1, label: 'Ingestion & Normalization', desc: 'Parsing structure & cleaning text' },
  { id: 2, label: 'Fact Graph Extraction', desc: 'Extracting claims, metrics & dates' },
  { id: 3, label: 'FAISS Vector Indexing', desc: 'Embedding context for precision RAG' },
  { id: 4, label: 'Multi-Agent Fan-Out', desc: 'Executing specialist writers' },
  { id: 5, label: 'Guardrail Critic', desc: 'Validating grounding vs Fact Graph' },
  { id: 6, label: 'Rendering & Persistence', desc: 'Compiling assets & saving SQLite record' }
];

export default function ProgressStepper() {
  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    const intervals = [
      setTimeout(() => setCurrentStep(2), 2000),
      setTimeout(() => setCurrentStep(3), 5500),
      setTimeout(() => setCurrentStep(4), 8500),
      setTimeout(() => setCurrentStep(5), 13000),
      setTimeout(() => setCurrentStep(6), 18000),
    ];
    return () => intervals.forEach(clearTimeout);
  }, []);

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm my-6 space-y-6">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-900">Synthesis Pipeline Running</h3>
          <p className="text-xs text-slate-500">Executing LangGraph state graph across specialist agents</p>
        </div>
        <span className="text-xs font-mono font-medium text-blue-700 bg-blue-50 px-2.5 py-1 rounded border border-blue-200">
          Step {currentStep} of 6
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {STEPS.map((step) => {
          const isDone = currentStep > step.id;
          const isCurrent = currentStep === step.id;

          return (
            <div
              key={step.id}
              className={`p-3 rounded-md border text-left transition-all ${
                isDone
                  ? 'bg-slate-50 border-slate-200 text-slate-700'
                  : isCurrent
                  ? 'bg-blue-50/50 border-blue-400 text-slate-900 shadow-2xs'
                  : 'bg-white border-slate-100 text-slate-400'
              }`}
            >
              <div className="flex items-center space-x-1.5 mb-1.5">
                <span className={`w-4 h-4 rounded-full flex items-center justify-center text-[10px] font-bold ${
                  isDone 
                    ? 'bg-emerald-600 text-white' 
                    : isCurrent 
                    ? 'bg-blue-600 text-white animate-pulse' 
                    : 'bg-slate-200 text-slate-600'
                }`}>
                  {isDone ? '✓' : step.id}
                </span>
                <span className="text-xs font-semibold">{step.label}</span>
              </div>
              <p className="text-[11px] text-slate-500 leading-snug">{step.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
