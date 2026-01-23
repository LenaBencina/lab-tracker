from pathlib import Path
import os
from dotenv import load_dotenv
import logging

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PDFS_DIR = DATA_DIR / "pdfs"
DB_PATH = DATA_DIR / "lab_tracker.db"

load_dotenv(PROJECT_ROOT / ".env")
SYNLAB_PDF_PASSWORD = os.getenv("SYNLAB_PDF_PASSWORD")

logging.basicConfig(level=logging.INFO)
