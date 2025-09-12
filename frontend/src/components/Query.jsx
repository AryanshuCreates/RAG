import React, { useState } from "react";
import { queryQuestion } from "../api";

export default function Query({ lastIngest }) {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  async function ask(e) {
    e.preventDefault();
    if (!q) return;
    setLoading(true);
    try {
      const res = await queryQuestion(q);
      setResult(res);
    } catch (err) {
      console.error(err);
      alert("Query failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Ask a question</h2>
      {lastIngest && (
        <div style={{ fontSize: 13, color: "#555" }}>
          Last ingested: {JSON.stringify(lastIngest)}
        </div>
      )}
      <form onSubmit={ask} style={{ marginTop: 8 }}>
        <input
          style={{ width: "70%" }}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Type your question"
        />
        <button style={{ marginLeft: 8 }} type="submit">
          Ask
        </button>
      </form>

      {loading && <div style={{ marginTop: 12 }}>Thinking…</div>}

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Answer</h3>
          <div style={{ whiteSpace: "pre-wrap" }}>{result.answer}</div>

          <h4 style={{ marginTop: 12 }}>Sources</h4>
          <ul>
            {result.sources.map((s, i) => (
              <li key={i} style={{ marginBottom: 8 }}>
                <strong>{s.metadata?.source || "unknown"}</strong>
                <div style={{ fontSize: 13, color: "#333", marginTop: 4 }}>
                  {s.text}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
