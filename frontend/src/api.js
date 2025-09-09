import axios from "axios";

const BACKEND = import.meta.env.VITE_BACKEND_URL || "http://localhost:4000";

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const resp = await axios.post(`${BACKEND}/api/upload`, form, {
    headers: { "Content-Type": "multipart/form-data" },
    timeout: 120000,
  });
  return resp.data;
}

export async function queryQuestion(question) {
  const resp = await axios.post(
    `${BACKEND}/api/query`,
    { question },
    { timeout: 120000 }
  );
  return resp.data;
}
