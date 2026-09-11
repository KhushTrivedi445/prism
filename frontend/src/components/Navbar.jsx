import React, { useState, useEffect } from 'react';
import { getHealth } from '../api/client';

export default function Navbar({ activePage, setActivePage, onNewGeneration }) {
  const [serverStatus, setServerStatus] = useState('checking');

  useEffect(() => {
    const checkServer = async () => {
      try {
        await getHealth();
        setServerStatus('online');
      } catch (err) {
        setServerStatus('offline');
      }
    };
    checkServer();
    const interval = setInterval(checkServer, 20000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200 bg-white shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div 
          onClick={() => setActivePage('dashboard')}
          className="flex items-center space-x-3 cursor-pointer select-none"
        >
          <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center font-bold text-sm tracking-wider shadow-sm">
            P
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight text-slate-900">PRISM</span>
              <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-blue-50 text-blue-700 border border-blue-200">
                Enterprise
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 sm:space-x-2">
          <button
            onClick={() => setActivePage('dashboard')}
            className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
              activePage === 'dashboard'
                ? 'text-blue-600 bg-blue-50/80 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            Dashboard
          </button>

          <button
            onClick={() => setActivePage('runs')}
            className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
              activePage === 'runs'
                ? 'text-blue-600 bg-blue-50/80 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            Run History
          </button>

          <button
            onClick={() => setActivePage('about')}
            className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
              activePage === 'about'
                ? 'text-blue-600 bg-blue-50/80 font-semibold'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            Architecture
          </button>
        </nav>

        {/* Right Action & Engine Status */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-xs px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-600">
            <span className={`w-2 h-2 rounded-full ${
              serverStatus === 'online' ? 'bg-emerald-500' : serverStatus === 'checking' ? 'bg-amber-500 animate-pulse' : 'bg-rose-500'
            }`} />
            <span className="font-medium">
              {serverStatus === 'online' ? 'Engine Online' : serverStatus === 'checking' ? 'Connecting...' : 'Offline'}
            </span>
          </div>

          <button
            onClick={onNewGeneration}
            className="hidden sm:inline-flex items-center px-3.5 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-colors"
          >
            + New Generation
          </button>
        </div>

      </div>
    </header>
  );
}
