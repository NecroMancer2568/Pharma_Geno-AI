"""
PharmGKB Database Seeder
Seeds PostgreSQL with pharmacogenomic data for RAG retrieval.
"""

import asyncio
import os
import sys

try:
    import asyncpg
    from pgvector.asyncpg import register_vector
except ImportError:
    print("Please install dependencies: pip install asyncpg pgvector")
    sys.exit(1)


# PharmGKB reference data for seeding
PHARMGKB_DATA = [
    {
        "gene": "CYP2D6",
        "rsid": "rs3892097",
        "drugs": ["codeine", "tramadol", "oxycodone", "tamoxifen", "fluoxetine"],
        "clinical_annotation": "CYP2D6*4 allele results in no enzyme function. Poor metabolizers have reduced conversion of codeine to morphine.",
        "evidence_level": "1A",
        "phenotype": "Poor Metabolizer"
    },
    {
        "gene": "CYP2C19",
        "rsid": "rs4244285",
        "drugs": ["clopidogrel", "omeprazole", "escitalopram", "voriconazole"],
        "clinical_annotation": "CYP2C19*2 allele results in no enzyme function. Affects clopidogrel activation and PPI metabolism.",
        "evidence_level": "1A",
        "phenotype": "Poor Metabolizer"
    },
    {
        "gene": "CYP2C19",
        "rsid": "rs12248560",
        "drugs": ["clopidogrel", "omeprazole", "escitalopram"],
        "clinical_annotation": "CYP2C19*17 allele results in increased enzyme function. Ultrarapid metabolizers may need dose adjustments.",
        "evidence_level": "1A",
        "phenotype": "Ultrarapid Metabolizer"
    },
    {
        "gene": "CYP2C9",
        "rsid": "rs1799853",
        "drugs": ["warfarin", "phenytoin", "celecoxib", "ibuprofen"],
        "clinical_annotation": "CYP2C9*2 allele results in decreased enzyme function. Reduced warfarin clearance.",
        "evidence_level": "1A",
        "phenotype": "Intermediate Metabolizer"
    },
    {
        "gene": "VKORC1",
        "rsid": "rs9923231",
        "drugs": ["warfarin", "acenocoumarol"],
        "clinical_annotation": "VKORC1 -1639G>A variant associated with increased warfarin sensitivity.",
        "evidence_level": "1A",
        "phenotype": "High Warfarin Sensitivity"
    },
    {
        "gene": "SLCO1B1",
        "rsid": "rs4149056",
        "drugs": ["simvastatin", "atorvastatin", "rosuvastatin", "pravastatin"],
        "clinical_annotation": "SLCO1B1 521T>C associated with increased risk of statin-induced myopathy.",
        "evidence_level": "1A",
        "phenotype": "Increased Myopathy Risk"
    },
    {
        "gene": "TPMT",
        "rsid": "rs1800460",
        "drugs": ["azathioprine", "mercaptopurine", "thioguanine"],
        "clinical_annotation": "TPMT*3A allele results in low enzyme activity. High risk of myelosuppression.",
        "evidence_level": "1A",
        "phenotype": "Poor Metabolizer"
    },
    {
        "gene": "DPYD",
        "rsid": "rs3918290",
        "drugs": ["fluorouracil", "capecitabine"],
        "clinical_annotation": "DPYD*2A allele results in no enzyme function. Contraindicated for fluoropyrimidines.",
        "evidence_level": "1A",
        "phenotype": "Poor Metabolizer - Contraindicated"
    },
    {
        "gene": "OPRM1",
        "rsid": "rs1799971",
        "drugs": ["morphine", "fentanyl", "methadone", "naltrexone"],
        "clinical_annotation": "OPRM1 A118G variant associated with reduced opioid receptor binding.",
        "evidence_level": "2A",
        "phenotype": "Reduced Opioid Response"
    },
    {
        "gene": "COMT",
        "rsid": "rs4680",
        "drugs": ["morphine", "codeine", "tramadol"],
        "clinical_annotation": "COMT Val158Met variant affects pain sensitivity and opioid requirements.",
        "evidence_level": "2A",
        "phenotype": "Variable Pain Sensitivity"
    },
    {
        "gene": "MTHFR",
        "rsid": "rs1801133",
        "drugs": ["methotrexate", "folic_acid"],
        "clinical_annotation": "MTHFR C677T variant associated with reduced folate metabolism.",
        "evidence_level": "2A",
        "phenotype": "Reduced Folate Metabolism"
    },
]


async def create_tables(conn):
    """Create database tables for PharmGKB data."""
    
    # Enable pgvector extension
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Create pharmgkb_annotations table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS pharmgkb_annotations (
            id SERIAL PRIMARY KEY,
            gene VARCHAR(50) NOT NULL,
            rsid VARCHAR(50) NOT NULL,
            drugs TEXT[] NOT NULL,
            clinical_annotation TEXT NOT NULL,
            evidence_level VARCHAR(10),
            phenotype VARCHAR(100),
            embedding vector(1536),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index on gene and rsid
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_pharmgkb_gene ON pharmgkb_annotations(gene)
    """)
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_pharmgkb_rsid ON pharmgkb_annotations(rsid)
    """)
    
    # Create index for vector similarity search (if embeddings are added)
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_pharmgkb_embedding 
        ON pharmgkb_annotations 
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 10)
    """)
    
    print("✓ Tables created successfully")


async def seed_data(conn):
    """Seed the database with PharmGKB reference data."""
    
    # Check if data already exists
    count = await conn.fetchval("SELECT COUNT(*) FROM pharmgkb_annotations")
    if count > 0:
        print(f"Database already contains {count} records. Skipping seed.")
        return
    
    # Insert data
    for entry in PHARMGKB_DATA:
        await conn.execute("""
            INSERT INTO pharmgkb_annotations (gene, rsid, drugs, clinical_annotation, evidence_level, phenotype)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 
            entry["gene"],
            entry["rsid"],
            entry["drugs"],
            entry["clinical_annotation"],
            entry["evidence_level"],
            entry["phenotype"]
        )
    
    print(f"✓ Seeded {len(PHARMGKB_DATA)} PharmGKB annotations")


async def main():
    """Main function to set up and seed the database."""
    
    print("PharmGKB Database Seeder")
    print("=" * 40)
    
    # Database connection parameters
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    user = os.getenv("POSTGRES_USER", "pharmgeno")
    password = os.getenv("POSTGRES_PASSWORD", "pharmgeno_secret")
    database = os.getenv("POSTGRES_DB", "pharmgeno_db")
    
    print(f"Connecting to PostgreSQL at {host}:{port}...")
    
    try:
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        await register_vector(conn)
        print("✓ Connected to PostgreSQL with pgvector")
        
        await create_tables(conn)
        await seed_data(conn)
        
        await conn.close()
        print("\n✓ Database setup complete!")
        
    except asyncpg.InvalidCatalogNameError:
        print(f"Database '{database}' does not exist. Please create it first.")
        print("Run: docker-compose up -d")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
