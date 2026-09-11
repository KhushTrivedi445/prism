import React, { useState, useEffect } from 'react';
import { getModels } from '../api/client';

const PRESETS = {
  prism_arch: {
    title: "PRISM Architecture Brief",
    text: `PRISM is an AI-powered content generation system.
It takes a source document and creates multiple content formats.
PRISM uses a centralized Fact Graph to maintain consistency across generated outputs.
The Fact Graph extracts entities, claims with source spans, metrics, dates, and recommendations as the single source of truth.
The platform includes an automated Guardrail Consistency Critic that flags unsupported claims and triggers bounded revisions.
Recent benchmarks show PRISM reduces cross-channel authoring time by 75% while achieving 100% factual provenance verification.`
  },
  financial_brief: {
    title: "Nexus Q3 Financial Report",
    text: `Nexus Global reported Q3 2026 revenue of $4.8 billion, representing a 28% year-over-year growth driven by enterprise AI adoption.
Operating margins expanded to 34.2%, up 450 basis points from Q3 2025.
The company announced an expanded capital expenditure of $1.2 billion for next-generation GPU compute clusters.
CEO Marcus Vance confirmed that cloud net retention reached 132%, with over 4,200 enterprise customers actively deploying generative agents.
Key risks highlighted include semiconductor supply constraints and regulatory compliance across EU jurisdictions.`
  },
  clinical_trial: {
    title: "CardiaGuard Phase III Brief",
    text: `The Phase III trial of CardiaGuard demonstrated a 42% relative reduction in major cardiovascular events among 6,400 enrolled patients over a 24-month period.
Primary endpoints were met with statistical significance (p < 0.001).
Adverse event rates were comparable to placebo at 3.1% versus 2.9%.
The clinical advisory board recommends priority FDA filing by Q1 2027.
The study was conducted across 48 clinical research sites in North America and Western Europe.`
  }
};

export default function GeneratorForm({ onSubmit, isLoading }) {
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file'
  const [inputText, setInputText] = useState(PRESETS.prism_arch.text);
  const [selectedFile, setSelectedFile] = useState(null);
  
  const [tone, setTone] = useState('Professional');
  const [audience, setAudience] = useState('Enterprise Executives');
  const [objective, setObjective] = useState('Multi-channel synthesis with 100% provenance verification');
  const [model, setModel] = useState('openai/gpt-oss-120b');
  const [modelsList, setModelsList] = useState([]);

  // Channels state
  const [channels, setChannels] = useState({
    linkedin: true,
    twitter: true,
    summary: true,
    advisory: true,
    presentation: true,
  });

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const data = await getModels();
        setModelsList(data);
        if (data.length > 0) {
          const rec = data.find(m => m.recommended) || data[0];
          setModel(rec.id);
        }
      } catch (err) {
        console.error("Failed to load models:", err);
      }
    };
    fetchModels();
  }, []);

  const handleChannelToggle = (key) => {
    setChannels(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const selectedChannelsList = Object.keys(channels).filter(k => channels[k]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedChannelsList.length === 0) {
      alert("Please select at least one output channel.");
      return;
    }

    if (inputMode === 'text') {
      if (!inputText.trim()) {
        alert("Please enter source document text.");
        return;
      }
      onSubmit({
        input_type: 'text',
        input_text: inputText,
        tone,
        audience,
        objective,
        model,
        selected_outputs: selectedChannelsList
      }, false);
    } else {
      if (!selectedFile) {
        alert("Please upload a PDF, DOCX, or TXT file.");
        return;
      }
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('tone', tone);
      formData.append('audience', audience);
      formData.append('objective', objective);
      formData.append('model', model);
      formData.append('selected_outputs', JSON.stringify(selectedChannelsList));

      onSubmit(formData, true);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      
      {/* 1. SOURCE DOCUMENT SECTION */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-3">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Source Document</h2>
            <p className="text-xs text-slate-500">Provide the single source of truth for factual grounding</p>
          </div>

          {/* Segmented Control */}
          <div className="inline-flex p-1 bg-slate-100 rounded-md border border-slate-200 self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setInputMode('text')}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                inputMode === 'text'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Paste Text
            </button>
            <button
              type="button"
              onClick={() => setInputMode('file')}
              className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                inputMode === 'file'
                  ? 'bg-white text-slate-900 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Upload Document
            </button>
          </div>
        </div>

        {inputMode === 'text' ? (
          <div className="space-y-3">
            {/* Quick Presets */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
              <span className="text-slate-500 font-medium whitespace-nowrap">Load Preset:</span>
              {Object.entries(PRESETS).map(([key, item]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setInputText(item.text)}
                  className="px-2.5 py-1 rounded bg-slate-50 hover:bg-slate-100 text-slate-700 border border-slate-200 whitespace-nowrap transition-colors"
                >
                  {item.title}
                </button>
              ))}
            </div>

            <textarea
              rows={8}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Paste your source document, technical report, clinical brief, or announcement here..."
              className="w-full rounded-md bg-white border border-slate-300 p-3.5 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 font-mono transition-all"
            />
          </div>
        ) : (
          <div className="py-4">
            {!selectedFile ? (
              <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-lg p-8 cursor-pointer bg-slate-50/50 hover:bg-slate-50 transition-all">
                <div className="w-10 h-10 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-lg mb-2">
                  ↑
                </div>
                <span className="text-sm font-medium text-slate-800">Select document or drag and drop</span>
                <span className="text-xs text-slate-500 mt-1">PDF, DOCX, or TXT (up to 25MB)</span>
                <input
                  type="file"
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      setSelectedFile(e.target.files[0]);
                    }
                  }}
                />
              </label>
            ) : (
              <div className="flex items-center justify-between p-3.5 rounded-md bg-slate-50 border border-slate-200">
                <div>
                  <p className="text-sm font-medium text-slate-900">{selectedFile.name}</p>
                  <p className="text-xs text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="px-2.5 py-1 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-200 rounded transition-colors"
                >
                  Remove
                </button>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 2. CONTROLS & OUTPUTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Synthesis Controls (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-lg border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="pb-3 border-b border-slate-100">
            <h2 className="text-base font-semibold text-slate-900">Synthesis Parameters</h2>
            <p className="text-xs text-slate-500">Configure audience, voice, and engine settings</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Target Audience</label>
              <select
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
                className="w-full rounded-md bg-white border border-slate-300 px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
              >
                <option value="Enterprise Executives">Enterprise Executives & C-Suite</option>
                <option value="Technical Engineers">Software Engineers & Data Architects</option>
                <option value="General Public">General Audience / Public</option>
                <option value="Investors & Board">Investors & Board Members</option>
                <option value="Industry Analysts">Industry Analysts & Researchers</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1.5">Tone of Voice</label>
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="w-full rounded-md bg-white border border-slate-300 px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
              >
                <option value="Professional">Professional & Authoritative</option>
                <option value="Executive">Executive & Visionary</option>
                <option value="Technical">Technical & Analytical</option>
                <option value="Conversational">Conversational & Engaging</option>
                <option value="Direct">Direct & Concise</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">LLM Engine</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full rounded-md bg-white border border-slate-300 px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
            >
              {modelsList.map(m => (
                <option key={m.id} value={m.id}>
                  {m.name} ({m.provider}) {m.recommended ? '— Recommended' : ''}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Strategic Objective</label>
            <input
              type="text"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
              placeholder="e.g. Synthesize core takeaways with complete provenance"
              className="w-full rounded-md bg-white border border-slate-300 px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
            />
          </div>
        </div>

        {/* Channels Selector (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-lg border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
              <div>
                <h2 className="text-base font-semibold text-slate-900">Output Channels</h2>
                <p className="text-xs text-slate-500">Select formats to generate</p>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700 border border-slate-200">
                {selectedChannelsList.length} Selected
              </span>
            </div>

            <div className="space-y-2">
              {[
                { id: 'linkedin', label: 'LinkedIn Post', desc: 'Professional thought-leadership article' },
                { id: 'twitter', label: 'Twitter / X Thread', desc: 'Structured multi-tweet synthesis' },
                { id: 'summary', label: 'Executive Summary', desc: 'High-level brief (DOCX/MD)' },
                { id: 'advisory', label: 'Strategic Advisory', desc: 'Actionable guidance and risk analysis' },
                { id: 'presentation', label: 'Presentation Deck', desc: 'Structured slides & downloadable PPTX' },
              ].map(({ id, label, desc }) => (
                <label
                  key={id}
                  className={`p-2.5 rounded-md border cursor-pointer transition-all flex items-start space-x-3 select-none ${
                    channels[id]
                      ? 'bg-blue-50/50 border-blue-200 text-slate-900'
                      : 'bg-white border-slate-200 text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={channels[id]}
                    onChange={() => handleChannelToggle(id)}
                    className="mt-0.5 w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-slate-900">{label}</p>
                    <p className="text-[11px] text-slate-500 leading-tight">{desc}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* 3. SUBMIT BUTTON */}
      <div className="flex justify-end pt-2">
        <button
          type="submit"
          disabled={isLoading || selectedChannelsList.length === 0}
          className="w-full sm:w-auto px-8 py-3 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm shadow-sm transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>{isLoading ? 'Synthesizing with PRISM...' : 'Generate Multi-Channel Synthesis'}</span>
        </button>
      </div>

    </form>
  );
}
