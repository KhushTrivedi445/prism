import React, { useState } from 'react';

export default function FactGraphViewer({ factGraph }) {
  const [activeTab, setActiveTab] = useState('claims');
  const [showRawJson, setShowRawJson] = useState(false);
  const [copied, setCopied] = useState(false);

  if (!factGraph) {
    return (
      <div className="p-8 text-center bg-white rounded-lg border border-slate-200 text-slate-500 text-sm">
        No Fact Graph available.
      </div>
    );
  }

  const {
    synopsis = '',
    entities = [],
    claims = [],
    metrics = [],
    dates = [],
    risks = [],
    recommendations = [],
    quotes = []
  } = factGraph;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(factGraph, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm space-y-6">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="text-base font-semibold text-slate-900">Fact Graph</h2>
            <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
              Single Source of Truth
            </span>
          </div>
          <p className="text-xs text-slate-500">Extracted factual claims, verified source spans, and entities</p>
        </div>

        <button
          type="button"
          onClick={() => setShowRawJson(!showRawJson)}
          className="px-3 py-1.5 rounded bg-slate-50 hover:bg-slate-100 text-xs font-medium text-slate-700 border border-slate-300 transition-colors self-start sm:self-auto"
        >
          {showRawJson ? 'Show Formatted View' : 'View Raw JSON'}
        </button>
      </div>

      {/* Raw JSON Mode */}
      {showRawJson ? (
        <div className="relative">
          <button
            onClick={handleCopyJson}
            className="absolute top-3 right-3 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-xs font-medium text-slate-700 border border-slate-300 shadow-2xs"
          >
            {copied ? '✓ Copied' : 'Copy JSON'}
          </button>
          <pre className="p-4 rounded-md bg-slate-900 text-slate-100 text-xs font-mono overflow-x-auto max-h-[460px] leading-relaxed">
            {JSON.stringify(factGraph, null, 2)}
          </pre>
        </div>
      ) : (
        <>
          {/* Neutral Synopsis */}
          {synopsis && (
            <div className="p-4 rounded-md bg-slate-50 border border-slate-200">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block mb-1">
                Factual Synopsis
              </span>
              <p className="text-xs sm:text-sm text-slate-800 leading-relaxed">{synopsis}</p>
            </div>
          )}

          {/* Metric Summary Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center">
            {[
              { label: 'Claims', count: claims.length },
              { label: 'Entities', count: entities.length },
              { label: 'Metrics', count: metrics.length },
              { label: 'Dates', count: dates.length },
              { label: 'Risks & Recs', count: recommendations.length + risks.length },
            ].map(({ label, count }) => (
              <div key={label} className="p-3 rounded-md bg-slate-50 border border-slate-200">
                <span className="text-lg font-bold text-slate-900">{count}</span>
                <p className="text-[11px] text-slate-500 font-medium">{label}</p>
              </div>
            ))}
          </div>

          {/* Sub Navigation */}
          <div className="flex border-b border-slate-200 space-x-1 overflow-x-auto">
            {[
              { id: 'claims', label: `Claims (${claims.length})` },
              { id: 'entities', label: `Entities (${entities.length})` },
              { id: 'metrics', label: `Metrics (${metrics.length})` },
              { id: 'dates', label: `Dates (${dates.length})` },
              { id: 'recommendations', label: `Recs & Risks (${recommendations.length + risks.length})` },
              { id: 'quotes', label: `Quotes (${quotes.length})` }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap border-b-2 ${
                  activeTab === tab.id
                    ? 'border-blue-600 text-blue-600 font-semibold'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
            
            {/* Claims */}
            {activeTab === 'claims' && (
              claims.length > 0 ? (
                claims.map((claim, idx) => (
                  <div key={idx} className="p-3.5 rounded-md bg-slate-50/70 border border-slate-200 space-y-2">
                    <div className="flex items-start justify-between gap-3">
                      <p className="text-xs font-medium text-slate-900 leading-snug">
                        {claim.text}
                      </p>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                        {Math.round((claim.confidence || 0.95) * 100)}% Conf
                      </span>
                    </div>
                    {claim.source_span && (
                      <div className="p-2.5 rounded bg-white border border-slate-200 text-xs text-slate-600 font-mono">
                        <span className="text-slate-400 select-none block text-[10px] uppercase font-bold mb-0.5">Source Span:</span>
                        "{claim.source_span}"
                      </div>
                    )}
                  </div>
                ))
              ) : <p className="text-xs text-slate-400 py-4 text-center">No factual claims extracted.</p>
            )}

            {/* Entities */}
            {activeTab === 'entities' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                {entities.map((e, idx) => (
                  <div key={idx} className="p-2.5 rounded-md bg-slate-50 border border-slate-200 flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-900">{e.name}</span>
                    <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-700">
                      {e.type}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Metrics */}
            {activeTab === 'metrics' && (
              metrics.map((m, idx) => (
                <div key={idx} className="p-3 rounded-md bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <span className="text-xs font-semibold text-slate-900">{m.name}: </span>
                    <span className="text-xs font-bold text-blue-700">{m.value}</span>
                    <p className="text-[11px] text-slate-500 mt-0.5">{m.context}</p>
                  </div>
                  {m.source_span && (
                    <span className="text-[11px] font-mono text-slate-600 bg-white px-2 py-1 rounded border border-slate-200">
                      "{m.source_span}"
                    </span>
                  )}
                </div>
              ))
            )}

            {/* Dates */}
            {activeTab === 'dates' && (
              dates.map((d, idx) => (
                <div key={idx} className="p-2.5 rounded-md bg-slate-50 border border-slate-200 flex items-center space-x-3">
                  <span className="text-xs font-bold text-slate-900 bg-white px-2 py-0.5 rounded border border-slate-200">
                    {d.date}
                  </span>
                  <span className="text-xs text-slate-700">{d.event}</span>
                </div>
              ))
            )}

            {/* Recommendations & Risks */}
            {activeTab === 'recommendations' && (
              <div className="space-y-3">
                {risks.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-rose-700 mb-1.5">
                      Identified Risks
                    </h4>
                    <div className="space-y-1">
                      {risks.map((r, i) => (
                        <div key={i} className="p-2 rounded bg-rose-50/50 border border-rose-200 text-xs text-rose-900">
                          • {r}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {recommendations.length > 0 && (
                  <div>
                    <h4 className="text-[11px] font-bold uppercase tracking-wider text-blue-700 mb-1.5">
                      Strategic Recommendations
                    </h4>
                    <div className="space-y-1">
                      {recommendations.map((rec, i) => (
                        <div key={i} className="p-2 rounded bg-blue-50/50 border border-blue-200 text-xs text-blue-900">
                          • {rec.text}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Quotes */}
            {activeTab === 'quotes' && (
              quotes.length > 0 ? (
                quotes.map((q, idx) => (
                  <div key={idx} className="p-3 rounded-md bg-slate-50 border border-slate-200 text-xs text-slate-700 italic">
                    "{q.text}"
                    {q.speaker && <span className="block not-italic font-semibold text-slate-500 mt-1">— {q.speaker}</span>}
                  </div>
                ))
              ) : <p className="text-xs text-slate-400 py-4 text-center">No quotes extracted.</p>
            )}

          </div>
        </>
      )}

    </div>
  );
}
