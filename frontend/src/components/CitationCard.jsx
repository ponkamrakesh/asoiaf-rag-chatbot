import React, { useState } from 'react';
import { BookOpen, Copy, Check, Bookmark } from 'lucide-react';

const BOOK_COLORS = {
  "A Game of Thrones": "border-blue-500/40 text-blue-400 bg-blue-950/20",
  "A Clash of Kings": "border-amber-500/40 text-amber-400 bg-amber-950/20",
  "A Storm of Swords": "border-red-500/40 text-red-400 bg-red-950/20",
  "A Feast for Crows": "border-purple-500/40 text-purple-400 bg-purple-950/20",
  "A Dance with Dragons": "border-emerald-500/40 text-emerald-400 bg-emerald-950/20",
};

export default function CitationCard({ citation, isHighlighted = false }) {
  const [copied, setCopied] = useState(false);

  const copyQuote = () => {
    navigator.clipboard.writeText(citation.quote);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const bookStyle = BOOK_COLORS[citation.book] || "border-westeros-gold/40 text-westeros-gold bg-westeros-900";
  const matchPercentage = Math.round((citation.score || 0) * 100);

  return (
    <div
      className={`rounded-xl border p-3.5 transition-all duration-200 text-left relative ${
        isHighlighted
          ? 'bg-westeros-850 border-westeros-gold ring-1 ring-westeros-gold shadow-lg shadow-westeros-gold/10'
          : 'bg-westeros-900/80 border-westeros-800 hover:border-westeros-700'
      }`}
    >
      {/* Top Bar: Citation ID, Book badge, Page, Match */}
      <div className="flex items-center justify-between gap-2 mb-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="w-5 h-5 rounded-full bg-westeros-gold text-westeros-950 font-bold text-xs flex items-center justify-center">
            {citation.id}
          </span>
          <span className={`text-[11px] font-medium px-2 py-0.5 rounded border ${bookStyle}`}>
            {citation.book}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {citation.score > 0 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-westeros-800 text-emerald-400 font-mono">
              {matchPercentage}% match
            </span>
          )}
          <button
            onClick={copyQuote}
            title="Copy Quote"
            className="text-gray-400 hover:text-gray-200 transition-colors p-1"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Chapter & Page Info */}
      <div className="flex items-center gap-2 text-xs text-gray-400 mb-2">
        <span className="font-semibold text-gray-300">
          Chapter: {citation.chapter}
        </span>
        <span>•</span>
        <span>PDF Page {citation.page}</span>
        {citation.source_type === 'appendix' && (
          <>
            <span>•</span>
            <span className="text-amber-400 text-[10px] uppercase font-bold">Appendix Lore</span>
          </>
        )}
      </div>

      {/* Quote Snippet */}
      <blockquote className="text-xs text-gray-300 italic border-l-2 border-westeros-gold/60 pl-2.5 py-0.5 font-serif leading-relaxed line-clamp-4 hover:line-clamp-none transition-all">
        "{citation.quote}"
      </blockquote>
    </div>
  );
}

