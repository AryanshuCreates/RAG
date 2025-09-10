# 📘 RAG MVP — GenAI + Docker + Terraform + CI/CD

A **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents (`.pdf` / `.txt`), embed them, store embeddings in a vector DB, and query them through a simple web app.

## 🏗️ Architecture

This project follows a **modular Retrieval-Augmented Generation (RAG)** architecture. Each layer is containerized and orchestrated via Docker Compose. Optionally, Terraform provisions infrastructure on AWS.

### Components

1. **Frontend (React + Vite)**

   - Provides a simple UI for users to upload documents and ask questions.
   - Connects to the backend API.
   - Deployed via Docker (served with Nginx in production).

2. **Backend (Express.js)**

   - Acts as the API gateway.
   - Routes requests between the frontend, ingest service, and vector database.
   - Includes middleware for authentication (JWT-ready, not fully implemented).
   - Exposes:
     - `/upload` → Send documents to ingestion service.
     - `/query` → Query stored embeddings and get LLM-generated answers.

3. **Ingest Service (FastAPI)**

   - Handles:
     - Document parsing (PDF/TXT).
     - Chunking into smaller segments.
     - Embedding generation.
     - Storing vectors in ChromaDB.
   - Provides `/ingest` and `/query` endpoints.

4. **Vector Database (ChromaDB)**

   - Stores embeddings of document chunks.
   - Performs semantic similarity search for queries.
   - Runs in a dedicated container with persistent volume.

5. **LLM (via API)**

   - Large Language Model used for answer generation.
   - Receives context retrieved from ChromaDB.
   - Configurable (OpenAI, Anthropic, local model, etc.).

6. **Infrastructure (Optional via Terraform)**

   - Provisions:
     - **EC2** → To host the Dockerized app.
     - **S3** → To store uploaded documents.
   - Terraform outputs (e.g., EC2 IP) can be wired into GitHub Actions secrets for automation.

7. **CI/CD (GitHub Actions)**
   - Builds and tests all services.
   - Builds Docker images.
   - Deploys to provisioned infrastructure.
   - Can automatically update services on push.

---

### High-Level Flow

1. User uploads `.pdf` or `.txt` via **Frontend**.
2. **Backend** forwards the file to the **Ingest Service**.
3. Ingest Service:
   - Extracts text.
   - Chunks content.
   - Generates embeddings.
   - Stores vectors in **ChromaDB**.
4. User submits a query.
5. **Backend** sends query to Ingest Service → retrieves relevant chunks from ChromaDB.
6. Retrieved context is passed to **LLM API** for final answer generation.
7. Answer with **source references** is returned to the **Frontend**.

## ⚙️ Features

- ✅ Upload `.pdf` / `.txt` → parsed, chunked, embedded, and stored in **ChromaDB**.
- ✅ Ask questions via **Frontend → Backend → Ingest → LLM with context**.
- ✅ Fully **Dockerized microservices**.
- ✅ **Terraform deployment** (EC2 + S3).
- ✅ **CI/CD** via GitHub Actions (DockerHub + Terraform).
- 🔒 JWT-based **Auth-ready middleware** in backend (not enforced by default).

---

## 🔑 1. Environment Variables

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

## 🔒 2. GitHub Actions Secrets (for CI/CD)

Go to Repo → Settings → Secrets and variables → Actions and add:

```ini
| Secret Name             | Purpose                                                     |
| ----------------------- | ----------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | For Terraform + S3/EC2 provisioning                         |
| `AWS_SECRET_ACCESS_KEY` | For Terraform + S3/EC2 provisioning                         |
| `AWS_REGION`            | e.g., `us-east-1`                                           |
| `DOCKERHUB_USERNAME`    | To push images to DockerHub                                 |
| `DOCKERHUB_TOKEN`       | DockerHub PAT (not password)                                |
| `OPENAI_API_KEY`        | Used by ingest service in EC2                               |
| `JWT_SECRET`            | For backend auth middleware (if enabled)                    |
| `EC2_IP`                | (Currently manual) used by workflow to know where to deploy |

```

🖥️ Running Locally (Recommended for Dev)

👉 Step 1 — Create a Python Virtual Environment

- Powershell
  Ingest service (FastAPI) setup

```ini
cd ingest
python -m venv .venv
.venv\Scripts\activate # (PowerShell on Windows)

# source .venv/bin/activate # (Mac/Linux)

pip install -r requirements.txt
```

👉 Step 2 — Run ChromaDB (Vector DB)

- bash

# Start a local Chroma DB server

```ini
docker run -d --name chroma -p 8001:8000 -v ./chroma_data:/data chromadb/chroma:latest
```

👉 Step 3 — Run the Ingest Service

- bash

```ini
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

👉 Step 4 — Run the Backend (Node.js + Express)

- bash

```ini
  cd backend
  npm install
  npm run dev # or npm start
```

👉 Step 5 — Run the Frontend (React + Vite)

- bash

```ini
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

```ini
  docker-compose up --build
```

This will start all services (frontend, backend, ingest, chroma) together.

# ☁️ Deploying to Production (Terraform + Docker + GitHub Actions)

This project includes **infrastructure-as-code (Terraform)** and **CI/CD automation (GitHub Actions)** to make production deployments seamless.

---

## 🛠️ What Gets Automated

✅ **Terraform** provisions:

- EC2 instance (Docker installed)
- S3 bucket (deployment artifacts)
- IAM roles/policies
- **EBS volume** (persistent storage for ChromaDB)

✅ **GitHub Actions** handles:

- Build + push all Docker images → DockerHub
- Upload `docker-compose.yml` to S3
- SSH into EC2 → auto-pull latest images → run `docker-compose up -d`

✅ **Data Persistence**:

- ChromaDB data is mounted to an **EBS volume** (`/data`) so embeddings are not lost on container restart.

✅ **Networking**:

- Only the **frontend** service is exposed to the public (via Nginx/port 80).
- Backend, ingest, and Chroma remain **internal** containers accessible only inside the Docker network.

---

## 🔧 What You Need To Do Manually

⚡ **Before First Deploy**

1. Add secrets in **GitHub Actions** (see section above).
2. Run Terraform once:
   ```bash
   cd infra
   terraform init
   terraform apply
   ```
   Copy the EC2 public IP and save it in GitHub Secrets as EC2_IP.

**🚀 Deployment Workflow**

1. Push code to main branch.

2. GitHub Actions runs automatically:

- Build all Docker images.

- Push to DockerHub.

- Deploy on EC2 via Docker Compose.

3. EC2 pulls the latest images and restarts services.

# 🛡️ Authentication Middleware (Backend)

- JWT middleware is already implemented (backend/middleware/auth.js).

- Protect routes by wrapping with auth:

## js

```ini
const auth = require("./middleware/auth");
app.use("/secure", auth, secureRoutes);

```

- Use with:

```ini
Authorization: Bearer <token>

```

**✅ Summary**

- Local Dev: Run with docker-compose up --build or manually via Node/FastAPI.

- Production: Push → GitHub Actions builds & deploys → EC2 auto-runs containers.

- Persistence: ChromaDB data is saved on EBS, not lost on restart.

- Security: Only frontend is exposed publicly; backend/ingest/Chroma are internal.

# 📦 Tech Stack

- Frontend: ⚛️ React + ⚡ Vite + 📡 Axios

- Backend: 🟢 Node.js + 🚏 Express.js + 🔒 JWT

- Ingest: 🐍 FastAPI + 📄 pdfplumber + 🤗 Sentence Transformers + 🧠 OpenAI API + 🗄️ ChromaDB

- Infra: ☁️ Terraform (EC2 + S3 + IAM) + 🐳 Docker + ⚙️ Docker Compose

- CI/CD: 🔄 GitHub Actions + 🐳 DockerHub + ☁️ Terraform
