import React, { useState } from "react";
import { uploadFile } from "../api";

export default function Upload({ onIngest }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);

  async function submit(e) {
    e.preventDefault();
    if (!file) return alert("Select a file first");
    setStatus("uploading");
    try {
      const res = await uploadFile(file);
      setStatus("done");
      onIngest?.(res);
    } catch (err) {
      console.error(err);
      setStatus("error");
      alert("Upload failed");
    }
  }

  return (
    <div>
      <h2>Upload document (.pdf or .txt)</h2>
      <form onSubmit={submit}>
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={(e) => setFile(e.target.files?.[0])}
        />
        <button style={{ marginLeft: 12 }} type="submit">
          Upload & Ingest
        </button>
      </form>
      {status && <div style={{ marginTop: 8 }}>Status: {status}</div>}
    </div>
  );
}
