import React from 'react';
import { Scroll, BarChart3, MessageSquare, ShieldCheck, Sparkles } from 'lucide-react';

export default function Header({ activeTab, setActiveTab, latestMetrics }) {
  return (
    <header className="border-b border-westeros-800 bg-westeros-900/90 backdrop-blur-md sticky top-0 z-50 px-4 lg:px-8 py-3 flex items-center justify-between">
      {/* Brand & Crest */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-600/20 to-westeros-gold/30 border border-westeros-gold/40 flex items-center justify-center text-westeros-gold shadow-lg shadow-westeros-gold/5">
          <Scroll className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h1 className="font-cinzel text-lg font-bold tracking-wider text-amber-100 flex items-center gap-2">
              CITADEL ARCHIVES
              <span className="text-[10px] tracking-normal font-sans px-2 py-0.5 rounded-full bg-westeros-gold/20 text-westeros-goldLight border border-westeros-gold/30">
                ASOIAF RAG
              </span>
            </h1>
          </div>
          <p className="text-xs text-gray-400">
            5 Books • 4,068 Pages • Pinecone Vector DB • Groq Llama 3.3
          </p>
        </div>
      </div>

      {/* View Switcher: Chat vs Metrics */}
      <div className="flex items-center bg-westeros-850 p-1 rounded-xl border border-westeros-800 shadow-inner">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'chat'
              ? 'bg-westeros-gold text-westeros-950 font-semibold shadow-md shadow-westeros-gold/20'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>Chat & Citations</span>
        </button>

        <button
          onClick={() => setActiveTab('metrics')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all ${
            activeTab === 'metrics'
              ? 'bg-westeros-gold text-westeros-950 font-semibold shadow-md shadow-westeros-gold/20'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          <BarChart3 className="w-4 h-4" />
          <span>Metrics Dashboard</span>
          {latestMetrics && (
            <span className="ml-1 text-[10px] px-1.5 py-0.2 rounded bg-westeros-950/40 text-amber-200">
              {latestMetrics.latency?.total_latency_ms ? `${Math.round(latestMetrics.latency.total_latency_ms)}ms` : 'Ready'}
            </span>
          )}
        </button>
      </div>

      {/* Engine Status */}
      <div className="hidden md:flex items-center gap-3">
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 text-xs">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Citadel Online (Free Tier)</span>
        </div>
      </div>
    </header>
  );
}

