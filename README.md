# 📘 RAG MVP — GenAI + Docker + Terraform + CI/CD

A **Retrieval-Augmented Generation (RAG)** application that allows users to upload documents (`.pdf` / `.txt`), embed them, store embeddings in a vector DB, and query them through a simple web app. There are some refinements needed on Terraform and ci/cd.

## 🏗️ Architecture

This project follows a **modular Retrieval-Augmented Generation (RAG)** architecture. Each layer is containerized and orchestrated via Docker Compose. Optionally, Terraform provisions infrastructure on AWS.

### Components

1. **Frontend (React + Vite)**

   - Provides a simple UI for users to upload documents and ask questions. (when running on a smaller compute, please upload small docs 5-6 pages)
   - Connects to the backend API.
   - Deployed via Docker.

2. **Backend (Express.js)** (kept a separate backend to keep the rag flow standalone and other non-rag features can he added in Node)

   - Acts as the API gateway.
   - Routes requests between the frontend, ingest service, and vector database.
   - Includes middleware for authentication (JWT-ready, need to apply on which routes to guard).
   - Exposes:
     - `/upload` → Send documents to ingestion service.
     - `/query` → Query stored embeddings and get LLM-generated answers.

3. **Ingest Service (FastAPI)**

   - Handles:
     - Document parsing (PDF/TXT).
     - Chunking into smaller segments. (current chunk size is 800 char, overlap is 120 chars)
     - Embedding generation.
     - Storing vectors in ChromaDB.
   - Provides `/ingest` and `/query` endpoints.

4. **Vector Database (ChromaDB)**

   - Stores embeddings of document chunks.
   - Performs semantic similarity search for queries.
   - persistent volume.

5. **LLM (via API)**

   - Large Language Model used for answer generation. (need to add Open AI token in env)
   - Receives context retrieved from ChromaDB.
     

6. **Infrastructure (Optional via Terraform)** (still need work to do)

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

# 🐳 Deploying on EC2

This project can be deployed in **two ways**: manual or automated.

---

## 1️⃣ Manual Docker + EC2 Process

⚡ **Steps:**

1. **Provision EC2 & EBS** (via Terraform or manually).
2. **Install Docker & Docker Compose** on EC2:

````bash
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```
3. **Copy project files:**

.env
docker-compose.yml
to the EC2 instance (e.g., via scp):

``` bash
scp -i my-key.pem docker-compose.yml .env ec2-user@<EC2_IP>:/home/ec2-user/
````

4. **Run services:** (Docker Compose file is in RAG/infra/docker-compose.yml)

```bash
docker-compose up --build -d
```

5. **Access services:**

Service URL
Frontend http://<EC2_IP>/
Backend http://<EC2_IP>:4000
Ingest http://<EC2_IP>:8000
ChromaDB http://<EC2_IP>:8001

✅ ChromaDB data persists on mounted EBS volume.

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

````

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
````
