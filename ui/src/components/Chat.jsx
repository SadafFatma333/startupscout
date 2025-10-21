import React, { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { clsx } from "clsx";
import AnswerPanel from "./AnswerPanel";
import SkeletonAnswer from "./SkeletonAnswer";

const LOCAL_KEY = "scout:history";
const MAX_TURNS = 100;

function loadLocalHistory() {
  try {
    const raw = localStorage.getItem(LOCAL_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}
function saveLocalHistory(turns) {
  try {
    localStorage.setItem(LOCAL_KEY, JSON.stringify(turns.slice(-MAX_TURNS)));
  } catch {}
}

export default function Chat() {
  const [turns, setTurns] = useState(() => loadLocalHistory());
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollerRef = useRef(null);

  // Lightweight demo questions (non-intrusive chips)
  const demoQs = [
    { icon: "🚀", text: "What helped teams get their first 100 active users?" },
    { icon: "💸", text: "How do early startups choose their first price?" },
    { icon: "✍️", text: "What convinced investors to write the first check (pre-seed/seed)?" },
    { icon: "🧭", text: "What small onboarding change improved sign-ups?" },
    { icon: "📣", text: "How did founders get their first press or community attention?" },
    { icon: "⭐", text: "What features did early users care about most?" },
  ];

  // Hydrate from server history (best-effort)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.getHistory?.().catch(() => null);
        if (cancelled || !data?.turns) return;
        if (Array.isArray(data.turns) && data.turns.length > 0) {
          setTurns(data.turns.slice(-MAX_TURNS));
        }
      } catch {}
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Persist to localStorage
  useEffect(() => saveLocalHistory(turns), [turns]);

  // Auto-scroll to bottom
  useEffect(() => {
    const el = scrollerRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [turns, busy]);

  async function onSend(e) {
    e?.preventDefault?.();
    setError("");
    const q = input.trim();
    if (!q) return;

    // Optimistic user message
    const optimistic = { role: "user", content: q, ts: Date.now() };
    setTurns((prev) => [...prev, optimistic]);
    setInput("");
    setBusy(true);

    try {
      const res = await api.ask(q); // api.ask returns normalized {question, answer, references}
      const ans = res?.answer || "No answer.";
      const refs = Array.isArray(res?.references) ? res.references : [];

      setTurns((prev) => [
        ...prev,
        {
          role: "assistant",
          content: ans,
          refs,
          ts: Date.now(),
        },
      ]);
    } catch (ex) {
      const msg = ex?.message || "Network error";
      setError(msg);
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: "❌ " + msg, ts: Date.now() },
      ]);
    } finally {
      setBusy(false);
    }
  }

  function onClear() {
    setTurns([]);
    localStorage.removeItem(LOCAL_KEY);
    api.clearHistory?.().catch(() => {});
  }

  function onQuickAsk(q) {
    if (busy) return;
    setInput(q);
    // send immediately for a smooth demo experience
    setTimeout(() => onSend(), 0);
  }

  const canSend = useMemo(() => input.trim().length > 0 && !busy, [input, busy]);

  return (
    <div className="chatWrap">
      <header className="topbar">
        <div className="brand">StartupScout</div>
        <div className="actions">
          <button className="btn ghost" onClick={onClear} disabled={busy}>
            Clear
          </button>
        </div>
      </header>

      {error ? <div className="error">{error}</div> : null}

      <div className="chatScroll" ref={scrollerRef}>
        {turns.map((t, idx) => {
          if (t.role === "assistant") {
            return (
              <div key={t?.ts ?? idx} className="bubbleRow bot">
                <AnswerPanel content={t.content} references={t.refs || t.references || []} answerId={`answer-${t?.ts ?? idx}`} />
              </div>
            );
          }
          // keep existing user bubble:
          return <Message key={t?.ts ?? idx} role={t.role} content={t.content} refs={t.refs} />;
        })}
        {busy ? (
          <div className="bubbleRow bot">
            <SkeletonAnswer />
          </div>
        ) : null}
      </div>

      <form className="composer" onSubmit={onSend}>
        <input
          className="askInput"
          placeholder="Ask about growth, pricing, fundraising, product…"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            if (error) setError("");
          }}
          disabled={busy}
        />
        <button className="btn" disabled={!canSend}>
          {busy ? "…" : "Ask"}
        </button>
      </form>

      {/* Suggested prompts */}
      <div className="suggestWrap">
        <div className="suggestTitle">Suggested prompts</div>
        <div className="quickChips">
          {demoQs.map((item, i) => (
            <button
              key={i}
              type="button"
              className="chipCard"
              onClick={() => onQuickAsk(item.text)}
              disabled={busy}
              title={item.text}
            >
              <span className="chipIcon" aria-hidden>
                {item.icon}
              </span>
              <span className="chipText">{item.text}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function Message({ role, content, refs }) {
  const me = role === "user";
  if (!me) return null; // assistant handled by AnswerCard
  
  return (
    <div className="bubbleRow me">
      <div className="bubble bubbleMe">
        <div className="content">{content}</div>
      </div>
    </div>
  );
}

