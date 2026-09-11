import React, { useState } from 'react';
import GeneratorForm from '../components/GeneratorForm';
import ProgressStepper from '../components/ProgressStepper';
import GuardrailBadge from '../components/GuardrailBadge';
import OutputCards from '../components/OutputCards';
import FactGraphViewer from '../components/FactGraphViewer';
import ProvenanceDrawer from '../components/ProvenanceDrawer';
import { generateContent, generateContentWithUpload } from '../api/client';
import { formatToIST } from '../utils/date';

export default function DashboardPage({ currentRun, setCurrentRun }) {
  const [isLoading, setIsLoading] = useState(false);
  const [provenanceOpen, setProvenanceOpen] = useState(false);
  const [provenanceFilter, setProvenanceFilter] = useState('all');
  const [errorMsg, setErrorMsg] = useState(null);

  const handleGenerate = async (data, isUpload) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      let result;
      if (isUpload) {
        result = await generateContentWithUpload(data);
      } else {
        result = await generateContent(data);
      }
      setCurrentRun(result);
    } catch (err) {
      console.error("Generation failed:", err);
      const msg = err.response?.data?.detail || err.message || "Synthesis pipeline failed.";
      setErrorMsg(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenProvenance = (channel) => {
    setProvenanceFilter(channel || 'all');
    setProvenanceOpen(true);
  };

  return (
    <div className="space-y-8 pb-16">
      
      {/* Editorial Header */}
      {!currentRun && (
        <div className="space-y-2 border-b border-slate-200 pb-6 pt-2">
          <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
            Provenance-Reasoned Intelligent Synthesis
          </h1>
          <p className="text-sm text-slate-600 max-w-3xl leading-relaxed">
            Synthesize multi-channel content anchored in a centralized Fact Graph. All claims are verified by automated Guardrail critics with 100% source-span provenance tracking.
          </p>
        </div>
      )}

      {/* Error Alert */}
      {errorMsg && (
        <div className="p-4 rounded-md bg-rose-50 border border-rose-200 text-rose-800 text-xs sm:text-sm flex items-center justify-between">
          <span>{errorMsg}</span>
          <button 
            onClick={() => setErrorMsg(null)} 
            className="text-xs font-semibold text-rose-700 underline ml-4 hover:text-rose-900"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Generator Form */}
      {!currentRun && (
        <div>
          <GeneratorForm onSubmit={handleGenerate} isLoading={isLoading} />
        </div>
      )}

      {/* Progress Stepper */}
      {isLoading && (
        <div>
          <ProgressStepper />
        </div>
      )}

      {/* Results Workspace */}
      {currentRun && !isLoading && (
        <div className="space-y-6">
          
          {/* Active Run Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-5 rounded-lg bg-white border border-slate-200 shadow-sm">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono font-bold text-blue-700 uppercase tracking-wider">
                  Run: {currentRun.run_id}
                </span>
                <span className="text-xs text-slate-300">•</span>
                <span className="text-xs text-slate-500 font-mono">
                  {formatToIST(currentRun.created_at)}
                </span>
              </div>
              <h2 className="text-lg font-bold text-slate-900 mt-1">
                Synthesized Multi-Channel Portfolio
              </h2>
              <p className="text-xs text-slate-600 mt-0.5">
                Target: <b>{currentRun.audience}</b> • Tone: <b>{currentRun.tone}</b>
              </p>
            </div>

            <button
              onClick={() => setCurrentRun(null)}
              className="px-3.5 py-1.5 rounded-md bg-white hover:bg-slate-100 text-slate-700 border border-slate-300 text-xs font-semibold transition-colors shadow-2xs self-start sm:self-auto"
            >
              + New Generation
            </button>
          </div>

          {/* Guardrail Critic Verdict */}
          <GuardrailBadge 
            guardrailResult={currentRun.guardrail_result} 
            revisionCount={currentRun.revision_count} 
          />

          {/* Multi-Channel Outputs */}
          <OutputCards
            selectedOutputs={currentRun.selected_outputs || []}
            generatedOutputs={currentRun.generated_outputs || {}}
            renderedAssets={currentRun.rendered_assets || {}}
            onViewProvenance={handleOpenProvenance}
            presentationOutput={currentRun.generated_outputs?.presentation}
            pptxPath={currentRun.rendered_assets?.presentation}
          />

          {/* Fact Graph Explorer */}
          <FactGraphViewer factGraph={currentRun.fact_graph} />

        </div>
      )}

      {/* Provenance Drawer */}
      <ProvenanceDrawer
        isOpen={provenanceOpen}
        onClose={() => setProvenanceOpen(false)}
        provenanceList={currentRun?.provenance || []}
        filterChannel={provenanceFilter}
      />

    </div>
  );
}
