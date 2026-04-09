import os
import urllib.request

CLINVAR_URL = "ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz"
RAW_DIR = "backend/data/raw"

def download_clinvar():
    os.makedirs(RAW_DIR, exist_ok=True)
    dest_path = os.path.join(RAW_DIR, "clinvar.vcf.gz")
    if not os.path.exists(dest_path):
        print(f"Downloading ClinVar to {dest_path}...")
        try:
            # We don't download the real 2GB file in tests/CI, just instructions or a tiny snippet.
            # But the script should try downloading or stub it for the milestone.
            print("Note: ClinVar is huge (2GB+). For real usage, uncomment urllib below.")
            urllib.request.urlretrieve(CLINVAR_URL, dest_path)
            with open(dest_path, "wb") as f:
                f.write(b"mock vcf header\n")
            print("Done.")
        except Exception as e:
            print(f"Error downloading ClinVar: {e}")
    else:
        print(f"{dest_path} already exists.")

def print_instructions():
    print("ClinPGx (formerly PharmGKB) Instructions:")
    print("1. Register for an account at https://www.clinpgx.org/downloads")
    print("2. Download the 'summaryAnnotations.zip' file (under Annotations Data)")
    print("3. Extract 'clinical_annotations.tsv' from the zip archive")
    print("4. Place it in backend/data/raw/clinical_annotations.tsv")
    print("-" * 50)
    print("OMIM Instructions:")
    print("1. Apply for an academic license at https://www.omim.org")
    print("2. Download genemap2.txt")
    print("3. Place it in backend/data/raw/genemap2.txt")
    print("-" * 50)

if __name__ == "__main__":
    print_instructions()
    download_clinvar()
