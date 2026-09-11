import React from 'react';

export default function GuardrailBadge({ guardrailResult, revisionCount }) {
  if (!guardrailResult) return null;

  const isPass = guardrailResult.overall_status === 'PASS';
  const outputs = guardrailResult.outputs || {};

  return (
    <div className={`p-4 rounded-lg border flex flex-col md:flex-row items-start md:items-center justify-between gap-4 ${
      isPass 
        ? 'bg-emerald-50/60 border-emerald-200 text-slate-800' 
        : 'bg-amber-50/60 border-amber-200 text-slate-800'
    }`}>
      <div className="flex items-start space-x-3">
        <div className={`w-6 h-6 rounded-full flex items-center justify-center font-bold text-xs shrink-0 mt-0.5 ${
          isPass ? 'bg-emerald-600 text-white' : 'bg-amber-600 text-white'
        }`}>
          {isPass ? '✓' : '!'}
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              Guardrail Review
            </span>
            <span className={`text-xs font-semibold px-2 py-0.5 rounded ${
              isPass 
                ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' 
                : 'bg-amber-100 text-amber-800 border border-amber-200'
            }`}>
              {isPass ? 'Passed Consistency Check' : 'Revision Performed'}
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-1">
            {isPass 
              ? 'All generated statements were verified and directly grounded in the Fact Graph.' 
              : 'Targeted revisions were applied to resolve unsupported factual claims.'}
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs">
        <span className="px-2.5 py-1 rounded bg-white border border-slate-200 font-mono text-slate-700 shadow-2xs">
          {revisionCount || 0} Revisions
        </span>
        
        <div className="flex flex-wrap items-center gap-1.5">
          {Object.entries(outputs).map(([channel, check]) => (
            <span
              key={channel}
              className={`px-2 py-0.5 rounded text-[11px] font-medium uppercase border ${
                check.status === 'PASS' 
                  ? 'bg-white text-emerald-700 border-emerald-200' 
                  : 'bg-white text-amber-700 border-amber-200'
              }`}
            >
              {check.status === 'PASS' ? '✓' : '!'} {channel}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
