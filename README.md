# Pharmacogenomics AI Platform

This platform takes a patient's raw genetic report (VCF, 23andMe export, or FASTA file), runs it through an AI pipeline, and generates a clinical-grade report.

## Setup Instructions

1. **Clone the repository.**
2. **Copy `.env.example` to `.env`:**
   ```bash
   cp .env.example .env
   ```
3. **Start all services using Docker Compose:**
   ```bash
   docker compose up --build -d
   ```
4. **Pull the Gemma model:**
   ```bash
   chmod +x scripts/pull_gemma.sh
   ./scripts/pull_gemma.sh
   ```
5. **Access the platform:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Ollama API: http://localhost:11434
   - Qdrant Dashboard: http://localhost:6333/dashboard

## Architecture
- **Local LLM**: Gemma 4 via Ollama
- **Vector DB**: Qdrant
- **Backend**: FastAPI (Python) + Celery + Redis
- **Frontend**: Next.js 14 + Tailwind CSS