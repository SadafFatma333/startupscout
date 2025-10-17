const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function authHeaders() {
  const token = localStorage.getItem("scout:token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function jsonFetch(path, { method = "GET", body, headers = {} } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...headers,
    },
    credentials: "include", // so backend can set/read session cookie
    body: body ? JSON.stringify(body) : undefined,
  });

  const isJson = (res.headers.get("content-type") || "").includes(
    "application/json"
  );
  const data = isJson ? await res.json() : await res.text();

  if (!res.ok) {
    const msg = data?.detail || data?.error || res.statusText || "Request failed";
    throw new Error(msg);
  }
  return data;
}

import { normalizeAsk } from "./lib/normalize";

export const api = {
  ask: async (question) => {
    const res = await jsonFetch(
      "/ask?" + new URLSearchParams({ question }).toString()
    );
    return normalizeAsk(res);
  },

  health: async () => jsonFetch("/health"),
  stats: async () => jsonFetch("/stats"),

  // optional auth (works only if your backend auth endpoints are enabled)
  register: async (email, password) =>
    jsonFetch("/auth/register", { method: "POST", body: { email, password } }),
  login: async (email, password) =>
    jsonFetch("/auth/login", { method: "POST", body: { email, password } }),

  // optional server chat history endpoints (your backend has /chat/history & /chat/clear)
  getHistory: async () => jsonFetch("/chat/history"),
  clearHistory: async () => jsonFetch("/chat/clear", { method: "POST" }),
};

export { API_BASE };
