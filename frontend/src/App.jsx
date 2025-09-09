import React, { useState } from "react";
import Query from "./components/query";
import Upload from "./components/upload";

export default function App() {
  const [lastIngest, setLastIngest] = useState(null);
  return (
    <div
      style={{ maxWidth: 900, margin: "40px auto", fontFamily: "Inter, Arial" }}
    >
      <h1 style={{ textAlign: "center" }}>RAG MVP — Ask your documents</h1>
      <section style={{ marginTop: 24 }}>
        <Upload onIngest={(info) => setLastIngest(info)} />
      </section>
      <hr style={{ margin: "24px 0" }} />
      <section>
        <Query lastIngest={lastIngest} />
      </section>
    </div>
  );
}
