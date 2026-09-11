import React, { useState } from 'react';
import { getDownloadUrl } from '../api/client';

export default function PresentationViewer({ presentationData, pptxPath }) {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  if (!presentationData) return null;

  const title = presentationData.title || "PRISM Presentation Deck";
  const slides = presentationData.slides || [];
  const activeSlide = slides[currentSlideIndex] || { title: "Slide", content: [] };

  const pptxDownloadUrl = pptxPath ? getDownloadUrl(pptxPath) : null;

  return (
    <div className="space-y-4">
      {/* Top Bar with PPTX Download */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3 bg-slate-50 rounded-md border border-slate-200">
        <div>
          <h3 className="text-xs font-semibold text-slate-900">{title}</h3>
          <p className="text-[11px] text-slate-500">{slides.length} Generated Slides</p>
        </div>
        
        {pptxDownloadUrl && (
          <a
            href={pptxDownloadUrl}
            download
            className="px-3.5 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-colors self-start sm:self-auto"
          >
            Download Presentation (.PPTX)
          </a>
        )}
      </div>

      {/* Slide Canvas */}
      <div className="aspect-[16/9] w-full rounded-lg bg-white border border-slate-300 p-8 sm:p-12 flex flex-col justify-between shadow-xs">
        
        {/* Slide Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <span className="text-xs font-mono font-semibold text-slate-500 uppercase tracking-wider">
            Slide {currentSlideIndex + 1} of {slides.length}
          </span>
          <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
            PRISM Deck
          </span>
        </div>

        {/* Slide Content */}
        <div className="my-auto space-y-5 py-4">
          <h2 className="text-xl sm:text-2xl lg:text-3xl font-bold text-slate-900 tracking-tight leading-snug">
            {activeSlide.title}
          </h2>
          <div className="space-y-3">
            {activeSlide.content && activeSlide.content.map((bullet, idx) => (
              <div key={idx} className="flex items-start space-x-3 text-slate-700 text-sm sm:text-base leading-relaxed">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-2.5 shrink-0" />
                <span>{bullet}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Slide Footer & Navigation */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <p className="text-xs text-slate-400 truncate max-w-[240px] sm:max-w-md">{title}</p>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentSlideIndex(Math.max(0, currentSlideIndex - 1))}
              disabled={currentSlideIndex === 0}
              className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="text-xs text-slate-500 font-mono px-1">
              {currentSlideIndex + 1} / {slides.length}
            </span>
            <button
              onClick={() => setCurrentSlideIndex(Math.min(slides.length - 1, currentSlideIndex + 1))}
              disabled={currentSlideIndex === slides.length - 1}
              className="px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>

      </div>

      {/* Slide Thumbnails List */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 pt-1">
        {slides.map((s, idx) => (
          <div
            key={idx}
            onClick={() => setCurrentSlideIndex(idx)}
            className={`p-2 rounded-md border cursor-pointer transition-all ${
              currentSlideIndex === idx
                ? 'bg-blue-50 border-blue-500 ring-1 ring-blue-500'
                : 'bg-white border-slate-200 hover:bg-slate-50'
            }`}
          >
            <span className="text-[10px] font-semibold text-slate-500 block">Slide {idx + 1}</span>
            <p className="text-xs font-medium text-slate-900 truncate">{s.title}</p>
          </div>
        ))}
      </div>

    </div>
  );
}
