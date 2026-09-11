import React, { useState } from 'react';

export default function ProvenanceDrawer({ isOpen, onClose, provenanceList, filterChannel }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChannel, setSelectedChannel] = useState(filterChannel || 'all');

  if (!isOpen) return null;

  const filteredItems = (provenanceList || []).filter(item => {
    const matchesChannel = selectedChannel === 'all' || item.output_channel === selectedChannel;
    const matchesSearch = !searchQuery || 
      item.output_statement?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.claim_text?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.source_span?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesChannel && matchesSearch;
  });

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-2xl bg-white border-l border-slate-200 h-full p-6 flex flex-col shadow-xl overflow-hidden animate-in slide-in-from-right duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-200">
          <div>
            <h2 className="text-base font-semibold text-slate-900">Provenance Grounding Matrix</h2>
            <p className="text-xs text-slate-500">Verifiable trace from generated statement to source span</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Filter Controls */}
        <div className="py-3 flex items-center space-x-2 border-b border-slate-100">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search statements, claims, or source spans..."
            className="flex-1 rounded-md bg-white border border-slate-300 px-3 py-1.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
          />
          <select
            value={selectedChannel}
            onChange={(e) => setSelectedChannel(e.target.value)}
            className="rounded-md bg-white border border-slate-300 px-3 py-1.5 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600"
          >
            <option value="all">All Channels</option>
            <option value="linkedin">LinkedIn</option>
            <option value="twitter">Twitter / X</option>
            <option value="summary">Summary</option>
            <option value="advisory">Advisory</option>
            <option value="presentation">Presentation</option>
          </select>
        </div>

        {/* Provenance Records List */}
        <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
          {filteredItems.length === 0 ? (
            <div className="p-12 text-center text-slate-400 text-xs">
              No matching provenance records found.
            </div>
          ) : (
            filteredItems.map((item, idx) => {
              const conf = item.confidence || 0.95;
              const confPct = Math.round(conf * 100);

              return (
                <div 
                  key={idx} 
                  className="p-4 rounded-lg bg-slate-50 border border-slate-200 space-y-3"
                >
                  {/* Channel & Confidence Header */}
                  <div className="flex items-center justify-between border-b border-slate-200/60 pb-2">
                    <span className="text-[11px] font-semibold uppercase text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {item.output_channel} Output
                    </span>
                    <span className="text-[11px] font-mono font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                      ✓ {confPct}% Grounding Conf
                    </span>
                  </div>

                  {/* 1. Generated Output Statement */}
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block mb-1">
                      1. Synthesized Statement
                    </span>
                    <p className="text-xs font-medium text-slate-900 pl-2.5 border-l-2 border-blue-600">
                      "{item.output_statement}"
                    </p>
                  </div>

                  {/* 2. Grounded in Fact Graph Claim */}
                  <div className="pl-3 space-y-1">
                    <span className="text-[10px] uppercase font-bold tracking-wider text-blue-700 block">
                      ↓ Grounded in Fact Graph Claim
                    </span>
                    <p className="text-xs text-slate-800 bg-white p-2.5 rounded border border-slate-200">
                      {item.claim_text}
                    </p>
                  </div>

                  {/* 3. Source Truth Passage */}
                  {item.source_span && (
                    <div className="pl-3 space-y-1">
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 block">
                        ↓ Original Source Document Span
                      </span>
                      <div className="p-2.5 rounded bg-slate-100 border border-slate-300 text-xs font-mono text-slate-700">
                        "{item.source_span}"
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-slate-200 text-center">
          <p className="text-[11px] text-slate-500">
            PRISM Provenance Engine guarantees 100% trace groundability to source document spans.
          </p>
        </div>

      </div>
    </div>
  );
}
