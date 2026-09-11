import React, { useState, useEffect } from 'react';
import { getModels } from '../api/client';

const PRESETS = {
  prism_arch: {
    title: "PRISM Architecture Brief",
    category: "Technical Architecture",
    desc: "Multi-agent synthesis system with Fact Graph grounding",
    text: `PRISM is an AI-powered content generation system.
It takes a source document and creates multiple content formats.
PRISM uses a centralized Fact Graph to maintain consistency across generated outputs.
The Fact Graph extracts entities, claims with source spans, metrics, dates, and recommendations as the single source of truth.
The platform includes an automated Guardrail Consistency Critic that flags unsupported claims and triggers bounded revisions.
Recent benchmarks show PRISM reduces cross-channel authoring time by 75% while achieving 100% factual provenance verification.`
  },
  financial_brief: {
    title: "Nexus Q3 Financial Report",
    category: "Corporate Earnings",
    desc: "Revenue growth, margin expansion, and CapEx forecast",
    text: `Nexus Global reported Q3 2026 revenue of $4.8 billion, representing a 28% year-over-year growth driven by enterprise AI adoption.
Operating margins expanded to 34.2%, up 450 basis points from Q3 2025.
The company announced an expanded capital expenditure of $1.2 billion for next-generation GPU compute clusters.
CEO Marcus Vance confirmed that cloud net retention reached 132%, with over 4,200 enterprise customers actively deploying generative agents.
Key risks highlighted include semiconductor supply constraints and regulatory compliance across EU jurisdictions.`
  },
  clinical_trial: {
    title: "CardiaGuard Phase III Trial",
    category: "Healthcare & Life Sciences",
    desc: "Cardiovascular efficacy, safety profile, and FDA submission",
    text: `The Phase III trial of CardiaGuard demonstrated a 42% relative reduction in major cardiovascular events among 6,400 enrolled patients over a 24-month period.
Primary endpoints were met with statistical significance (p < 0.001).
Adverse event rates were comparable to placebo at 3.1% versus 2.9%.
The clinical advisory board recommends priority FDA filing by Q1 2027.
The study was conducted across 48 clinical research sites in North America and Western Europe.`
  },
  cyber_resilience: {
    title: "Global Cybersecurity Threat Advisory",
    category: "Cybersecurity & Risk",
    desc: "Critical zero-day mitigation and defense protocols",
    text: `The National Cyber Defense Alliance issued a Tier-1 alert regarding active exploitation of CVE-2026-9811 in legacy identity federation systems.
Over 340 infrastructure providers across banking and utilities were targeted in the preceding 72 hours.
Security operations teams are advised to enforce multi-factor hardware keys, rotate OAuth signing credentials, and isolate unpatched gateway proxies.
Initial incident response metrics indicate zero data exfiltration when segmentation policies were applied within 15 minutes of anomaly detection.`
  }
};

export default function GeneratorForm({ onSubmit, isLoading }) {
  // Input modes: 'custom' (user custom paste) | 'presets' (sample library) | 'file' (upload)
  const [inputMode, setInputMode] = useState('custom');
  const [customText, setCustomText] = useState('');
  const [activePresetKey, setActivePresetKey] = useState('prism_arch');
  const [selectedFile, setSelectedFile] = useState(null);
  const [pasteNotice, setPasteNotice] = useState(false);
  
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

  // Current active text based on mode
  const currentText = inputMode === 'custom' 
    ? customText 
    : (inputMode === 'presets' ? PRESETS[activePresetKey]?.text || '' : '');

  // Calculate text statistics
  const wordCount = currentText.trim() ? currentText.trim().split(/\s+/).length : 0;
  const charCount = currentText.length;
  const estimatedReadTime = Math.max(1, Math.ceil(wordCount / 200));

  // Handle Clipboard Paste
  const handlePasteClipboard = async () => {
    try {
      if (navigator.clipboard && navigator.clipboard.readText) {
        const text = await navigator.clipboard.readText();
        if (text) {
          setCustomText(text);
          setInputMode('custom');
          setPasteNotice(true);
          setTimeout(() => setPasteNotice(false), 2500);
        }
      } else {
        alert("Clipboard access not supported in this browser. Please use Ctrl+V / Cmd+V to paste.");
      }
    } catch (err) {
      console.warn("Clipboard read failed:", err);
      alert("Unable to access clipboard automatically. Please press Ctrl+V / Cmd+V inside the text box.");
    }
  };

  const handleClearCustomText = () => {
    setCustomText('');
  };

  const handleSelectPreset = (key) => {
    setActivePresetKey(key);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (selectedChannelsList.length === 0) {
      alert("Please select at least one output channel.");
      return;
    }

    if (inputMode === 'custom' || inputMode === 'presets') {
      const textToSubmit = inputMode === 'custom' ? customText.trim() : (PRESETS[activePresetKey]?.text || '').trim();
      
      if (!textToSubmit) {
        alert("Please enter or paste your custom source document text.");
        return;
      }

      onSubmit({
        input_type: 'text',
        input_text: textToSubmit,
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
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        
        {/* Section Header with Segmented Navigation */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 mb-5 border-b border-slate-100 gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-600 animate-pulse"></span>
              <h2 className="text-base font-bold text-slate-900">Source Document Input</h2>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Provide your raw text or file as the single factual ground truth for PRISM synthesis
            </p>
          </div>

          {/* Three-Tab Segmented Control */}
          <div className="inline-flex p-1 bg-slate-100/90 rounded-lg border border-slate-200 self-start sm:self-auto shadow-inner">
            <button
              type="button"
              id="tab-custom-input"
              onClick={() => setInputMode('custom')}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                inputMode === 'custom'
                  ? 'bg-white text-blue-700 shadow-sm border border-slate-200/60'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>✍️</span>
              <span>Custom Text (Paste)</span>
            </button>

            <button
              type="button"
              id="tab-presets"
              onClick={() => setInputMode('presets')}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                inputMode === 'presets'
                  ? 'bg-white text-blue-700 shadow-sm border border-slate-200/60'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>⚡</span>
              <span>Sample Presets</span>
            </button>

            <button
              type="button"
              id="tab-upload"
              onClick={() => setInputMode('file')}
              className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-md text-xs font-semibold transition-all ${
                inputMode === 'file'
                  ? 'bg-white text-blue-700 shadow-sm border border-slate-200/60'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <span>📄</span>
              <span>Upload Document</span>
            </button>
          </div>
        </div>

        {/* MODE 1: CUSTOM INPUT (USER'S OWN PASTED TEXT) */}
        {inputMode === 'custom' && (
          <div className="space-y-3 animate-fadeIn">
            
            {/* Toolbar for Custom Text */}
            <div className="flex flex-wrap items-center justify-between gap-2 p-2.5 bg-slate-50/80 rounded-lg border border-slate-200/70">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-medium text-slate-700">Custom Input Mode:</span>
                <span className="text-[11px] px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 font-semibold">
                  Direct Text
                </span>
                {pasteNotice && (
                  <span className="text-[11px] text-emerald-600 font-semibold animate-bounce">
                    ✓ Content Pasted from Clipboard!
                  </span>
                )}
              </div>

              <div className="flex items-center space-x-2">
                <button
                  type="button"
                  onClick={handlePasteClipboard}
                  className="px-2.5 py-1 rounded bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 text-xs font-medium transition-colors shadow-2xs flex items-center space-x-1"
                  title="Paste directly from your system clipboard"
                >
                  <span>📋</span>
                  <span>Paste from Clipboard</span>
                </button>

                {customText && (
                  <button
                    type="button"
                    onClick={handleClearCustomText}
                    className="px-2.5 py-1 rounded bg-white hover:bg-rose-50 text-rose-600 border border-rose-200 text-xs font-medium transition-colors"
                    title="Clear text area"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            {/* Custom Text Area */}
            <div className="relative">
              <textarea
                rows={9}
                value={customText}
                onChange={(e) => setCustomText(e.target.value)}
                placeholder="Paste your custom document, technical report, meeting minutes, press release, research brief, or notes here...

Example:
'Acme Corp unveiled its next-generation Quantum Orchestration Engine today, achieving 99.98% uptime in initial trials across 12 enterprise pilot sites. The new architecture cuts operational latency from 140ms to 12ms and introduces zero-trust cryptographic verification...'"
                className="w-full rounded-lg bg-white border border-slate-300 p-4 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 font-sans leading-relaxed transition-all shadow-inner"
              />

              {/* Character and Word Count Badge Bar */}
              <div className="flex items-center justify-between px-3 py-2 bg-slate-50 border-t border-slate-200 rounded-b-lg text-xs text-slate-500 font-mono -mt-2">
                <div className="flex items-center space-x-3">
                  <span><b>{wordCount}</b> words</span>
                  <span>•</span>
                  <span><b>{charCount}</b> characters</span>
                  <span>•</span>
                  <span>~{estimatedReadTime} min read</span>
                </div>
                <div>
                  {wordCount === 0 ? (
                    <span className="text-amber-600 font-sans text-[11px]">Paste text to begin</span>
                  ) : wordCount < 30 ? (
                    <span className="text-blue-600 font-sans text-[11px]">Short text (good for quick testing)</span>
                  ) : (
                    <span className="text-emerald-600 font-sans text-[11px]">✓ Ready for Fact Graph extraction</span>
                  )}
                </div>
              </div>
            </div>

          </div>
        )}

        {/* MODE 2: BENCHMARK PRESETS */}
        {inputMode === 'presets' && (
          <div className="space-y-4 animate-fadeIn">
            <div>
              <p className="text-xs text-slate-600 mb-2 font-medium">Select a curated benchmark document:</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {Object.entries(PRESETS).map(([key, item]) => {
                  const isSelected = activePresetKey === key;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => handleSelectPreset(key)}
                      className={`text-left p-3 rounded-lg border transition-all ${
                        isSelected
                          ? 'bg-blue-50/70 border-blue-500 ring-1 ring-blue-500/20 shadow-xs'
                          : 'bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50'
                      }`}
                    >
                      <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 block mb-1">
                        {item.category}
                      </span>
                      <h4 className="text-xs font-bold text-slate-900 leading-snug mb-1">
                        {item.title}
                      </h4>
                      <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                        {item.desc}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Preset Document Preview */}
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-800 font-mono whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
              {PRESETS[activePresetKey]?.text}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-500 font-mono">
              <span>Preset: <b>{PRESETS[activePresetKey]?.title}</b></span>
              <span>{wordCount} words • {charCount} chars</span>
            </div>
          </div>
        )}

        {/* MODE 3: UPLOAD DOCUMENT */}
        {inputMode === 'file' && (
          <div className="py-3 animate-fadeIn">
            {!selectedFile ? (
              <label className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 hover:border-blue-500 rounded-xl p-8 cursor-pointer bg-slate-50/50 hover:bg-slate-50 transition-all group">
                <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xl mb-3 group-hover:scale-110 transition-transform">
                  ↑
                </div>
                <span className="text-sm font-semibold text-slate-900">Upload source document</span>
                <span className="text-xs text-slate-500 mt-1">PDF, DOCX, or TXT (up to 25MB)</span>
                <span className="mt-3 px-3 py-1 rounded-md bg-white border border-slate-200 text-xs font-medium text-slate-700 shadow-2xs">
                  Browse Files
                </span>
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
              <div className="flex items-center justify-between p-4 rounded-lg bg-blue-50/50 border border-blue-200">
                <div className="flex items-center space-x-3">
                  <div className="w-9 h-9 rounded-md bg-blue-600 text-white flex items-center justify-center font-bold text-xs uppercase">
                    {selectedFile.name.split('.').pop()}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900">{selectedFile.name}</p>
                    <p className="text-[11px] text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB • Ready for extraction</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="px-2.5 py-1 text-xs text-rose-600 hover:text-rose-800 hover:bg-rose-50 border border-rose-200 rounded transition-colors"
                >
                  Remove File
                </button>
              </div>
            )}
          </div>
        )}

      </div>

      {/* 2. CONTROLS & OUTPUTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Synthesis Controls (7 cols) */}
        <div className="lg:col-span-7 bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
          <div className="pb-3 border-b border-slate-100">
            <h2 className="text-base font-bold text-slate-900">Synthesis Parameters</h2>
            <p className="text-xs text-slate-500">Configure audience, tone of voice, and model intelligence</p>
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
        <div className="lg:col-span-5 bg-white rounded-xl border border-slate-200 p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-3">
              <div>
                <h2 className="text-base font-bold text-slate-900">Output Channels</h2>
                <p className="text-xs text-slate-500">Select formats to generate</p>
              </div>
              <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
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
                  className={`p-2.5 rounded-lg border cursor-pointer transition-all flex items-start space-x-3 select-none ${
                    channels[id]
                      ? 'bg-blue-50/50 border-blue-300 text-slate-900 shadow-2xs'
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
                    <p className="text-xs font-bold text-slate-900">{label}</p>
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
          id="btn-generate-synthesis"
          disabled={isLoading || selectedChannelsList.length === 0}
          className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm shadow-md hover:shadow-lg transition-all flex items-center justify-center space-x-2.5 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span>{isLoading ? 'Synthesizing with PRISM Engine...' : 'Generate Multi-Channel Synthesis'}</span>
          {!isLoading && <span className="text-base">→</span>}
        </button>
      </div>

    </form>
  );
}

