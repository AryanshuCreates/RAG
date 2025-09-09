# 📘 RAG MVP — GenAI + Docker + Terraform + CI/CD

A **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents (`.pdf` / `.txt`), embed them, store embeddings in a vector DB, and query them through a simple web app.

---

## 🗂 Project Structure

RAG/
├── frontend/ # 🎨 React + Vite frontend
├── backend/ # ⚡ Express.js backend
├── ingest/ # 🐍 FastAPI service (embedding + retrieval)
├── docker-compose.yml
├── infra/ # ☁️ Terraform IaC (EC2 + S3 + IAM)
└── .github/workflows/cicd.yml

---

## ⚙️ Features

- ✅ Upload `.pdf` / `.txt` → parsed, chunked, embedded, and stored in **ChromaDB**.
- ✅ Ask questions via **Frontend → Backend → Ingest → LLM with context**.
- ✅ Fully **Dockerized microservices**.
- ✅ **Terraform deployment** (EC2 + S3).
- ✅ **CI/CD** via GitHub Actions (DockerHub + Terraform).
- 🔒 JWT-based **Auth-ready middleware** in backend (not enforced by default).

---

## 🔑 Environment Variables

Create a **`.env` file** in the project root:

```ini
# Common
OPENAI_API_KEY=sk-...

# Backend
PORT=4000
JWT_SECRET=supersecretkey
NODE_ENV=development
INGEST_URL=http://localhost:8000

# Ingest Service
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DB_PATH=./chroma_data
COLLECTION_NAME=rag_collection

# Frontend
VITE_API_URL=http://localhost:4000
VITE_INGEST_URL=http://localhost:8000

# AWS/Terraform
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
```

🖥️ Running Locally (Recommended for Dev)

👉 Step 1 — Create a Python Virtual Environment

- Powershell

# Ingest service (FastAPI) setup

cd ingest
python -m venv .venv
.venv\Scripts\activate # (PowerShell on Windows)

# source .venv/bin/activate # (Mac/Linux)

pip install -r requirements.txt

# 👉 Step 2 — Run ChromaDB (Vector DB)

- bash

# Start a local Chroma DB server

docker run -d --name chroma -p 8001:8000 -v ./chroma_data:/data chromadb/chroma:latest

# 👉 Step 3 — Run the Ingest Service

- bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000

# 👉 Step 4 — Run the Backend (Node.js + Express)

- bash

```
  cd backend
  npm install
  npm run dev # or npm start
```

# 👉 Step 5 — Run the Frontend (React + Vite)

- bash

```
  cd frontend
  npm install
  npm run dev
```

## 📍 Access the services:

- Frontend → http://localhost:3000

- Backend → http://localhost:4000

- Ingest → http://localhost:8000

- ChromaDB → http://localhost:8001

# 🐳 Running with Docker Compose

- bash

```
  docker-compose up --build
```

This will start all services (frontend, backend, ingest, chroma) together.

# ☁️ Deploying with Terraform + GitHub Actions

1. Provision infra:

- bash
  cd infra
  terraform init
  terraform apply

Creates:

- 🖥 EC2 instance (with Docker preinstalled)

- 📦 S3 bucket (deployment artifacts)

- 🔑 IAM roles/policies

2. CI/CD workflow (.github/workflows/cicd.yml) handles:

- Build + push Docker images → DockerHub

- Upload docker-compose.yml → S3

- EC2 pulls from S3 → runs containers

⚡ Planned improvement: auto-update EC2_IP in GitHub secrets via Terraform outputs.

# 🛡️ Authentication Middleware (Backend)

- JWT middleware is already implemented (backend/middleware/auth.js).

- Protect routes by wrapping with auth:

## js

```
const auth = require("./middleware/auth");
app.use("/secure", auth, secureRoutes);

```

- Use with:

```Authorization: Bearer <token>

```

# 📦 Tech Stack

- Frontend: ⚛️ React + ⚡ Vite + 📡 Axios

- Backend: 🟢 Node.js + 🚏 Express.js + 🔒 JWT

- Ingest: 🐍 FastAPI + 📄 pdfplumber + 🤗 Sentence Transformers + 🧠 OpenAI API + 🗄️ ChromaDB

- Infra: ☁️ Terraform (EC2 + S3 + IAM) + 🐳 Docker + ⚙️ Docker Compose

- CI/CD: 🔄 GitHub Actions + 🐳 DockerHub + ☁️ Terraform
