import React, { useState } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import CitationsPanel from './components/CitationsPanel';
import MetricsView from './components/MetricsView';

const INITIAL_GREETING = {
  role: 'assistant',
  content: `Greetings, traveler. I am an Archmaester of the Citadel in Oldtown. 

The scrolls, ledgers, and chronicles of the Seven Kingdoms—spanning all five books of *A Song of Ice and Fire*—are open before us. 

Whether you inquire of the ancient Valyrians, the true lineage of Jon Snow, the tragedy of the Red Wedding, or the whispers of Littlefinger, speak your query. Every claim I make shall be grounded in the sacred pages of George R. R. Martin's books.`,
  metrics: null,
};

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' or 'metrics'
  const [messages, setMessages] = useState([INITIAL_GREETING]);
  const [isLoading, setIsLoading] = useState(false);
  const [latestCitations, setLatestCitations] = useState([]);
  const [latestMetrics, setLatestMetrics] = useState(null);
  const [highlightedCitationId, setHighlightedCitationId] = useState(null);

  const handleSendMessage = async (userText) => {
    const userMsg = { role: 'user', content: userText };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setHighlightedCitationId(null);

    try {
      // Build conversation history excluding initial greeting
      const history = messages
        .filter((_, idx) => idx > 0)
        .map((m) => ({ role: m.role, content: m.content }));

      const apiUrl = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api/chat` 
        : '/api/chat';

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          conversation_history: history,
          top_k: 6,
        }),
      });

      if (!response.ok) {
        throw new Error(`Archival server responded with status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMsg = {
        role: 'assistant',
        content: data.answer,
        metrics: data.metrics,
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setLatestCitations(data.citations || []);
      setLatestMetrics(data.metrics || null);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMsg = {
        role: 'assistant',
        content: `**A Raven was lost in flight.** Unable to reach the Citadel archives (${err.message}). If you are running locally, ensure the FastAPI backend is running at \`http://localhost:8000\`.`,
        metrics: null,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCitationClick = (citationId) => {
    setHighlightedCitationId(citationId);
    // If on mobile or metrics view, could also switch or scroll
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-westeros-950 text-gray-100 font-sans">
      {/* Universal Top Header with Chat <-> Metrics Switch */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        latestMetrics={latestMetrics}
      />

      {/* Main View Area */}
      <main className="flex-1 flex overflow-hidden relative">
        {activeTab === 'chat' ? (
          <div className="flex-1 flex flex-col lg:flex-row h-full overflow-hidden">
            {/* Left: Chat Window */}
            <ChatWindow
              messages={messages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              onCitationClick={handleCitationClick}
              latestMetrics={latestMetrics}
            />

            {/* Right: Dynamic Citations Drawer */}
            <CitationsPanel
              citations={latestCitations}
              highlightedId={highlightedCitationId}
            />
          </div>
        ) : (
          /* Metrics Dashboard View */
          <MetricsView
            metrics={latestMetrics}
            citations={latestCitations}
          />
        )}
      </main>
    </div>
  );
}

