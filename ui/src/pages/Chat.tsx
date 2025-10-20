import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import { http, toMessage } from "../lib/http";
import ErrorBanner from "../components/ErrorBanner";
import DemoCards from "../components/DemoCards";
import "../styles/markdown.css";

type AskResponse = {
  question: string;
  answer: string;
  references?: Array<{
    id: string;
    title: string;
    url?: string;
    source?: string;
    stage?: string;
    tags?: string;
    similarity: number;
  }>;
};

type ChatTurn =
  | { role: "user"; content: string; ts: number }
  | { role: "assistant"; content: string; refs?: AskResponse["references"]; ts: number }
  | { role: "system"; content: string; ts: number };

const STORAGE_KEY = "startupscout:chat:v1";

export default function Chat() {
  const [input, setInput] = useState("");
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [showDemoCards, setShowDemoCards] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Load history once
  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    let hasHistory = false;
    
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as ChatTurn[];
        if (Array.isArray(parsed) && parsed.length > 1) { // More than just system message
          setTurns(parsed);
          hasHistory = true;
        }
      } catch {
        /* ignore */
      }
    }
    
    if (!hasHistory) {
      // default system message
      setTurns([
        {
          role: "system",
          content:
            "Ask anything about growth, pricing, fundraising, or product decisions. I'll pull from real startup cases.",
          ts: Date.now(),
        },
      ]);
      // Show demo cards for fresh chat
      setShowDemoCards(true);
    }
  }, []);

  // Persist on every change
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(turns));
  }, [turns]);

  // Auto-scroll on update
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [turns, loading]);

  const handleDemoQuestion = (question: string) => {
    console.log('handleDemoQuestion called with:', question);
    setInput(question);
    setShowDemoCards(false);
  };

  async function send() {
    const q = input.trim();
    if (!q || loading) return;
    setErr("");
    setInput("");
    setShowDemoCards(false);

    setTurns((t) => [...t, { role: "user", content: q, ts: Date.now() }]);
    setLoading(true);

    try {
      const res = await http.get<AskResponse>("/ask", { params: { question: q } });
      setTurns((t) => [
        ...t,
        {
          role: "assistant",
          content: res.data.answer || "No answer.",
          refs: res.data.references,
          ts: Date.now(),
        },
      ]);
    } catch (e) {
      setErr(toMessage(e));
      setTurns((t) => [
        ...t,
        { role: "assistant", content: "Sorry—request failed. Try again.", ts: Date.now() },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  function clearHistory() {
    setTurns([
      {
        role: "system",
        content:
          "History cleared. Ask anything about growth, pricing, fundraising, or product decisions.",
        ts: Date.now(),
      },
    ]);
    setErr("");
    setShowDemoCards(true); // Show demo cards after clearing history
  }

  function showDemoCards() {
    console.log('showDemoCards called');
    setShowDemoCards(true);
  }

  return (
    <section className="flex flex-col h-[calc(100vh-6rem)] bg-white">
      <div className="mb-4 flex items-center justify-between border-b pb-3">
        <h1 className="text-2xl font-bold text-gray-900">StartupScout Chat</h1>
        <div className="flex gap-2">
          <button
            onClick={showDemoCards}
            className="text-sm px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            disabled={loading}
          >
            Demo Questions
          </button>
          <button
            onClick={clearHistory}
            className="text-sm px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            disabled={loading}
          >
            Clear History
          </button>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto bg-gray-50 border border-gray-200 rounded-lg p-6 space-y-6"
      >
        {turns.map((t, idx) => (
          <MessageBubble
            key={idx}
            role={t.role}
            content={t.content}
            refs={("refs" in t && t.refs) || undefined}
          />
        ))}
        {loading && <TypingBubble />}
      </div>

      <div className="mt-4">
        <ErrorBanner message={err} />
      </div>

      <div className="mt-4 flex gap-3">
        <textarea
          className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          placeholder="Ask StartupScout about pricing, growth, fundraising, or product decisions..."
          value={input}
          rows={2}
          onChange={(e) => {
            setInput(e.target.value);
            if (err) setErr("");
          }}
          onKeyDown={onKeyDown}
        />
        <button
          className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-6 py-3 rounded-lg disabled:opacity-50 transition-colors font-medium"
          onClick={send}
          disabled={loading || !input.trim()}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
    </section>
  );
}

function MessageBubble({
  role,
  content,
  refs,
}: {
  role: "user" | "assistant" | "system";
  content: string;
  refs?: AskResponse["references"];
}) {
  const isUser = role === "user";
  const isSystem = role === "system";
  const wrap = isSystem ? "justify-center" : isUser ? "justify-end" : "justify-start";
  
  const bubbleClasses = isSystem
    ? "bg-blue-50 text-blue-800 border border-blue-200"
    : isUser
    ? "bg-blue-600 text-white"
    : "bg-white text-gray-900 border border-gray-200 shadow-sm";

  return (
    <div className={`w-full flex ${wrap}`}>
      <div className={`max-w-[85%] rounded-2xl px-5 py-4 text-sm ${bubbleClasses}`}>
        <div className="markdown prose prose-sm max-w-none">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              a: (props) => (
                <a 
                  {...props} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline"
                />
              ),
              code: ({ inline, className, children, ...rest }: any) => (
                <code 
                  className={`${inline ? "bg-gray-100 px-1 py-0.5 rounded text-xs" : "block bg-gray-900 text-gray-100 p-3 rounded-lg overflow-x-auto"} ${className || ""}`} 
                  {...rest}
                >
                  {children}
                </code>
              ),
              ul: (props) => <ul className="list-disc list-inside space-y-1 my-2" {...props} />,
              ol: (props) => <ol className="list-decimal list-inside space-y-1 my-2" {...props} />,
              li: (props) => <li className="leading-relaxed" {...props} />,
              p: (props) => <p className="leading-relaxed mb-2" {...props} />,
            }}
          >
            {content || ""}
          </ReactMarkdown>
        </div>

        {/* Enhanced References section */}
        {role !== "user" && refs && refs.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-xs font-semibold text-gray-600 mb-3 uppercase tracking-wide">
              Sources ({refs.length})
            </div>
            <div className="space-y-2">
              {refs.map((ref, i) => (
                <div key={i} className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 text-sm mb-1">
                        {ref.title}
                      </div>
                      {ref.source && (
                        <div className="text-xs text-gray-500 mb-1">
                          Source: {ref.source}
                          {ref.stage && ` • Stage: ${ref.stage}`}
                        </div>
                      )}
                      {ref.url && (
                        <a 
                          href={ref.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:text-blue-800 underline"
                        >
                          View Source
                        </a>
                      )}
                    </div>
                    <div className="ml-3 text-xs text-gray-400 bg-gray-200 px-2 py-1 rounded">
                      {ref.similarity.toFixed(2)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <DemoCards 
        onQuestionClick={handleDemoQuestion}
        isVisible={showDemoCards}
      />
      {console.log('Chat render - showDemoCards:', showDemoCards)}
    </div>
  );
}

function TypingBubble() {
  return (
    <div className="w-full flex justify-start">
      <div className="bg-white border border-gray-200 rounded-2xl px-5 py-4 text-sm text-gray-600 shadow-sm">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
          </div>
          <span>StartupScout is thinking...</span>
        </div>
      </div>
    </div>
  );
}
