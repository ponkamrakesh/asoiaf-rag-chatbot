import React from 'react';
import { BookOpen, Layers, Sparkles } from 'lucide-react';
import CitationCard from './CitationCard';

export default function CitationsPanel({ citations = [], highlightedId = null }) {
  if (!citations || citations.length === 0) {
    return (
      <aside className="w-full lg:w-80 border-l border-westeros-800 bg-westeros-900/40 p-4 flex flex-col items-center justify-center text-center">
        <div className="w-12 h-12 rounded-xl bg-westeros-850 border border-westeros-800 flex items-center justify-center text-gray-500 mb-3">
          <BookOpen className="w-6 h-6" />
        </div>
        <h4 className="font-cinzel text-sm text-gray-300 font-bold mb-1">
          Archival Citations
        </h4>
        <p className="text-xs text-gray-500 max-w-[220px]">
          Enter an inquiry into the chronicles to summon exact book passages and page references.
        </p>
      </aside>
    );
  }

  return (
    <aside className="w-full lg:w-96 border-t lg:border-t-0 lg:border-l border-westeros-800 bg-westeros-900/60 flex flex-col h-full overflow-hidden">
      {/* Panel Header */}
      <div className="p-3.5 border-b border-westeros-800 bg-westeros-850/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-westeros-gold" />
          <h3 className="font-cinzel text-xs font-bold tracking-wider text-amber-200">
            CITADEL SCROLLS CITED ({citations.length})
          </h3>
        </div>
        <span className="text-[10px] text-emerald-400 font-mono bg-emerald-950/40 px-2 py-0.5 rounded border border-emerald-500/20">
          Verified Book Canon
        </span>
      </div>

      {/* Citations List */}
      <div className="p-3 space-y-3 overflow-y-auto flex-1">
        {citations.map((c) => (
          <CitationCard
            key={c.id}
            citation={c}
            isHighlighted={highlightedId === c.id}
          />
        ))}
      </div>
    </aside>
  );
}

