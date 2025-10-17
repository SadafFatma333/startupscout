import { useState } from "react";
import { http, toMessage } from "../lib/http";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";

type SearchItem = {
  title: string;
  url: string;
  snippet?: string;
  tags?: string[];
  stage?: string;
};

type SearchResponse = {
  query: string;
  results: SearchItem[];
};

export default function Search() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [items, setItems] = useState<SearchItem[]>([]);

  async function onSearch(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setItems([]);
    if (!q.trim()) {
      setErr("Please enter a search query.");
      return;
    }
    setLoading(true);
    try {
      // Adjust param name to match your /search implementation
      const res = await http.get<SearchResponse>("/search", { params: { q } });
      setItems(res.data.results || []);
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1 className="text-xl font-semibold mb-4">Search</h1>
      <form onSubmit={onSearch} className="flex gap-2 mb-4">
        <input
          className="flex-1 border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
          placeholder="Try: pricing pivots, growth strategy, churn"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button
          className="bg-black text-white text-sm px-4 py-2 rounded-md"
          type="submit"
          disabled={loading}
        >
          Search
        </button>
      </form>

      {loading && <Loader label="Searching..." />}
      <ErrorBanner message={err} />

      <div className="space-y-3">
        {items.map((it, idx) => (
          <article key={idx} className="bg-white border rounded-md p-4">
            <a href={it.url} target="_blank" rel="noreferrer" className="text-sm font-semibold hover:underline">
              {it.title}
            </a>
            <div className="text-xs text-gray-600 mt-1">
              {it.stage ? `Stage: ${it.stage}` : null}
              {it.tags && it.tags.length ? ` | Tags: ${it.tags.join(", ")}` : null}
            </div>
            {it.snippet && <p className="text-sm text-gray-800 mt-2">{it.snippet}</p>}
          </article>
        ))}
      </div>
    </section>
  );
}
