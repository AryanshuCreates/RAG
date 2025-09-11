const express = require("express");
const multer = require("multer");
const fs = require("fs");
const path = require("path");
const axios = require("axios");
const FormData = require("form-data");

const router = express.Router();
// const upload = multer({ dest: "/tmp/uploads" });  // for lunix
const upload = multer({ dest: path.join(__dirname, "../../tmp") }); // for windows

const INGEST_URL = process.env.INGEST_URL || "http://44.211.81.99:8000";

router.post("/", upload.single("file"), async (req, res) => {
  if (!req.file) return res.status(400).json({ error: "file is required" });
  try {
    const filePath = req.file.path;
    const stream = fs.createReadStream(filePath);
    const form = new FormData();
    form.append("file", stream, { filename: req.file.originalname });

    const headers = form.getHeaders();
    // Forward to ingest service
    const resp = await axios.post(`${INGEST_URL}/ingest`, form, {
      headers,
      timeout: 120000,
    });

    // cleanup
    fs.unlink(filePath, () => {});
    return res.json(resp.data);
  } catch (err) {
    console.error("upload error", err?.response?.data || err.message || err);
    return res.status(500).json({
      error: "upload failed",
      detail: err?.response?.data || err.message,
    });
  }
});

module.exports = router;
