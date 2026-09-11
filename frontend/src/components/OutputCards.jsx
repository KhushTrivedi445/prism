import React, { useState } from 'react';
import PresentationViewer from './PresentationViewer';
import { getDownloadUrl } from '../api/client';

export default function OutputCards({ 
  selectedOutputs = [], 
  generatedOutputs = {}, 
  renderedAssets = {}, 
  onViewProvenance,
  presentationOutput,
  pptxPath
}) {
  const [activeTab, setActiveTab] = useState(selectedOutputs[0] || 'linkedin');
  const [copiedChannel, setCopiedChannel] = useState(null);

  const handleCopy = (text, channel) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopiedChannel(channel);
    setTimeout(() => setCopiedChannel(null), 2000);
  };

  const channelLabels = {
    linkedin: 'LinkedIn Post',
    twitter: 'Twitter / X Thread',
    summary: 'Executive Summary',
    advisory: 'Strategic Advisory',
    presentation: 'Presentation Deck'
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 shadow-sm space-y-6">
      
      {/* Header & Tab Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-base font-semibold text-slate-900">Generated Outputs</h2>
          <p className="text-xs text-slate-500">Multi-channel synthesis validated against the Fact Graph</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-1 bg-slate-100 p-1 rounded-md border border-slate-200 self-start sm:self-auto">
          {selectedOutputs.map((channel) => {
            const isActive = activeTab === channel;
            return (
              <button
                key={channel}
                onClick={() => setActiveTab(channel)}
                className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-white text-blue-700 shadow-xs font-semibold'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {channelLabels[channel] || channel}
              </button>
            );
          })}
        </div>
      </div>

      {/* Tab Content Display */}
      <div>
        {activeTab === 'presentation' ? (
          <PresentationViewer
            presentationData={presentationOutput || generatedOutputs.presentation}
            pptxPath={pptxPath || renderedAssets.presentation}
          />
        ) : (
          <div className="space-y-4">
            
            {/* Action Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-slate-50 rounded-md border border-slate-200">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-semibold text-slate-900">
                  {channelLabels[activeTab] || activeTab}
                </span>
                <span className="text-xs text-slate-400">•</span>
                <span className="text-xs text-slate-500 font-mono">
                  {generatedOutputs[activeTab] ? `${generatedOutputs[activeTab].length} characters` : '0 chars'}
                </span>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                {/* Copy Button */}
                <button
                  onClick={() => handleCopy(generatedOutputs[activeTab], activeTab)}
                  className="px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 border border-slate-300 transition-colors shadow-xs flex items-center space-x-1"
                >
                  <span>{copiedChannel === activeTab ? '✓ Copied' : 'Copy Content'}</span>
                </button>

                {/* Provenance Button */}
                <button
                  onClick={() => onViewProvenance(activeTab)}
                  className="px-3 py-1.5 rounded bg-blue-50 hover:bg-blue-100 text-xs font-semibold text-blue-700 border border-blue-200 transition-colors"
                >
                  View Provenance
                </button>

                {/* Download Actions */}
                {activeTab === 'summary' && renderedAssets.summary_docx && (
                  <a
                    href={getDownloadUrl(renderedAssets.summary_docx)}
                    download
                    className="px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 border border-slate-300 transition-colors shadow-xs"
                  >
                    Download .DOCX
                  </a>
                )}

                {activeTab === 'advisory' && renderedAssets.advisory_docx && (
                  <a
                    href={getDownloadUrl(renderedAssets.advisory_docx)}
                    download
                    className="px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 border border-slate-300 transition-colors shadow-xs"
                  >
                    Download .DOCX
                  </a>
                )}

                {activeTab === 'linkedin' && renderedAssets.linkedin_md && (
                  <a
                    href={getDownloadUrl(renderedAssets.linkedin_md)}
                    download
                    className="px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 border border-slate-300 transition-colors shadow-xs"
                  >
                    Download .MD
                  </a>
                )}

                {activeTab === 'twitter' && renderedAssets.twitter_md && (
                  <a
                    href={getDownloadUrl(renderedAssets.twitter_md)}
                    download
                    className="px-3 py-1.5 rounded bg-white hover:bg-slate-50 text-xs font-medium text-slate-700 border border-slate-300 transition-colors shadow-xs"
                  >
                    Download .MD
                  </a>
                )}
              </div>
            </div>

            {/* Document Reading Pane */}
            <div className="p-6 rounded-md bg-white border border-slate-200 text-sm text-slate-800 leading-relaxed whitespace-pre-wrap font-sans min-h-[220px]">
              {generatedOutputs[activeTab] || (
                <span className="text-slate-400 italic">No output generated for this channel.</span>
              )}
            </div>

          </div>
        )}
      </div>

    </div>
  );
}
