import { useState } from "react";
import { http, toMessage } from "../lib/http";
import Loader from "../components/Loader";
import ErrorBanner from "../components/ErrorBanner";

type AskResponse = {
  question: string;
  answer: string;
  references?: [string, string, string, string][];
};

export default function Ask() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");
  const [data, setData] = useState<AskResponse | null>(null);

  async function onAsk(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setData(null);
    if (!q.trim()) {
      setErr("Please enter a question.");
      return;
    }
    setLoading(true);
    try {
      const res = await http.get<AskResponse>("/ask", { params: { question: q } });
      setData(res.data);
    } catch (e) {
      setErr(toMessage(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1 className="text-xl font-semibold mb-4">Ask StartupScout</h1>
      <form onSubmit={onAsk} className="flex gap-2 mb-4">
        <input
          className="flex-1 border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-black"
          placeholder="Ask about growth, pricing, churn, fundraising..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <button
          className="bg-black text-white text-sm px-4 py-2 rounded-md"
          type="submit"
          disabled={loading}
        >
          Ask
        </button>
      </form>

      {loading && <Loader label="Fetching answer..." />}
      <ErrorBanner message={err} />

      {data && (
        <div className="mt-4 space-y-3">
          <div className="bg-white border rounded-md p-4">
            <div className="text-sm text-gray-500 mb-1">Question</div>
            <div className="text-sm">{data.question}</div>
          </div>
          <div className="bg-white border rounded-md p-4">
            <div className="text-sm text-gray-500 mb-1">Answer</div>
            <div className="whitespace-pre-wrap text-sm">{data.answer}</div>
          </div>
          {data.references && data.references.length > 0 && (
            <div className="bg-white border rounded-md p-4">
              <div className="text-sm text-gray-500 mb-2">References</div>
              <ul className="list-disc list-inside text-sm space-y-1">
                {data.references.map((r, idx) => (
                  <li key={idx}>
                    <span className="font-medium">{r[0]}</span> — <span className="text-gray-600">{r[2]}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
