# PharmGeno AI

AI-powered pharmacogenomics platform for personalized drug compatibility analysis.

## Overview

Upload your 23andMe or AncestryDNA raw data, enter your medications, and receive a personalized drug compatibility report in under 60 seconds.

## Features

- 🧬 **DNA Parsing**: Supports 23andMe and AncestryDNA raw data files
- 💊 **Drug Search**: RxNorm-powered medication autocomplete
- 🤖 **AI Analysis**: Claude-powered pharmacogenomic report generation
- 📊 **Risk Scoring**: Clear compatibility scores (1-10) with explanations
- 🔒 **Privacy First**: Your data is processed locally and never stored

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Python 3.11, Pydantic v2
- **Database**: PostgreSQL 15 + pgvector, Redis
- **AI**: Claude API (claude-sonnet-4-5)
- **Data Sources**: PharmGKB, RxNorm API

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Setup

1. **Start databases**:
   ```bash
   docker-compose up -d
   ```

2. **Setup backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   cp .env.example .env  # Add your ANTHROPIC_API_KEY
   python db/seed_pharmgkb.py
   uvicorn main:app --reload
   ```

3. **Setup frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Open**: http://localhost:3000

## Project Structure

```
pharmgeno-ai/
├── frontend/
│   ├── app/
│   │   ├── page.tsx           # Landing page
│   │   ├── upload/page.tsx    # Upload flow
│   │   └── report/page.tsx    # Report display
│   └── components/
│       ├── UploadZone.tsx     # DNA file upload
│       ├── MedicationInput.tsx # Autocomplete entry
│       ├── ReportCard.tsx     # Drug compatibility card
│       ├── RiskBadge.tsx      # Green/Amber/Red status
│       └── Disclaimer.tsx     # Medical disclaimer
├── backend/
│   ├── main.py                # FastAPI entry
│   ├── core/
│   │   ├── dna_parser.py      # 23andMe parser
│   │   ├── rag_retriever.py   # PharmGKB RAG
│   │   ├── report_generator.py # Claude integration
│   │   └── rxnorm.py          # Drug normalization
│   └── db/
│       └── seed_pharmgkb.py   # Database seeder
└── docker-compose.yml         # Postgres + Redis
```

## API Endpoints

- `POST /api/analyze` - Analyze DNA file with medications
- `POST /api/analyze-demo` - Demo analysis with sample data
- `GET /api/medications/search?q=` - Search medications

## Environment Variables

### Backend (.env)
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=pharmgeno
POSTGRES_PASSWORD=pharmgeno_secret
POSTGRES_DB=pharmgeno_db
ANTHROPIC_API_KEY=your_api_key
```

## Medical Disclaimer

⚠️ This platform provides educational information only and is NOT medical advice. Always consult your healthcare provider before making medication decisions.

## License

MIT
