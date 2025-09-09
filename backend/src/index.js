require("dotenv").config();
const express = require("express");
const cors = require("cors");
const path = require("path");

const uploadRouter = require("./routes/upload");
const queryRouter = require("./routes/query");

const app = express();
app.use(cors());
app.use(express.json());

// Mount routers
app.use("/api/upload", uploadRouter);
app.use("/api/query", queryRouter);

// simple health
app.get("/health", (req, res) => res.json({ status: "ok" }));

const PORT = process.env.PORT || 4000;
app.listen(PORT, () => console.log(`Backend listening on ${PORT}`));
