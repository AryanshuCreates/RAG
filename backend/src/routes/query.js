const express = require("express");
const axios = require("axios");

const router = express.Router();
const INGEST_URL = process.env.INGEST_URL || "http://44.211.81.99:8000";

router.post("/", async (req, res) => {
  const { question } = req.body || {};
  if (!question) return res.status(400).json({ error: "question is required" });
  try {
    const resp = await axios.post(
      `${INGEST_URL}/query`,
      { question },
      { timeout: 120000 }
    );
    return res.json(resp.data);
  } catch (err) {
    console.error("query error", err?.response?.data || err.message || err);
    return res.status(500).json({
      error: "query failed",
      detail: err?.response?.data || err.message,
    });
  }
});

module.exports = router;
