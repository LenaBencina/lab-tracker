from src.database import Database
from src.parsers.synlab_parser import SynlabParser
from src.parsers.zdl_parser import ZDLParser
from src.parsers.dcbled_parser import DCBledParser
from src.config import PDFS_DIR
import os
import logging
import colorlog

# Set up colored logging
logging.root.handlers = []
handler = colorlog.StreamHandler()
handler.setFormatter(
    colorlog.ColoredFormatter("%(log_color)s%(levelname)s:%(name)s:%(message)s")
)
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)

logger = logging.getLogger(__name__)

PARSERS_PER_LAB = {"synlab": SynlabParser, "dcbled": DCBledParser, "zdl": ZDLParser}


def parse_and_insert_per_lab(db: Database, lab_name: str):
    for file_name in os.listdir(PDFS_DIR / lab_name):
        file_path = PDFS_DIR / lab_name / file_name

        if db.report_exists(file_path.stem):
            continue

        try:
            logger.info(f"Processing file {file_path.stem}")
            parser = PARSERS_PER_LAB.get(lab_name)
            report, results = parser().parse_pdf(file_path)
            db.insert_full_report(report, results)
        except Exception as e:
            logger.exception(f"Failed to parse {file_path}: {e}")


def main():
    # initialize db
    db = Database("data/lab_tracker.db")
    db.execute_sql_script("src/delete_tables.sql")
    db.execute_sql_script("src/schema.sql")
    db.execute_sql_script("src/insert_labs.sql")

    # todo when multiple labs implemented: could list all subdirs in data/pdf instead of hardcoding/duplicating
    parse_and_insert_per_lab(db, "synlab")
    parse_and_insert_per_lab(db, "dcbled")
    parse_and_insert_per_lab(db, "zdl")


if __name__ == "__main__":
    main()
