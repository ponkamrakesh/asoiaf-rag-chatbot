import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, User, Scroll, Sparkles, Feather, AlertCircle } from 'lucide-react';

const SUGGESTED_QUERIES = [
  "Who is Jon Snow and what is his origin?",
  "Who was truly responsible for the death of Jon Arryn?",
  "Why did Jaime push Bran from the broken tower?",
  "What happened at the Red Wedding and who betrayed Robb?",
];

export default function ChatWindow({
  messages,
  onSendMessage,
  isLoading,
  onCitationClick,
  latestMetrics
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickQuery = (text) => {
    if (isLoading) return;
    onSendMessage(text);
  };

  // Helper to render markdown while converting citation markers [1], [2] to clickable badges
  const renderMessageContent = (content) => {
    // Regex for citation markers like [1], [2], [1, 2]
    const parts = content.split(/(\[\d+\])/g);

    return (
      <div className="prose prose-invert prose-amber max-w-none text-sm leading-relaxed">
        {parts.map((part, index) => {
          const match = part.match(/^\[(\d+)\]$/);
          if (match) {
            const id = parseInt(match[1], 10);
            return (
              <button
                key={index}
                onClick={() => onCitationClick && onCitationClick(id)}
                className="inline-flex items-center justify-center px-1.5 py-0.2 mx-0.5 text-[11px] font-bold font-mono rounded bg-westeros-gold/20 text-westeros-gold hover:bg-westeros-gold hover:text-westeros-950 border border-westeros-gold/40 transition-all cursor-pointer shadow-sm align-super"
                title={`Jump to Citation [${id}]`}
              >
                [{id}]
              </button>
            );
          }
          return <ReactMarkdown key={index} components={{ p: ({ children }) => <span>{children}</span> }}>{part}</ReactMarkdown>;
        })}
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-westeros-950">
      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto py-12">
            <div className="w-16 h-16 rounded-2xl bg-westeros-900 border border-westeros-gold/30 flex items-center justify-center text-westeros-gold mb-4 shadow-xl shadow-westeros-gold/5">
              <Scroll className="w-8 h-8" />
            </div>
            <h2 className="font-cinzel text-xl font-bold text-amber-100 mb-2">
              The Citadel of Oldtown
            </h2>
            <p className="text-xs text-gray-400 mb-6 leading-relaxed">
              Consult the 5 canonical books of <em>A Song of Ice and Fire</em>.
              Every answer is verified against Pinecone vector embeddings and cited directly with chapter and page evidence.
            </p>

            {/* Quick Starters */}
            <div className="w-full space-y-2">
              <span className="text-[11px] font-semibold tracking-wider text-westeros-gold/80 uppercase">
                Inquire of the Archmaester:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                {SUGGESTED_QUERIES.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleQuickQuery(q)}
                    className="p-2.5 rounded-xl bg-westeros-900/80 border border-westeros-800 hover:border-westeros-gold/50 text-xs text-gray-300 hover:text-amber-200 transition-all text-left flex items-start gap-2 shadow-sm"
                  >
                    <Feather className="w-3.5 h-3.5 text-westeros-gold mt-0.5 shrink-0" />
                    <span>{q}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-3xl ${
                m.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 text-xs font-bold ${
                  m.role === 'user'
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20'
                    : 'bg-westeros-gold text-westeros-950 border border-westeros-goldLight shadow-md shadow-westeros-gold/20'
                }`}
              >
                {m.role === 'user' ? <User className="w-4 h-4" /> : <Scroll className="w-4 h-4" />}
              </div>

              {/* Message Bubble */}
              <div
                className={`rounded-2xl p-4 transition-all ${
                  m.role === 'user'
                    ? 'bg-blue-600/90 text-white rounded-tr-none'
                    : 'bg-westeros-900/90 border border-westeros-800 text-gray-200 rounded-tl-none shadow-lg'
                }`}
              >
                {m.role === 'user' ? (
                  <p className="text-sm">{m.content}</p>
                ) : (
                  renderMessageContent(m.content)
                )}

                {/* Sub-bar for Assistant messages */}
                {m.role === 'assistant' && m.metrics && (
                  <div className="mt-3 pt-2.5 border-t border-westeros-800/80 flex items-center justify-between text-[11px] text-gray-400">
                    <span className="flex items-center gap-1.5 font-mono">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                      {m.metrics.knowledge_mode || 'Grounded RAG'}
                    </span>
                    <span className="font-mono text-gray-500">
                      {m.metrics.latency?.total_latency_ms ? `${Math.round(m.metrics.latency.total_latency_ms)}ms` : ''}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 max-w-xl mr-auto">
            <div className="w-8 h-8 rounded-lg bg-westeros-gold text-westeros-950 flex items-center justify-center shrink-0">
              <Scroll className="w-4 h-4 animate-pulse" />
            </div>
            <div className="bg-westeros-900/90 border border-westeros-800 rounded-2xl rounded-tl-none p-4 text-gray-400 text-xs flex items-center gap-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-westeros-gold rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-2 h-2 bg-westeros-gold rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-2 h-2 bg-westeros-gold rounded-full animate-bounce"></div>
              </div>
              <span className="font-cinzel text-amber-200">
                Consulting Citadel Scrolls & Pinecone Vectors...
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Query Input Bar */}
      <div className="p-4 border-t border-westeros-800 bg-westeros-900/80 backdrop-blur-md">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Inquire of the Citadel (e.g. 'Who is Jon Snow?', 'Who poisoned Jon Arryn?')..."
            disabled={isLoading}
            className="w-full pl-4 pr-12 py-3 bg-westeros-950 border border-westeros-800 focus:border-westeros-gold focus:ring-1 focus:ring-westeros-gold rounded-xl text-sm text-gray-100 placeholder-gray-500 outline-none transition-all shadow-inner"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 p-2 rounded-lg bg-westeros-gold text-westeros-950 hover:bg-westeros-goldLight disabled:opacity-40 disabled:cursor-not-allowed transition-all shadow-md shadow-westeros-gold/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
        <p className="text-[10px] text-center text-gray-500 mt-2">
          Strict George R. R. Martin Book Canon • 100% Free Hosting Stack (Groq + Pinecone + Vercel + Render)
        </p>
      </div>
    </div>
  );
}

