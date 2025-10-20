import React, { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { clsx } from "clsx";

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
        {turns.map((t, idx) => (
          <Message key={t?.ts ?? idx} role={t.role} content={t.content} refs={t.refs} />
        ))}
        {busy ? <Typing /> : null}
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
  const refsArr = Array.isArray(refs) ? refs : [];

  return (
    <div className={clsx("bubbleRow", me ? "me" : "bot")}>
      <div className={clsx("bubble", me ? "bubbleMe" : "bubbleBot")}>
        <div className="content">{content}</div>

        {refsArr.length > 0 ? (
          <div className="refs">
            <span className="muted tiny">Sources</span>
            <ul>
              {refsArr.map((r, i) => {
                // Back-compat: older cached refs might be tuples like [title, ...]
                if (Array.isArray(r)) {
                  const [title] = r;
                  return (
                    <li key={`legacy-${i}`} className="tiny">
                      {String(title || "(untitled)")}
                    </li>
                  );
                }

                // Normalized object shape from API
                const title = r?.title ?? "(untitled)";
                const url = r?.url ?? null;
                const source = r?.source ?? null;
                const stage = r?.stage ?? null;
                const sim =
                  typeof r?.similarity === "number"
                    ? r.similarity
                    : (typeof r?.similarity === "string" ? Number(r.similarity) : null);
                const tags = Array.isArray(r?.tags) ? r.tags : [];

                return (
                  <li key={url ?? r?.id ?? `${title}-${i}`} className="tiny">
                    <div className="ref-title">
                      {url ? (
                        <a href={url} target="_blank" rel="noreferrer">
                          {title}
                        </a>
                      ) : (
                        title
                      )}
                    </div>
                    <div className="ref-meta muted">
                      {source && <span>{source}</span>}
                      {stage && <span> • {stage}</span>}
                      {typeof sim === "number" && !Number.isNaN(sim) && (
                        <span> • sim {sim.toFixed(2)}</span>
                      )}
                    </div>
                    {!!tags.length && (
                      <div className="ref-tags">
                        {tags.map((t) => (
                          <span key={t} className="tag">
                            {t}
                          </span>
                        ))}
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Typing() {
  return (
    <div className="bubbleRow bot">
      <div className="bubble bubbleBot typing">
        <span className="dot" />
        <span className="dot" />
        <span className="dot" />
      </div>
    </div>
  );
}
