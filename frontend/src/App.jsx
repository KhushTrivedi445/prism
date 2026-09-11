import React, { useState } from 'react';
import Navbar from './components/Navbar';
import DashboardPage from './pages/DashboardPage';
import RunsPage from './pages/RunsPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [currentRun, setCurrentRun] = useState(null);

  const handleInspectRunFromHistory = (runDetail) => {
    setCurrentRun(runDetail);
    setActivePage('dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col selection:bg-blue-100 selection:text-blue-900">
      <Navbar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        onNewGeneration={() => {
          setCurrentRun(null);
          setActivePage('dashboard');
        }}
      />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activePage === 'dashboard' && (
          <DashboardPage 
            currentRun={currentRun} 
            setCurrentRun={setCurrentRun} 
          />
        )}
        {activePage === 'runs' && (
          <RunsPage 
            onInspectRun={handleInspectRunFromHistory} 
          />
        )}
        {activePage === 'about' && (
          <AboutPage />
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="font-medium text-slate-700">PRISM — Provenance-Reasoned Intelligent Synthesis</p>
          <p className="text-slate-400">Enterprise Multi-Channel Content Grounding & Verification</p>
        </div>
      </footer>
    </div>
  );
}
