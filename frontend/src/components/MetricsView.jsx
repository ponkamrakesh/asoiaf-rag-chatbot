import React, { useState } from 'react';
import {
  Clock,
  Zap,
  Cpu,
  Layers,
  Database,
  CheckCircle2,
  AlertTriangle,
  Code2,
  ChevronDown,
  ChevronUp,
  Coins,
  ShieldCheck,
  SpellCheck,
  Compass,
  Sparkles,
  ArrowRightLeft,
  Tv,
  Globe2,
  BookMarked
} from 'lucide-react';

export default function MetricsView({ metrics, citations = [] }) {
  const [showRawContext, setShowRawContext] = useState(false);
  const [showTransformation, setShowTransformation] = useState(true);

  if (!metrics) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-westeros-950">
        <div className="w-16 h-16 rounded-2xl bg-westeros-900 border border-westeros-800 flex items-center justify-center text-gray-500 mb-4">
          <Layers className="w-8 h-8" />
        </div>
        <h3 className="font-cinzel text-lg font-bold text-gray-200 mb-2">
          No Archival Metrics Yet
        </h3>
        <p className="text-xs text-gray-400 max-w-md">
          Execute an inquiry in the Chat window to view real-time latency breakdowns, high Top-K candidate pooling, re-ranking scores, and evaluation diagnostics.
        </p>
      </div>
    );
  }

  const {
    domain = 'book_canon',
    knowledge_mode = 'Grounded RAG',
    knowledge_ratio = { rag_vectors: 70, llm_parametric: 30 },
    faithfulness_score = 96.0,
    context_relevance_score = 0.0,
    latency = {},
    prompt_tokens = 0,
    completion_tokens = 0,
    total_tokens = 0,
    tokens_per_second = 0.0,
    model = 'llama-3.3-70b-versatile',
    candidate_pool_size = 0,
    reranked_pool_size = 0,
    reordering_strategy = 'Lost-in-the-Middle',
    transformation = null
  } = metrics;

  const totalMs = latency.total_latency_ms || 1;
  const routingPct = Math.round(((latency.spelling_and_routing_ms || 0) / totalMs) * 100);
  const embeddingPct = Math.round(((latency.embedding_ms || 0) / totalMs) * 100);
  const pineconePct = Math.round(((latency.pinecone_search_ms || 0) / totalMs) * 100);
  const rerankPct = Math.round(((latency.reranking_ms || 0) / totalMs) * 100);
  const groqPct = Math.round(((latency.groq_llm_ms || 0) / totalMs) * 100);

  const getDomainBadge = () => {
    switch (domain) {
      case 'series_lore':
        return { label: 'TV & Screen Chronicles', icon: Tv, style: 'bg-purple-950/60 text-purple-300 border-purple-500/30' };
      case 'out_of_universe':
        return { label: 'Universal Science & Philosophy', icon: Globe2, style: 'bg-blue-950/60 text-blue-300 border-blue-500/30' };
      case 'casual_chat':
        return { label: 'Conversational Dialogue', icon: Sparkles, style: 'bg-emerald-950/60 text-emerald-300 border-emerald-500/30' };
      default:
        return { label: 'Book Canon Lore', icon: BookMarked, style: 'bg-amber-950/60 text-amber-300 border-amber-500/30' };
    }
  };

  const domainBadge = getDomainBadge();
  const DomainIcon = domainBadge.icon;

  return (
    <div className="flex-1 overflow-y-auto p-4 lg:p-8 bg-westeros-950 space-y-6">
      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="p-3.5 rounded-2xl bg-westeros-900 border border-westeros-800 shadow-md">
          <span className="text-[10px] text-gray-400 font-mono uppercase block">Total Latency</span>
          <span className="text-lg font-bold font-mono text-amber-200 mt-1 block">
            {Math.round(totalMs)} ms
          </span>
          <span className="text-[10px] text-gray-500">End-to-end</span>
        </div>

        <div className="p-3.5 rounded-2xl bg-westeros-900 border border-westeros-800 shadow-md">
          <span className="text-[10px] text-gray-400 font-mono uppercase block">Gen Speed</span>
          <span className="text-lg font-bold font-mono text-emerald-400 mt-1 block">
            {tokens_per_second > 0 ? `${tokens_per_second} tps` : 'Instant'}
          </span>
          <span className="text-[10px] text-gray-500">Groq LPU Engine</span>
        </div>

        <div className="p-3.5 rounded-2xl bg-westeros-900 border border-westeros-800 shadow-md">
          <span className="text-[10px] text-gray-400 font-mono uppercase block">Top Re-Rank Score</span>
          <span className="text-lg font-bold font-mono text-blue-400 mt-1 block">
            {context_relevance_score > 0 ? `${context_relevance_score}%` : 'N/A'}
          </span>
          <span className="text-[10px] text-gray-500">Cross-Scored</span>
        </div>

        <div className="p-3.5 rounded-2xl bg-westeros-900 border border-westeros-800 shadow-md">
          <span className="text-[10px] text-gray-400 font-mono uppercase block">Canon Faithfulness</span>
          <span className="text-lg font-bold font-mono text-emerald-300 mt-1 block">
            {faithfulness_score}%
          </span>
          <span className="text-[10px] text-gray-500">Verified Citation</span>
        </div>

        <div className="p-3.5 rounded-2xl bg-westeros-900 border border-westeros-800 shadow-md">
          <span className="text-[10px] text-gray-400 font-mono uppercase block">Candidates Filtered</span>
          <span className="text-lg font-bold font-mono text-westeros-gold mt-1 block">
            {candidate_pool_size} → {reranked_pool_size}
          </span>
          <span className="text-[10px] text-gray-500">High Top-K Refined</span>
        </div>

        <div className="p-3.5 rounded-2xl bg-westeros-900 border border-westeros-800 shadow-md">
          <span className="text-[10px] text-gray-400 font-mono uppercase block">Compute Cost</span>
          <span className="text-lg font-bold font-mono text-emerald-400 mt-1 block flex items-center gap-1">
            <Coins className="w-4 h-4" /> $0.00
          </span>
          <span className="text-[10px] text-gray-500">100% Free Tier</span>
        </div>
      </div>

      {/* Hero Banner: Knowledge Synthesis Mode & Domain */}
      <div className="rounded-2xl bg-gradient-to-r from-westeros-900 via-westeros-850 to-westeros-900 border border-westeros-800 p-5 shadow-xl">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className={`flex items-center gap-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full border ${domainBadge.style}`}>
                <DomainIcon className="w-3.5 h-3.5" />
                {domainBadge.label}
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-westeros-gold"></span>
              <span className="text-xs text-gray-400 font-mono">Re-Ordering: {reordering_strategy}</span>
            </div>
            <h2 className="text-xl font-bold font-cinzel text-amber-100 flex items-center gap-2">
              {knowledge_mode}
              {knowledge_mode.includes('Grounded') && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
              {knowledge_mode.includes('Comparative') && <ArrowRightLeft className="w-5 h-5 text-purple-400" />}
              {knowledge_mode.includes('Macro') && <Compass className="w-5 h-5 text-blue-400" />}
            </h2>
          </div>

          <div className="text-right">
            <span className="text-xs text-gray-400 font-mono block">Inference Engine</span>
            <span className="text-sm font-semibold text-gray-200">{model}</span>
          </div>
        </div>

        {/* Knowledge Source Attribution Split */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span className="flex items-center gap-1.5 text-emerald-400 font-medium">
              <Database className="w-3.5 h-3.5" />
              Retrieved Scrolls Evidence: {knowledge_ratio.rag_vectors}%
            </span>
            <span className="flex items-center gap-1.5 text-westeros-gold font-medium">
              <Cpu className="w-3.5 h-3.5" />
              Grand Maester Archival Memory: {knowledge_ratio.llm_parametric}%
            </span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-westeros-950 overflow-hidden flex border border-westeros-800">
            <div
              style={{ width: `${knowledge_ratio.rag_vectors}%` }}
              className="bg-emerald-500 transition-all duration-500"
              title={`Pinecone Vectors: ${knowledge_ratio.rag_vectors}%`}
            />
            <div
              style={{ width: `${knowledge_ratio.llm_parametric}%` }}
              className="bg-westeros-gold transition-all duration-500"
              title={`LLM Archival Memory: ${knowledge_ratio.llm_parametric}%`}
            />
          </div>
        </div>
      </div>

      {/* Two-Stage Retrieval & Lost-in-the-Middle Re-Ordering Card */}
      <div className="rounded-2xl bg-westeros-900 border border-westeros-800 p-5 shadow-lg">
        <h3 className="font-cinzel text-sm font-bold text-amber-200 mb-3 flex items-center gap-2">
          <ArrowRightLeft className="w-4 h-4 text-westeros-gold" />
          TWO-STAGE RE-RANKING & ATTENTION RE-ORDERING PIPELINE
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800">
            <span className="text-gray-400 font-semibold block mb-1">Stage 1: Broad Pooling</span>
            <p className="text-gray-300">
              Retrieved <strong>{candidate_pool_size} candidate scrolls</strong> from Pinecone serverless vector index using dense cosine matching.
            </p>
          </div>
          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800">
            <span className="text-gray-400 font-semibold block mb-1">Stage 2: Cross Re-Ranking ({latency.reranking_ms || 0}ms)</span>
            <p className="text-gray-300">
              Scored candidate pool with composite lexical overlap, character entity alignment, and chapter bonuses to extract the top <strong>{reranked_pool_size} elite scrolls</strong>.
            </p>
          </div>
          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800">
            <span className="text-gray-400 font-semibold block mb-1">Stage 3: Attention Optimization</span>
            <p className="text-gray-300">
              Re-arranged using <strong>Lost-in-the-Middle</strong> ordering: top evidence placed at start and end of prompt to counter cognitive attention sag.
            </p>
          </div>
        </div>
      </div>

      {/* Latency Waterfall Breakdown */}
      <div className="rounded-2xl bg-westeros-900 border border-westeros-800 p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-cinzel text-sm font-bold text-amber-200 flex items-center gap-2">
            <Clock className="w-4 h-4 text-westeros-gold" />
            5-STAGE LATENCY WATERFALL BREAKDOWN
          </h3>
          <span className="text-xs font-mono font-bold px-2.5 py-1 rounded-lg bg-westeros-950 border border-westeros-800 text-gray-200">
            Total: {Math.round(totalMs)} ms
          </span>
        </div>

        {/* Multi-segment Progress Bar */}
        <div className="w-full h-3 rounded-full bg-westeros-950 overflow-hidden flex mb-4 border border-westeros-800">
          <div style={{ width: `${routingPct}%` }} className="bg-purple-500 transition-all" title={`Routing: ${latency.spelling_and_routing_ms}ms`} />
          <div style={{ width: `${embeddingPct}%` }} className="bg-blue-500 transition-all" title={`FastEmbed: ${latency.embedding_ms}ms`} />
          <div style={{ width: `${pineconePct}%` }} className="bg-emerald-500 transition-all" title={`Pinecone Search: ${latency.pinecone_search_ms}ms`} />
          <div style={{ width: `${rerankPct}%` }} className="bg-cyan-500 transition-all" title={`Re-Ranking: ${latency.reranking_ms}ms`} />
          <div style={{ width: `${groqPct}%` }} className="bg-westeros-gold transition-all" title={`Groq LLM: ${latency.groq_llm_ms}ms`} />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
            <span className="text-[10px] font-mono text-purple-400 block mb-0.5">1. Preprocessing</span>
            <span className="text-sm font-mono font-bold text-gray-200">{latency.spelling_and_routing_ms || 0} ms</span>
            <span className="text-[10px] text-gray-500 block mt-0.5">Spelling & Aliases</span>
          </div>

          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
            <span className="text-[10px] font-mono text-blue-400 block mb-0.5">2. Query Embedding</span>
            <span className="text-sm font-mono font-bold text-gray-200">{latency.embedding_ms || 0} ms</span>
            <span className="text-[10px] text-gray-500 block mt-0.5">FastEmbed (BGE-small)</span>
          </div>

          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
            <span className="text-[10px] font-mono text-emerald-400 block mb-0.5">3. Vector Search</span>
            <span className="text-sm font-mono font-bold text-gray-200">{latency.pinecone_search_ms || 0} ms</span>
            <span className="text-[10px] text-gray-500 block mt-0.5">15 Candidate Chunks</span>
          </div>

          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
            <span className="text-[10px] font-mono text-cyan-400 block mb-0.5">4. Re-Ranking</span>
            <span className="text-sm font-mono font-bold text-gray-200">{latency.reranking_ms || 0} ms</span>
            <span className="text-[10px] text-gray-500 block mt-0.5">Cross-Scoring Top 6</span>
          </div>

          <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80 col-span-2 md:col-span-1">
            <span className="text-[10px] font-mono text-westeros-gold block mb-0.5">5. Groq Generation</span>
            <span className="text-sm font-mono font-bold text-gray-200">{latency.groq_llm_ms || 0} ms</span>
            <span className="text-[10px] text-gray-500 block mt-0.5">{model}</span>
          </div>
        </div>
      </div>

      {/* Re-Ranked Scrolls Spectrum vs Raw Vector Scores */}
      {citations.length > 0 && (
        <div className="rounded-2xl bg-westeros-900 border border-westeros-800 p-5 shadow-lg">
          <h3 className="font-cinzel text-sm font-bold text-amber-200 mb-3 flex items-center gap-2">
            <Database className="w-4 h-4 text-westeros-gold" />
            FINAL ELITE SCROLLS (RE-RANKED COMPOSITE VS RAW VECTOR MATCH)
          </h3>

          <div className="space-y-3">
            {citations.map((c) => {
              const compositePct = Math.round((c.score || 0) * 100);
              const rawPct = Math.round((c.raw_vector_score || 0) * 100);
              return (
                <div key={c.id} className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
                  <div className="flex items-center justify-between text-xs mb-2">
                    <span className="font-semibold text-gray-200">
                      Scroll [{c.id}]: {c.book} ({c.chapter}) • Page {c.page}
                    </span>
                    <div className="flex items-center gap-3">
                      <span className="text-gray-400 font-mono text-[11px]">
                        Raw Vector: {rawPct}%
                      </span>
                      <span className="font-mono text-emerald-400 font-bold text-xs bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-500/30">
                        Composite: {compositePct}%
                      </span>
                    </div>
                  </div>
                  <blockquote className="text-xs text-gray-400 italic line-clamp-2">
                    "{c.quote}"
                  </blockquote>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Query Transformation & Spell Checker Inspector */}
      {transformation && (
        <div className="rounded-2xl bg-westeros-900 border border-westeros-800 p-5 shadow-lg">
          <button
            onClick={() => setShowTransformation(!showTransformation)}
            className="w-full flex items-center justify-between font-cinzel text-xs font-bold text-gray-300 hover:text-amber-200 transition-colors"
          >
            <span className="flex items-center gap-2">
              <SpellCheck className="w-4 h-4 text-westeros-gold" />
              QUERY REFORMULATION & SPELLING CORRECTION
              {(transformation.spelling_corrections.length > 0 || transformation.alias_expansions.length > 0) && (
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-500/30">
                  Enhanced
                </span>
              )}
            </span>
            {showTransformation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>

          {showTransformation && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 text-xs font-mono">
              <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
                <span className="text-[10px] text-gray-500 uppercase block mb-1">Raw User Query</span>
                <p className="text-gray-300">"{transformation.original_query}"</p>
              </div>

              <div className="p-3 rounded-xl bg-westeros-950 border border-westeros-800/80">
                <span className="text-[10px] text-emerald-400 uppercase block mb-1">Enriched Search Query</span>
                <p className="text-amber-200">"{transformation.enriched_query}"</p>
              </div>

              {transformation.spelling_corrections.length > 0 && (
                <div className="col-span-1 md:col-span-2 p-2.5 rounded-lg bg-blue-950/20 border border-blue-500/20 text-blue-300 flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
                  <span>Phonetic Corrections: {transformation.spelling_corrections.join(', ')}</span>
                </div>
              )}

              {transformation.alias_expansions.length > 0 && (
                <div className="col-span-1 md:col-span-2 p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/20 text-amber-300 flex items-center gap-2">
                  <Sparkles className="w-3.5 h-3.5 shrink-0" />
                  <span>Westeros Alias Mappings: {transformation.alias_expansions.join(', ')}</span>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
