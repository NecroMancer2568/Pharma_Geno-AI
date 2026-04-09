# Pharmacogenomics AI Platform — Master Context Document for Claude Code

> This document contains the full project context, architecture decisions, data sources, technology choices, and step-by-step build instructions. No code is included — this is the intelligence layer that guides every implementation decision.

---

## What This Project Does

This platform takes a patient's raw genetic report (VCF, 23andMe export, or FASTA file), runs it through an AI pipeline, and generates a clinical-grade report containing:

- **Drug-gene compatibility scores** — which medications are safe, risky, or contraindicated for this patient based on their genetic variants
- **Overall genomic risk score** — a 0–100 composite score representing the patient's pharmacogenomic risk burden
- **Gene compatibility rates and percentages** — how each pharmacogene (e.g. CYP2D6, CYP2C19) is functioning relative to population norms
- **Disease predisposition predictions** — probability percentages for diseases that can be inferred from the patient's SNP profile
- **Actionable clinical recommendations** — physician-ready guidance derived from CPIC and PharmGKB evidence-based guidelines

The entire inference stack runs locally. No patient data ever leaves the server. No external LLM APIs are called.

---

## Technology Stack — Every Choice Explained

### Local LLM: Gemma 4 via Ollama

Gemma 4 is Google's open-weight model served locally through Ollama. It is chosen because it runs without internet connectivity (critical for patient data privacy), supports long context windows needed for RAG-enriched genomic prompts, and has strong instruction-following for structured JSON output generation. Ollama provides a simple REST API on port 11434 that the backend calls directly. No GPU is strictly required but one significantly improves inference speed. Use the `gemma2:27b` variant for production accuracy or `gemma2:9b` for faster development iteration.

### Vector Database: Qdrant

Qdrant is the vector database that powers the RAG (Retrieval-Augmented Generation) system. It runs locally via Docker on port 6333. It is chosen over alternatives because it supports metadata filtering (allowing retrieval to be scoped by gene name, drug class, or evidence level before semantic search), has a Python SDK, requires no cloud account, and handles the payload sizes needed for clinical text chunks. All PharmGKB, CPIC, and ClinVar knowledge base documents are embedded and stored here.

### Embedding Model: sentence-transformers (local)

Genomic text and patient profiles are converted to vector embeddings using a local sentence-transformers model. Use `all-MiniLM-L6-v2` for speed or `BiomedNLP-BiomedBERT-base` for clinical accuracy. This model runs entirely in-process within the Python backend. No embedding API calls are made externally.

### ML Risk Models: XGBoost + Polygenic Risk Scores

Two separate ML systems handle numeric prediction, separate from the LLM which handles language generation. An XGBoost classifier trained on PharmGKB clinical annotation data predicts drug-gene interaction risk categories (HIGH / MODERATE / LOW) and outputs a 0–100 composite risk score based on the patient's metabolizer status profile across all pharmacogenes. Polygenic Risk Score (PRS) calculations using PLINK2-style weighted SNP scoring estimate disease predisposition percentages relative to population averages.

### Backend: FastAPI (Python)

Python is mandatory for the backend because all genomics libraries (BioPython, PyVCF, pysam), ML frameworks (PyTorch, XGBoost, scikit-learn), and LLM tooling (LangChain, sentence-transformers, Qdrant SDK) have their primary SDKs in Python. FastAPI provides async request handling and clean Pydantic schema validation. It runs on port 8000.

### Async Job Processing: Celery + Redis

Genomic analysis is computationally expensive — a full pipeline run takes 30–120 seconds depending on hardware. This means it cannot run synchronously in an HTTP request. Celery processes jobs asynchronously with Redis as the message broker. The frontend polls a job status endpoint every 2 seconds to show real-time progress. Redis runs on port 6379.

### Frontend: Next.js 14 + TypeScript + Tailwind CSS

The user-facing interface is built in Next.js 14 using the App Router, TypeScript for type safety, and Tailwind CSS for styling. It communicates with the FastAPI backend via REST API calls. Key UI flows: file upload with drag-and-drop, real-time job progress polling, results dashboard with risk visualizations, and PDF report download.

### PDF Generation: ReportLab (Python)

Clinical PDF reports are generated server-side in Python using ReportLab. This produces professional, printable reports that physicians can attach to patient records. The PDF includes the risk score, gene activity table, drug compatibility matrix, disease risk panel, AI summary, and recommendations. ReportLab is preferred over WeasyPrint because it is pure Python with no system library dependencies, making Docker containerization simpler.

### Containerization: Docker Compose

All services (FastAPI, Celery worker, Qdrant, Redis, Ollama, Next.js) are orchestrated via a single Docker Compose file. This ensures the entire stack starts with one command and behaves identically across development and production environments.

---

## Complete System Architecture

The data flows through the system in this exact sequence:

**Step 1 — File Ingestion**
The patient or clinician uploads a gene report file through the Next.js frontend. Supported formats are VCF (Variant Call Format from clinical sequencing labs), 23andMe raw data export (tab-separated text), and FASTA sequence files. The file is sent to FastAPI via a multipart form POST.

**Step 2 — Job Creation**
FastAPI saves the uploaded file to disk, creates a job record in the database with a unique job ID, and immediately dispatches the job to Celery. The frontend receives the job ID and begins polling the status endpoint every 2 seconds.

**Step 3 — Genomic Preprocessing**
The Celery worker parses the gene report file using BioPython and PyVCF. It extracts all SNP variants and filters them down to the 13 key pharmacogenes: CYP2D6, CYP2C19, CYP2C9, CYP3A4, CYP3A5, DPYD, TPMT, VKORC1, SLCO1B1, UGT1A1, NUDT15, G6PD, and HLA-B. These genes govern how the body metabolizes the majority of commonly prescribed medications.

**Step 4 — Variant Annotation**
Each extracted variant is cross-referenced against ClinVar via the NCBI Entrez API to retrieve its clinical significance classification (pathogenic, likely pathogenic, benign, uncertain significance). This step enriches the raw SNP data with established medical meaning.

**Step 5 — Metabolizer Status Determination**
Using known star allele mappings from CPIC guidelines, each pharmacogene is assigned a metabolizer status: Poor Metabolizer, Intermediate Metabolizer, Normal Metabolizer, or Rapid/Ultrarapid Metabolizer. For example, a patient with two non-functional CYP2D6 alleles is classified as a CYP2D6 Poor Metabolizer, meaning codeine will not convert to morphine and other drugs metabolized by this enzyme may accumulate dangerously.

**Step 6 — Embedding Generation**
The patient's full genomic profile (all metabolizer statuses and annotated variants) is converted into a text representation and embedded using the local sentence-transformers model. This embedding vector captures the semantic meaning of the patient's pharmacogenomic state.

**Step 7 — RAG Retrieval from Qdrant**
Using the patient's embedding, Qdrant performs a cosine similarity search across the indexed knowledge base (PharmGKB, CPIC, OMIM documents). The top 6–8 most relevant drug-gene guideline chunks are retrieved. These contain evidence-based clinical recommendations specific to the patient's genetic variants.

**Step 8 — Prompt Assembly**
A structured prompt is built containing the patient's metabolizer status summary, the retrieved clinical guideline context, and precise instructions for Gemma 4 to output a structured JSON report covering drug compatibilities, overall risk score, disease predispositions, and recommendations.

**Step 9 — Gemma 4 Inference**
The assembled prompt is sent to the Ollama API endpoint running Gemma 4 locally. Inference runs with a low temperature (0.1) for clinical precision. The model returns a structured JSON response containing all report fields.

**Step 10 — Risk Scoring**
In parallel with LLM inference, the XGBoost classifier processes the metabolizer status feature vector and outputs a 0–100 composite risk score. The PRS calculator computes disease probability percentages.

**Step 11 — PDF Generation**
ReportLab assembles the final clinical PDF containing all report sections. The file is saved to disk.

**Step 12 — Results Delivery**
The job status is updated to "complete" in the database. The Next.js frontend's polling detects the completion, fetches the full report JSON, and renders the results dashboard. The physician can download the PDF.

---

## Directory Structure

```
pharmacogenomics-ai/
├── frontend/                        # Next.js 14 + TypeScript
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                 # Landing / upload page
│   │   ├── dashboard/
│   │   │   └── [jobId]/page.tsx     # Results dashboard
│   │   └── api/
│   │       ├── upload/route.ts      # BFF proxy to FastAPI
│   │       ├── job/[id]/route.ts
│   │       └── report/[id]/route.ts
│   ├── components/
│   │   ├── FileUpload.tsx
│   │   ├── JobStatus.tsx
│   │   ├── RiskGauge.tsx
│   │   ├── DrugCompatibilityTable.tsx
│   │   ├── DiseaseRiskPanel.tsx
│   │   └── ReportExport.tsx
│   ├── lib/
│   │   ├── api.ts                   # All API calls live here, not in components
│   │   └── types.ts                 # TypeScript interfaces matching backend schemas
│   └── package.json
│
├── backend/                         # FastAPI (Python)
│   ├── main.py                      # App entry point, middleware, router registration
│   ├── routers/
│   │   ├── upload.py                # POST /api/upload/, GET /api/upload/status/{id}
│   │   ├── jobs.py                  # Job management endpoints
│   │   └── reports.py               # GET /api/reports/{id}, GET /api/reports/{id}/pdf
│   ├── services/
│   │   ├── preprocessing.py         # VCF/23andMe/FASTA parsing and pharmacogene extraction
│   │   ├── annotation.py            # ClinVar API annotation and star allele mapping
│   │   ├── embedding.py             # Sentence-transformer embedding generation
│   │   ├── rag.py                   # Qdrant retrieval and prompt assembly
│   │   ├── llm.py                   # Gemma 4 via Ollama, JSON extraction, fallback handling
│   │   ├── classifier.py            # XGBoost risk scoring and rule-based fallback
│   │   └── report_generator.py      # ReportLab PDF creation
│   ├── models/
│   │   ├── schemas.py               # All Pydantic models (GenomicReport, JobStatus, etc.)
│   │   └── db.py                    # SQLAlchemy ORM models and CRUD functions
│   ├── tasks/
│   │   └── celery_tasks.py          # Celery task definitions and pipeline orchestration
│   ├── data/
│   │   ├── raw/                     # Downloaded source files (ClinVar VCF, PharmGKB TSVs)
│   │   ├── knowledge_base/          # Processed markdown documents ready for indexing
│   │   └── processed/               # Training data CSVs for XGBoost
│   └── trained_models/              # Serialized model files (.pkl)
│
├── scripts/
│   ├── index_knowledge_base.py      # Reads knowledge_base/, embeds, uploads to Qdrant
│   ├── download_datasets.py         # Automated download of ClinVar; manual instructions for PharmGKB
│   ├── train_classifier.py          # XGBoost training on processed PharmGKB data
│   └── pull_gemma.sh                # Ollama model pull command
│
├── docker-compose.yml               # All services: qdrant, redis, ollama, backend, celery, frontend
├── .env.example                     # All required environment variables with descriptions
└── README.md
```

---

## Data Sources — What to Download and Where to Get It

### PharmGKB (Primary Source — Most Important)

Website: pharmgkb.org/downloads — requires a free account registration.

Files needed:
- `clinical_annotations.tsv` — the core drug-gene-phenotype association table with evidence levels (1A, 1B, 2A, 2B, 3, 4). Evidence level 1A means a CPIC guideline exists. This file is the backbone of the drug compatibility scoring.
- `relationships.zip` — gene-drug-disease relationship graph data.
- `drug_labels.zip` — FDA and EMA drug label annotations with pharmacogenomic sections.

After downloading, each clinical annotation entry must be converted into a structured markdown document with YAML frontmatter containing the gene name, drug name, evidence level, and source. The body text should contain the clinical summary and recommendation. These markdown files are what get chunked and indexed into Qdrant.

### CPIC Guidelines (Clinical Rules)

Website: cpicpgx.org/genes-drugs/ — fully public, no login required.

CPIC publishes pair-specific guidelines for each gene-drug combination. Each guideline PDF contains dosing recommendations based on metabolizer phenotype. Convert these to markdown and add to the knowledge base. Prioritize these high-priority drug-gene pairs: CYP2D6+codeine, CYP2D6+tamoxifen, CYP2C19+clopidogrel, CYP2C19+SSRIs, DPYD+fluorouracil, TPMT/NUDT15+thiopurines, VKORC1/CYP2C9+warfarin, SLCO1B1+simvastatin.

### ClinVar (Variant Significance)

FTP: ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz — fully public.

This VCF file maps rsIDs to clinical significance classifications. It is used at query time via the NCBI Entrez API rather than being indexed into Qdrant (the file is too large to fully embed). The annotation service makes targeted API calls for specific rsIDs found in the patient's gene report. Register for a free NCBI API key at ncbi.nlm.nih.gov/account/ to raise the rate limit from 3 to 10 requests per second.

### OMIM (Disease-Gene Links)

Website: omim.org — requires a free academic license application.

OMIM maps genes to Mendelian diseases. Used to populate the disease predisposition section. The `genemap2.txt` file is the key download. Convert each disease-gene entry to a knowledge base markdown document.

### gnomAD (Population Frequencies)

Website: gnomad.broadinstitute.org — fully public.

Provides allele frequencies for every SNP across diverse human populations. Used to contextualize whether a patient's variant is rare (potentially more significant) or common. Only extract frequency data for the 13 target pharmacogenes — the full gnomAD dataset is terabytes.

---

## Knowledge Base Document Format

Every document indexed into Qdrant must follow this structure. The YAML frontmatter block (between `---` delimiters at the top of each file) must contain:

- `gene` — the HGNC gene symbol (e.g. CYP2D6)
- `drug` — the drug name, or "N/A" for disease-only documents
- `evidence_level` — CPIC/PharmGKB evidence code: 1A, 1B, 2A, 2B, 3, 4, or "disease" for OMIM entries
- `source` — one of: PharmGKB, CPIC, OMIM, ClinVar, FDA

The body of each document should be 300–500 words covering: the biological mechanism of the gene-drug interaction, the clinical consequence for each metabolizer phenotype, the specific CPIC dosing recommendation or FDA label warning, and any population-specific considerations. Longer source documents should be split into multiple files, each covering one gene-drug pair.

Target a minimum of 200 knowledge base documents before the first end-to-end test. 500+ documents significantly improves report quality.

---

## Pharmacogene Reference — The 13 Core Genes

Claude Code must implement metabolizer status determination for all 13 of these genes.

**CYP2D6** — Chromosome 22. Metabolizes 25% of all prescribed drugs including codeine, tramadol, tamoxifen, many antidepressants (SSRIs, TCAs), antipsychotics, and beta-blockers. Poor metabolizer star alleles include `*3` (rs35742686), `*4` (rs3892097), `*5` (gene deletion), `*6` (rs5030655). Ultrarapid metabolizer results from gene duplication. This is the most clinically impactful pharmacogene.

**CYP2C19** — Chromosome 10. Metabolizes clopidogrel (critical for cardiac stent patients), PPIs (omeprazole, pantoprazole), and many SSRIs/SNRIs. Poor metabolizer alleles: `*2` (rs4244285), `*3` (rs4986893). Rapid metabolizer: `*17` (rs12248560). Clopidogrel non-response in `*2/*2` patients is a major clinical safety concern.

**CYP2C9** — Chromosome 10. Metabolizes warfarin, NSAIDs, phenytoin, and sulfonylureas. Poor metabolizer alleles: `*2` (rs1799853), `*3` (rs1057910). Warfarin dosing must be significantly reduced in `*3` carriers to avoid bleeding.

**CYP3A4 and CYP3A5** — Chromosome 7. Together metabolize approximately 50% of all drugs. CYP3A5 `*3` (rs776746) is the most common loss-of-function variant. Critical for tacrolimus dosing in transplant patients.

**DPYD** — Chromosome 1. Metabolizes fluorouracil (5-FU) and capecitabine used in cancer chemotherapy. Poor metabolizers face life-threatening toxicity from standard doses. Key variants: `*2A` (rs3918290), `c.2846A>T` (rs67376798). This is a patient safety-critical gene — always flag regardless of evidence level threshold.

**TPMT and NUDT15** — Chromosome 6 and 13 respectively. Both affect thiopurine metabolism (azathioprine, mercaptopurine, thioguanine used in leukemia and autoimmune disease). Poor metabolizers accumulate toxic thioguanine nucleotides. Must be evaluated together.

**VKORC1** — Chromosome 16. The warfarin target enzyme. The `rs9923231` variant significantly reduces warfarin dose requirements. Must be evaluated together with CYP2C9 for warfarin dosing.

**SLCO1B1** — Chromosome 12. Transports statins into liver cells. The `*5` variant (rs4149056) reduces statin uptake, increasing plasma levels and myopathy risk. Important for simvastatin, atorvastatin, rosuvastatin patients.

**UGT1A1** — Chromosome 2. Metabolizes irinotecan (cancer chemotherapy) and is responsible for Gilbert's syndrome. `*28` variant (rs3064744) causes severe irinotecan toxicity at standard doses.

**G6PD** — Chromosome X. Deficiency causes hemolytic anemia when exposed to certain drugs (primaquine, rasburicase, dapsone). X-linked inheritance means males with one variant allele are fully affected.

**HLA-B** — Chromosome 6. Specific HLA alleles cause severe drug hypersensitivity reactions. `HLA-B*57:01` causes abacavir hypersensitivity in HIV treatment. `HLA-B*58:01` causes allopurinol-induced Stevens-Johnson syndrome. These are the most severe pharmacogenomic safety signals — always flag in any report regardless of other risk thresholds.

---

## API Endpoint Specification

**POST /api/upload/** — Accepts a multipart form with the gene report file and patient ID. Saves the file, creates a job record, dispatches to Celery. Returns `{ job_id, status: "processing", message }`.

**GET /api/upload/status/{job_id}** — Returns the current job status object. The frontend polls this every 2 seconds. Returns `{ job_id, status, progress, current_step, result, error }`.

**GET /api/reports/{job_id}** — Returns the complete GenomicReport JSON object once the job is complete.

**GET /api/reports/{job_id}/pdf** — Returns the PDF file as a binary blob with `Content-Type: application/pdf`. Triggers a browser download.

**GET /health** — Returns `{ status: "ok" }`. Used by Docker Compose health checks.

---

## Data Schema — Every Field Defined

### GenomicReport (master output object)

- `job_id` — UUID string
- `patient_id` — string provided at upload time
- `overall_risk_score` — float 0–100, XGBoost-computed composite risk score
- `drug_compatibilities` — array of DrugCompatibility objects
- `disease_risks` — array of DiseaseRisk objects
- `gene_activity_scores` — dictionary mapping each pharmacogene name to its metabolizer status string
- `ai_summary` — Gemma 4 generated clinical narrative paragraph for the treating physician
- `recommendations` — array of 3–5 string recommendations from Gemma 4
- `created_at` — ISO 8601 timestamp
- `pdf_path` — server-side file path to the generated PDF

### DrugCompatibility

- `drug_name` — medication name (e.g. "Clopidogrel")
- `gene` — primary gene responsible for the interaction (e.g. "CYP2C19")
- `compatibility_score` — float 0.0 to 1.0, where 1.0 is fully compatible and 0.0 is contraindicated
- `risk_level` — enum: HIGH, MODERATE, or LOW
- `recommendation` — specific clinical action as a string
- `evidence_level` — PharmGKB/CPIC classification: 1A (highest) through 4 (lowest)

### DiseaseRisk

- `disease_name` — condition name (e.g. "Warfarin Bleeding Risk")
- `risk_percentage` — float 0–100, patient's estimated risk
- `population_average` — float 0–100, general population baseline for comparison
- `associated_genes` — array of gene name strings
- `risk_category` — enum: HIGH, MODERATE, or LOW

### JobStatus

- `job_id` — UUID string
- `status` — enum: pending, processing, complete, failed
- `progress` — integer 0–100
- `current_step` — human-readable description of the current pipeline stage
- `result` — null during processing, GenomicReport object when complete
- `error` — null unless status is failed

---

## Gemma 4 Prompt Engineering Guidelines

The quality of the clinical report depends entirely on prompt quality. The prompt must follow these principles exactly.

Open with a clear role definition: Gemma 4 is a clinical pharmacogenomics AI assistant producing structured medical reports.

The patient profile section must present the 13 gene metabolizer statuses in a clean list format. Never include raw rsID data in the LLM prompt — it adds noise without clinical value for the generation task.

The retrieved context section must include the RAG-retrieved clinical guideline chunks verbatim, each labeled with its source (PharmGKB, CPIC), gene, drug, and evidence level. Include a maximum of 6 chunks to stay within context limits.

The task instruction must explicitly request JSON output and define every field name and data type expected. Include a JSON schema example in the prompt. Gemma 4 responds reliably to explicit schema definitions.

Temperature must be set to 0.1 for clinical precision. Higher temperatures introduce hallucinations in medical contexts.

Always validate the JSON output from Gemma 4 against the schema before saving. If JSON parsing fails, first attempt to find and parse the JSON block within the response text (search for the first `{` and last `}`). If extraction also fails, return a structured fallback error response — never crash the Celery job.

---

## XGBoost Training Data Requirements

The classifier requires processed training data before it can be trained. The PharmGKB `clinical_annotations.tsv` must be processed into a training CSV with one column per pharmacogene (13 total) containing the metabolizer status for each sample, and an `outcome` column with values low/moderate/high representing the drug interaction severity.

Since real patient genomic training data is not publicly available, the training set is constructed from PharmGKB's known variant-phenotype-outcome associations. Each row represents a known genotype combination and its documented clinical outcome. A minimum of 1,000 rows is required before training is meaningful. Augmentation with synthetic samples based on known haplotype frequencies from gnomAD is acceptable.

Class imbalance is expected (most interactions are LOW risk). Use `scale_pos_weight` in XGBoost to handle this. Train with 5-fold cross-validation and report precision, recall, and F1 per class.

If the trained model file does not exist at runtime, the classifier service must fall back to a deterministic rule-based scoring function using CPIC star allele clinical significance ratings. This fallback ensures the pipeline always produces output even before model training is complete. Poor Metabolizer status on any critical gene (DPYD, HLA-B, CYP2D6, CYP2C19) should contribute significant points to the rule-based score.

---

## Celery Job Pipeline — Step Labels and Progress Percentages

Each pipeline stage must update the job record with both a progress integer and a human-readable step label. The frontend displays these in real time.

1. `"Parsing gene report"` — 5%
2. `"Extracting pharmacogene variants"` — 15%
3. `"Annotating variants with ClinVar"` — 25%
4. `"Determining metabolizer status"` — 35%
5. `"Generating genomic embeddings"` — 45%
6. `"Retrieving clinical guidelines (RAG)"` — 55%
7. `"Assembling clinical context"` — 62%
8. `"Running Gemma 4 analysis"` — 65% held until inference completes, then jumps to 85%
9. `"Calculating risk scores"` — 90%
10. `"Generating PDF report"` — 95%
11. `"Complete"` — 100%

The entire Celery task must be wrapped in a top-level try-except that catches all exceptions, logs the full traceback, and updates the job status to "failed" with the error message. Without this, failed jobs appear stuck at the last progress percentage indefinitely.

---

## Frontend UI Specification

### Page 1: Landing / Upload (route: `/`)

The page should feel clinical and trustworthy — clean white background, minimal decoration. Contains a centered card with a text input for patient ID (required before upload is enabled), a drag-and-drop file upload zone accepting VCF, TXT, TSV, FASTA files with clear file type labels, and a brief explanation of what the platform does. On upload success, immediately redirect to the dashboard page with the job ID in the URL.

### Page 2: Analysis Dashboard (route: `/dashboard/[jobId]`)

While the job is processing, show a progress bar with the current step label updating every 2 seconds.

When the job is complete, render:

- A top-level risk gauge or score display showing the 0–100 overall risk score with a color band (green 0–33, amber 34–66, red 67–100)
- Gene activity profile — a table showing each of the 13 genes and their metabolizer status, color-coded by severity
- Drug compatibility table — each row is a drug with columns for gene, risk level badge (colored HIGH/MODERATE/LOW), compatibility score, evidence level, and recommendation text
- Disease risk panel — a list of diseases with the patient's risk percentage vs population average shown as comparative bars
- AI clinical summary — the Gemma 4 generated paragraph in a clearly demarcated box with a note that this is AI-generated and requires physician interpretation
- Recommendations list — 3–5 numbered action items
- Export PDF button in the top-right of the page

### Component Architecture Rules

Each major UI section is its own isolated React component with a TypeScript props interface. The API client is a standalone module in `lib/api.ts` — no API calls are made directly from components. All polling logic lives in a custom hook or a useEffect in the dashboard page, not in child components. All TypeScript types are defined in `lib/types.ts` and must exactly match the backend Pydantic schema field names and types.

---

## Security and Compliance Requirements

All patient genomic data is health information subject to privacy regulation. These requirements are non-negotiable and must be implemented, not deferred.

Patient files must be stored encrypted at rest using AES-256. The encryption key must come from an environment variable, never hardcoded.

All genomic data must be anonymized before entering the LLM prompt. The prompt must contain metabolizer status labels only — never the patient's name, date of birth, MRN, or any direct identifier.

All API endpoints that return patient data must require authentication. Implement JWT-based auth with tokens that expire after 8 hours.

File uploads must be validated for file type by checking magic bytes (not just the file extension), size-limited to 50MB maximum, and stored in an isolated directory with no web-accessible path.

Audit logs must record every data access event (upload, job creation, report retrieval, PDF download) with timestamp, anonymized patient ID, and action type. Never log raw genomic data or file contents.

CORS must be restricted to the known frontend origin in production. In development, localhost:3000 is acceptable.

---

## Environment Variables — Complete Reference

All configuration must come from environment variables. No hardcoded values anywhere in the codebase.

- `QDRANT_URL` — Qdrant service URL. `http://localhost:6333` in development, `http://qdrant:6333` inside Docker Compose
- `REDIS_URL` — Redis connection string for Celery. `redis://localhost:6379` in development
- `OLLAMA_URL` — Ollama API base URL. `http://localhost:11434` in development
- `GEMMA_MODEL` — Ollama model tag. Default `gemma2:27b`
- `DATABASE_URL` — SQLAlchemy connection string. `sqlite:///./pharma_ai.db` for development, PostgreSQL URL for production
- `SECRET_KEY` — Long random string for JWT signing
- `UPLOAD_DIR` — Filesystem path for uploaded gene report files
- `REPORTS_DIR` — Filesystem path for generated PDF reports
- `NCBI_API_KEY` — Optional. Obtained from ncbi.nlm.nih.gov/account/. Raises ClinVar API rate limit from 3 to 10 req/sec
- `NEXT_PUBLIC_API_URL` — FastAPI base URL visible to the Next.js frontend. `http://localhost:8000` in development

---

## Build Order and Milestones

Build in this exact sequence. Each milestone is independently testable before proceeding.

### Milestone 1 — Infrastructure Verified

Docker Compose is running with all five services healthy: Qdrant (port 6333), Redis (port 6379), Ollama (port 11434), FastAPI skeleton (port 8000), Next.js placeholder (port 3000). Gemma 4 has been pulled via Ollama and responds to a test prompt via the Ollama REST API. Qdrant has an empty collection created and is accessible. This milestone is complete when a health check to each service returns a healthy response.

### Milestone 2 — Knowledge Base Indexed

PharmGKB and CPIC source files have been downloaded. At least 200 markdown knowledge base documents have been created in the correct frontmatter format. The indexing script has run successfully and the Qdrant collection contains at least 500 vector points. A test similarity search for "CYP2D6 codeine" returns relevant CPIC guideline text in the top 3 results.

### Milestone 3 — Parsing Pipeline Working

The preprocessing service correctly parses a real VCF file. The annotation service successfully annotates at least one rsID via the ClinVar API. The metabolizer status determination returns correct phenotype labels for a known test case — rs4244285 homozygous should produce "CYP2C19 Poor Metabolizer".

### Milestone 4 — End-to-End Report Generated Without Frontend

A complete analysis job is triggered by a direct API POST with a test VCF file. The Celery worker processes all pipeline stages. Gemma 4 generates a valid JSON report. The XGBoost classifier or its rule-based fallback produces a risk score. A PDF is created on disk. The status endpoint returns `status: "complete"` with the full GenomicReport object. Test with Postman or curl before building the frontend.

### Milestone 5 — Frontend Connected

The Next.js frontend successfully uploads a file, shows real-time progress updates, renders the complete results dashboard with all components, and triggers a PDF download. All TypeScript types match the API response shapes. Error states (failed job, network error) are handled gracefully.

### Milestone 6 — Security Layer

JWT authentication is implemented and all protected endpoints reject unauthenticated requests. File uploads are validated for type and size. Patient data in prompts is anonymized. Environment variables are loaded correctly in all environments. Audit logging writes to a log file.

### Milestone 7 — Production Ready

Docker Compose includes a production configuration with resource limits. The frontend is built with `next build`. The XGBoost model has been trained on at least 1,000 labeled samples. All error paths are handled and surfaced to the user with clear messages.

---

## Common Failure Points and How to Avoid Them

**Gemma 4 output is not valid JSON** — Always wrap JSON extraction in a try-catch. First attempt to parse the full response. If that fails, search for the first `{` and last `}` and parse the substring. If that also fails, log the raw output and return a graceful fallback response. Never crash the Celery job on LLM output parse failure.

**ClinVar API rate limiting** — Cache all ClinVar API responses in Redis with a 24-hour TTL. Never hit the same rsID twice in the same run or across runs.

**Qdrant search returns irrelevant results** — This happens when knowledge base documents are too long. Enforce a maximum chunk size of 400 tokens per Qdrant document point. Shorter, focused chunks retrieve more precisely than long documents.

**VCF files with non-standard chromosome notation** — Always strip the `chr` prefix from chromosome numbers before comparison. Some VCFs use `chr22`, others use `22`. Handle both GRCh37 and GRCh38 coordinate systems — the chromosomal positions for pharmacogenes differ between these genome builds.

**Celery job silently fails** — Always wrap the entire Celery task body in a top-level try-except. On any exception, log the full traceback and update the job status to "failed" with the error message. Without this, failed jobs appear stuck at the last progress percentage.

**Large VCF files cause memory issues** — Parse VCF files as a streaming iterator, never loading the full file into memory. Filter down to the 13 pharmacogene chromosomal regions as early as possible.

**ReportLab font issues in Docker** — ReportLab ships with its own built-in fonts. Only use Helvetica, Times-Roman, and Courier (all built-in) to avoid font file dependencies in the container.

---

## Testing Strategy

The canonical integration test case is a synthetic patient with CYP2D6 `*4/*4` (Poor Metabolizer), CYP2C19 `*2/*2` (Poor Metabolizer), and SLCO1B1 `*5/*5` (reduced function). This patient should: score HIGH risk overall (above 66), show HIGH risk for codeine, clopidogrel, and simvastatin, and the AI summary should contain specific dosing adjustment recommendations for each drug.

Use pytest for all backend service tests. Use Jest and React Testing Library for frontend component tests. End-to-end testing should use Playwright to simulate a full upload-to-PDF-download flow.

For the LLM service specifically, mock the Ollama API in unit tests and test both the happy path (valid JSON returned) and all failure paths (invalid JSON, connection timeout, empty response).

For the RAG service, write a test that verifies top-K retrieval scores are above 0.6 cosine similarity for known gene-drug query pairs after the knowledge base is indexed.

---

## Python Package Requirements (Complete List)

**FastAPI and web layer:** fastapi, uvicorn, python-multipart, aiofiles, httpx, python-jose (JWT), passlib (password hashing), slowapi (rate limiting)

**Celery and caching:** celery, redis

**Database:** sqlalchemy, alembic (migrations)

**Genomics:** biopython, pyvcf3, pysam

**ML and data:** torch, transformers, sentence-transformers, xgboost, scikit-learn, numpy, pandas, scipy

**RAG and vector DB:** qdrant-client, langchain, langchain-community, langchain-ollama

**PDF generation:** reportlab

**Utilities:** python-dotenv, cryptography (AES-256 file encryption), requests

---

## Frontend Package Requirements (Complete List)

**Core:** next (v14), react, react-dom, typescript, tailwindcss

**UI components:** @radix-ui/react-progress, @radix-ui/react-tabs, lucide-react, shadcn/ui

**Data and networking:** axios, react-dropzone

**Visualization:** recharts (for risk gauges and comparative bar charts)

**Utilities:** react-hot-toast (notifications), clsx, tailwind-merge

---

*This document is the single source of truth for all implementation decisions in the Pharmacogenomics AI Platform. Every technology choice, data source, API contract, schema definition, and architectural pattern described here was deliberate. Claude Code should follow this document precisely and refer back to it when making any implementation decision.*
