import React, { useState } from "react";
import { api } from "../api";

export default function AuthPanel({ onAuth }) {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function submit(e) {
    e.preventDefault();
    setErr("");
    setBusy(true);
    try {
      const fn = mode === "login" ? api.login : api.register;
      const data = await fn(email.trim(), pw);
      // if backend returns token, store it
      if (data?.token) localStorage.setItem("scout:token", data.token);
      onAuth?.(data);
    } catch (ex) {
      setErr(ex.message || "Authentication failed");
    } finally {
      setBusy(false);
    }
  }

  function logout() {
    localStorage.removeItem("scout:token");
    onAuth?.(null);
  }

  const token = localStorage.getItem("scout:token");

  if (token) {
    return (
      <div className="auth-signed-in">
        <div className="auth-status">
          <div className="auth-status-indicator"></div>
          <span className="auth-status-text">Signed in</span>
        </div>
        <button 
          className="auth-logout-btn"
          onClick={logout}
        >
          Log out
        </button>
      </div>
    );
  }

  return (
    <form className="auth-form" onSubmit={submit}>
      <div className="auth-input-group">
        <label htmlFor="auth-email" className="auth-label">
          Email
        </label>
        <input
          id="auth-email"
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="auth-input"
          required
        />
      </div>
      
      <div className="auth-input-group">
        <label htmlFor="auth-password" className="auth-label">
          Password
        </label>
        <input
          id="auth-password"
          type="password"
          placeholder="Enter your password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          className="auth-input"
          required
        />
      </div>
      
      {err && (
        <div className="auth-error">
          {err}
        </div>
      )}
      
      <button 
        className="auth-submit-btn"
        disabled={busy}
      >
        {busy ? "..." : mode === "login" ? "Sign In" : "Create Account"}
      </button>
      
      <button
        type="button"
        className="auth-toggle-btn"
        onClick={() => setMode(mode === "login" ? "register" : "login")}
      >
        {mode === "login" ? "Need an account? Sign up" : "Have an account? Sign in"}
      </button>
    </form>
  );
}
