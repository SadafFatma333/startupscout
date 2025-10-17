import React, { useEffect, useState } from "react";
import Chat from "./components/Chat.jsx";
import AuthPanel from "./components/AuthPanel.jsx";
import { api, API_BASE } from "./api";

export default function App() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [showBackend, setShowBackend] = useState(false); // Toggle for backend panel

  useEffect(() => {
    (async () => {
      try {
        const [h, s] = await Promise.all([api.health(), api.stats()]);
        setHealth(h);
        setStats(s);
      } catch {
        // ignore — BE might still be starting
      }
    })();
  }, []);

  return (
    <div className="page">
      <div className="sidebar">
        {/* Compact Backend Toggle */}
        <div className="panel backend-compact">
          <div className="panelTitle" style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <span>Backend</span>
            <button 
              onClick={() => setShowBackend(!showBackend)}
              style={{
                background: 'transparent',
                border: '1px solid var(--border)',
                color: 'var(--muted)',
                borderRadius: '4px',
                padding: '2px 6px',
                fontSize: '10px',
                cursor: 'pointer'
              }}
            >
              {showBackend ? 'Hide' : 'Show'}
            </button>
          </div>
          
          {showBackend ? (
            <>
              <div className="kv">
                <span className="k">API</span>
                <span className="v">{API_BASE}</span>
              </div>
              <div className="kv">
                <span className="k">Status</span>
                <span className="v">{health?.status || "unknown"}</span>
              </div>
              <div className="kv">
                <span className="k">DB</span>
                <span className="v">{health?.db || "unknown"}</span>
              </div>
              <div className="kv">
                <span className="k">Reqs</span>
                <span className="v">{stats?.requests ?? "-"}</span>
              </div>
              <div className="kv">
                <span className="k">Cache</span>
                <span className="v">
                  {stats?.cache?.redis_used
                    ? `redis:${stats.cache.keys ?? "?"}`
                    : `mem:${stats?.cache?.entries ?? "-"}`}
                </span>
              </div>
            </>
          ) : (
            <div className="kv">
              <span className="k">Status</span>
              <span className="v" style={{color: health?.status === 'ok' ? 'var(--accent-2)' : 'var(--danger)'}}>
                {health?.status || "unknown"}
              </span>
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panelTitle">Authentication</div>
          <AuthPanel onAuth={() => {}} />
        </div>
      </div>

      <div className="main">
        <Chat />
      </div>
    </div>
  );
}
