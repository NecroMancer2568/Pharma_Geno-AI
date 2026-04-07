import asyncio
import os
from dotenv import load_dotenv
from core.dna_parser import DNAParser
from core.rag_retriever import RAGRetriever
from core.report_generator import ReportGenerator

async def main():
    load_dotenv()
    
    dna_parser = DNAParser()
    rag_retriever = RAGRetriever()
    report_generator = ReportGenerator()
    
    with open('sample-demo.txt', 'r') as f:
        dna_text = f.read()
    
    medications = ["Lisinopril", "Metformin"]
    
    try:
        genetic_variants = await dna_parser.parse(dna_text)
        print("DNA Parsed successfully.")
    except Exception as e:
        print(f"DNA Parse error: {e}")
        return
        
    try:
        pharmgkb_context = await rag_retriever.get_relevant_data(
            genetic_variants=genetic_variants,
            medications=medications
        )
        print("RAG Context retrieved:")
        print(pharmgkb_context)
    except Exception as e:
        print(f"RAG error: {e}")
        import traceback
        traceback.print_exc()
        return
        
    try:
        report = await report_generator.generate(
            genetic_variants=genetic_variants,
            medications=medications,
            pharmgkb_context=pharmgkb_context
        )
        print("Report generated successfully:")
        print(report)
    except Exception as e:
        print(f"Report Generation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
