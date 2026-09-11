import React, { useState, useEffect } from 'react';
import HistoryTable from '../components/HistoryTable';
import { getRuns, getRun, deleteRun } from '../api/client';

export default function RunsPage({ onInspectRun }) {
  const [runs, setRuns] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchRuns = async () => {
    setIsLoading(true);
    try {
      const data = await getRuns();
      setRuns(data);
    } catch (err) {
      console.error("Failed to fetch runs:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns();
  }, []);

  const handleSelectRun = async (runId) => {
    try {
      const detail = await getRun(runId);
      onInspectRun(detail);
    } catch (err) {
      alert("Failed to load run details: " + err.message);
    }
  };

  const handleDeleteRun = async (runId) => {
    if (!confirm(`Are you sure you want to delete run '${runId}'?`)) return;
    try {
      await deleteRun(runId);
      setRuns(prev => prev.filter(r => r.run_id !== runId));
    } catch (err) {
      alert("Failed to delete run: " + err.message);
    }
  };

  return (
    <div className="space-y-6 pb-16 pt-2">
      <div className="space-y-1 border-b border-slate-200 pb-4">
        <h1 className="text-xl sm:text-2xl font-bold text-slate-900">Synthesis Run History</h1>
        <p className="text-xs sm:text-sm text-slate-600">
          Inspect previous synthesis runs, review truth provenance, and download compiled assets from SQLite.
        </p>
      </div>

      <HistoryTable
        runs={runs}
        onSelectRun={handleSelectRun}
        onDeleteRun={handleDeleteRun}
        isLoading={isLoading}
      />
    </div>
  );
}
