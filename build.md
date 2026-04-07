
Gemini said
Claude Code Implementation Master Plan
AI Drug Compatibility Report — Pharmacogenomics Platform
1. Project Context & Background 

1.1 What We Are Building 

An AI-powered pharmacogenomics platform that allows users to upload their raw DNA data (from 23andMe or AncestryDNA), input their current medications, and receive a personalized drug compatibility report in under 60 seconds.


The Problem: 2 out of 5 prescriptions fail because they are based on population averages rather than individual genetics.


The Opportunity: Pharmacogenomics is currently locked behind expensive labs ($500+) and doctor referrals.


The Solution: This platform makes science-backed genetic insights accessible, affordable, and instant.


One-Line Pitch: "Upload your DNA file. Enter your medications. Get a personalized report showing which drugs are safe, which are risky, and what alternatives exist — all powered by real pharmacogenomic science." 

1.2 Hackathon Context 

Criterion	Score	Reason
12-day feasibility	8/10	
LLM + RAG + file parsing — no simulation engine needed 

Scalability	9/10	
SaaS model, $29/report or $99/yr, B2B hospital sales path 

Wow factor	9.5/10	
Live upload → 60-second report stuns judges every time 

Market size	High	
$50B pharmacogenomics market, <1% consumer penetration 

Competition	Low	
Labs charge $500+. No consumer app exists 

2. System Architecture 

2.1 High-Level Architecture 

The system utilizes a three-layer stack:


Frontend (Next.js): Handles UI, file uploads, and PDF exports.


Backend API (FastAPI): Processes DNA files, queries RAG, and assembles JSON reports.


AI & Data Layer: Claude API for generation, pgvector for RAG, and PharmGKB for data.

2.2 Tech Stack 

Frontend: Next.js 14 (App Router), TypeScript, Tailwind CSS, Framer Motion.

Backend: FastAPI (Python 3.11), Pydantic v2.

Database/AI: PostgreSQL 15 + pgvector, Redis (Cache), Claude API (claude-sonnet).

Data Sources: PharmGKB (Genetic data), RxNorm API (Drug normalization).

3. Project Folder Structure 
+1

Claude Code must strictly follow this monorepo structure:

Plaintext
pharmgeno-ai/
|-- frontend/
|   |-- app/
|   |   |-- page.tsx               # Landing page
|   |   |-- upload/page.tsx        # Upload flow
|   |   |-- report/page.tsx        # Report display
|   |-- components/
|   |   |-- UploadZone.tsx         # DNA file upload
|   |   |-- MedicationInput.tsx    # Autocomplete entry
|   |   |-- ReportCard.tsx         # Drug compatibility card
|   |   |-- RiskBadge.tsx          # Green/Amber/Red status
|   |   |-- Disclaimer.tsx         # Medical disclaimer (Non-negotiable)
|-- backend/
|   |-- main.py                    # FastAPI entry
|   |-- core/
|   |   |-- dna_parser.py          # 23andMe parser
|   |   |-- rag_retriever.py       # pgvector search
|   |   |-- report_generator.py    # Claude integration
|   |-- db/
|   |   |-- seed_pharmgkb.py       # DB seeder script
|-- docker-compose.yml             # Postgres + Redis
4. Implementation Phases (12 Days) 

Phase 1: Foundation & Data Layer (Days 1–3) 


Setup: Init Next.js and FastAPI; configure Docker with pgvector.


Data Ingestion: Download PharmGKB TSVs and seed PostgreSQL.


DNA Parsing: Build dna_parser.py to handle 23andMe .txt files using streaming.


RAG Setup: Implement similarity search in pgvector using OpenAI embeddings.

Phase 2: AI Core & Report Engine (Days 4–6) 


Normalization: Integrate RxNorm API to standardize medication names.


Claude Integration: Build the report generator using the mandated system prompt (Section 5.2).


API Routing: Wire the /api/analyze endpoint to chain the full pipeline.

Phase 3: Frontend & UX (Days 7–9) 


Landing Page: Hero section with "Try Demo" and "Upload" CTAs.


Upload Flow: Build UploadZone and MedicationInput with autocompletion.


Report View: Render OverallScore, staggered DrugCards, and PDF export.

Phase 4: Polish & Deployment (Days 10–12) 


Optimization: Ensure sub-60-second processing using Redis and profiling.


Deployment: Vercel (Frontend) and Railway (Backend).


Demo Prep: Pitch deck and screen recording backup.

5. AI Configuration & Prompts 

5.2 Claude API System Prompt 

Important: Claude must respond with ONLY valid JSON.
Required Schema:

overall_risk_score: Integer 1-10.

summary: 2-3 sentence plain English.

drugs: List containing compatibility, score, gene_variants_involved, and alternatives.

gene_summary: List of phenotypes (e.g., "poor metabolizer").

5.3 API Settings 

Model: claude-sonnet-4-5

Temperature: 0 (for consistent JSON)

Max Tokens: 4096

6. Key Requirements & Risks 


Medical Disclaimer: Must be rendered at the TOP of the report page, yellow/amber background, non-dismissible.


Data Integrity: Use only provided PharmGKB context; do not hallucinate drug interactions.
+2


Performance: DNA files can be 1M+ lines; use streaming/chunked reading.
+1


Demo Mode: Must work without a user file by using sample-demo.txt.

11.1 Quick Start 
+1

docker-compose up -d

cd backend && pip install -r requirements.txt && python db/seed_pharmgkb.py

uvicorn main:app --reload

cd frontend && npm install && npm run dev