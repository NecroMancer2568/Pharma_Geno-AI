# Pharmacogenomics AI Platform: Comprehensive Setup Guide

This guide walks you through the complete setup of the Pharmacogenomics AI platform, encompassing the acquisition of genetic datasets, building the vector knowledge base for RAG, training the ML classification model, setting up the local LLM, and getting the infrastructure production-ready.

## Overview of Components
The platform leverages a robust microservices architecture:
- **FastAPI Backend**: Handles API routing, file parsing (VCF/FASTA/23andMe).
- **Next.js Frontend**: The user interface.
- **Celery & Redis**: Background job processing for heavy genomic parsing and AI inference tasks.
- **Qdrant**: Vector database for Knowledge Base (RAG) retrieval.
- **Ollama**: Local instance running Gemma 4 (gemma2:9b) for clinical report generation.
- **XGBoost Classifier**: Determines clinical risk levels based on variant profiles.

---

## 1. Initial Infrastructure Setup

Ensure your machine (or deployment server) has **Docker, Docker Compose, Python 3.9+**, and **Node.js 18+** installed. You will also need sufficient RAM (at least 16GB) to comfortably run the local LLM and vector database.

> [!IMPORTANT]
> The easiest way to run the entire stack is via Docker. However, some initialization scripts are meant to be run locally, so you should set up a local Python virtual environment.

**Clone & Environments:**
1. Clone the project.
2. Setup environment variables:
   ```bash
   cp .env.example .env
   ```
3. Set up a local Python virtual environment in the `backend` directory:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

---

## 2. Infrastructure Services (Docker)

Start the fundamental services:
```bash
docker compose up -d redis qdrant ollama
```
*(You can also run `docker compose up -d` to spin up the whole stack, but we recommend spinning up the infrastructure first to ingest data into the DBs).*

---

## 3. Downloading Datasets

The platform parses variants against known databases.

Run the dataset download script:
```bash
python scripts/download_datasets.py
```
This script downloads a minimal/mock chunk of the ClinVar VCF to `backend/data/raw/clinvar.vcf.gz`. 

> [!NOTE]
> For a true production instance:
> - **ClinVar**: Edit the script to download the full 2GB+ VCF archive.
> - **PharmGKB**: Register at [pharmgkb.org/downloads](https://www.pharmgkb.org/downloads) and place `clinical_annotations.tsv` in `backend/data/raw/`.
> - **OMIM**: Request a license at [omim.org](https://www.omim.org) and place `genemap2.txt` in the same directory.

---

## 4. Knowledge Base & Vector Store Setup (RAG)

To augment the LLM's responses, the platform uses Retrieval-Augmented Generation (RAG) backed by Qdrant.

**Step 4.1: Generate the Knowledge Base**
```bash
python scripts/generate_synthetic_kb.py
```
This script generates ~200 synthetic markdown files in `backend/data/knowledge_base/` detailing clinical mechanisms, consequences, and CPIC dosing recommendations for the 13 primary pharmacogenes.

**Step 4.2: Index into Qdrant**
```bash
python scripts/index_knowledge_base.py
```
This requires `sentence-transformers` to be installed. It loops through the Markdown documents, parses the YAML frontmatter, encodes the text using the `all-MiniLM-L6-v2` embedding model, and upserts them into a Qdrant collection named `pharmacogenomics_kb`.

---

## 5. Training the ML Risk Classifier

The backend depends on a local XGBoost model to evaluate patient genotypes and output an initial risk classification (LOW, MODERATE, HIGH).

Run the training pipeline:
```bash
python scripts/train_classifier.py
```
**What this does:**
- Generates 1,500 rows of synthetic multigenic data across 13 genes.
- Trains an `XGBClassifier` utilizing softprob objective over 3 classes.
- Validates the model (5-fold Cross-Validation) and prints Precision/Recall/F1 scores.
- Serializes and stores the final model at `backend/trained_models/xgboost_risk.pkl`.

> [!WARNING]
> Your backend will crash on startup if `xgboost_risk.pkl` has not been generated or if it fails to load the model. Ensure this step completes successfully!

---

## 6. Local LLM Setup (Ollama + Gemma)

The system relies on Gemma running securely on-premises via Ollama. 

Pull the weights and initialize the model:
```bash
chmod +x scripts/pull_gemma.sh
./scripts/pull_gemma.sh
```
This contacts the Ollama service running on `http://localhost:11434` and pulls the `gemma2:9b` model structure into its volume.

---

## 7. Starting the Application Services

Once data, knowledge base, models, and the LLM are prepared, you are ready to start the remaining services:

### Production (Dockerized)
Run the entire stack via Docker:
```bash
docker compose up --build -d
```
This spins up:
- The `backend` FastAPI server on `http://localhost:8000`
- The `celery_worker` waiting for jobs via Redis.
- The `frontend` Next.js server on `http://localhost:3000`

### Local Development (Non-Docker)
If you prefer running services directly via your terminal:

**1. Start Redis, Qdrant, Ollama**:
```bash
docker compose up -d redis qdrant ollama
```
**2. Backend Main API**:
```bash
cd backend
uvicorn main:app --reload
```
**3. Celery Worker** (Required for processing genomic files):
```bash
cd backend
celery -A tasks.celery_tasks worker --loglevel=info
```
**4. Frontend Server**:
```bash
cd frontend
npm run dev
```

---

## 8. Summary of the Inference Flow

For you to understand how data is parsed and flows through the production infrastructure:

1. **Upload**: User uploads a VCF or 23andMe TXT file via Frontend.
2. **Parsing**: `services/preprocessing.py` uses `pyvcf3` to stream the VCF without overloading memory, filtering exclusively for variants overlapping standard GRCh38 coordinates natively linked to the 13 pharmacogenes (e.g., CYP2D6, DPYD).
3. **ML Risk Scoring**: The parsed variant profiles are fed into the XGBoost `.pkl` model running in the Celery worker, defining initial baseline risk.
4. **Vector Retrieval**: The patient's critical variants trigger a similarity search utilizing `sentence-transformers` against the Qdrant database to uncover clinical practice guidelines.
5. **LLM Generation**: The prompt combines the LLM task, ML risk score, extracted genotype data, and RAG context, and ships it to Gemma via the Ollama endpoint.
6. **Result**: A finished asynchronous clinical-grade report gets published to the Database and sent to the Frontend.

Your Pharmacogenomics AI Platform is now perfectly configured and ready for production inferences!
