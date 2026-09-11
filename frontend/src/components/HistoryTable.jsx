import React from 'react';
import { formatToIST } from '../utils/date';

export default function HistoryTable({ runs = [], onSelectRun, onDeleteRun, isLoading }) {
  if (isLoading) {
    return (
      <div className="p-12 text-center bg-white rounded-lg border border-slate-200 text-slate-500 text-sm">
        Loading historical runs from SQLite database...
      </div>
    );
  }

  if (runs.length === 0) {
    return (
      <div className="p-12 text-center bg-white rounded-lg border border-slate-200 space-y-2">
        <h3 className="text-sm font-semibold text-slate-900">No Previous Runs</h3>
        <p className="text-xs text-slate-500 max-w-sm mx-auto">
          Runs generated from the dashboard are automatically persisted in your local SQLite database.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden space-y-0">
      <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-slate-50/50">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">Persisted Synthesis Runs</h2>
          <p className="text-xs text-slate-500">Historical runs saved locally in SQLite (IST / Asia-Kolkata)</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-0.5 rounded bg-white text-slate-700 border border-slate-200 shadow-2xs">
          {runs.length} Runs Recorded
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-700">
          <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200 uppercase tracking-wider">
            <tr>
              <th className="px-4 py-3">Run ID</th>
              <th className="px-4 py-3">Date / Time (IST)</th>
              <th className="px-4 py-3">Audience & Tone</th>
              <th className="px-4 py-3">Outputs</th>
              <th className="px-4 py-3">Revisions</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {runs.map((run) => (
              <tr 
                key={run.run_id} 
                className="hover:bg-slate-50 transition-colors"
              >
                <td className="px-4 py-3 font-mono font-semibold text-blue-700">
                  {run.run_id}
                </td>
                <td className="px-4 py-3 text-slate-600 font-mono text-[11px]">
                  {formatToIST(run.created_at)}
                </td>
                <td className="px-4 py-3">
                  <span className="font-semibold text-slate-900 block">{run.audience}</span>
                  <span className="text-[11px] text-slate-500">{run.tone}</span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {(run.selected_outputs || []).map((ch) => (
                      <span key={ch} className="px-1.5 py-0.5 rounded text-[10px] uppercase font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                        {ch}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-100 text-slate-700 border border-slate-200">
                    {run.revision_count || 0} revs
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end space-x-1.5">
                    <button
                      onClick={() => onSelectRun(run.run_id)}
                      className="px-2.5 py-1 rounded bg-white hover:bg-slate-100 text-blue-700 border border-slate-300 text-xs font-semibold transition-colors shadow-2xs"
                    >
                      Inspect
                    </button>
                    <button
                      onClick={() => onDeleteRun(run.run_id)}
                      className="px-2 py-1 rounded text-rose-600 hover:bg-rose-50 border border-transparent hover:border-rose-200 transition-colors text-xs font-medium"
                      title="Delete run"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
