from src.database import Database
from src.parsers.synlab_parser import parse_pdf as parse_synlab_pdf
from src.parsers.dcbled_parser import parse_pdf as parse_dcbled_pdf
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

PARSERS_PER_LAB = {"synlab": parse_synlab_pdf, "dcbled": parse_dcbled_pdf}


def parse_and_insert_per_lab(db: Database, lab_name: str):
    for file_name in os.listdir(PDFS_DIR / lab_name):
        file_path = PDFS_DIR / lab_name / file_name

        if db.report_exists(file_path.stem):
            continue

        try:
            report, results = PARSERS_PER_LAB.get(lab_name)(file_path)
            db.insert_full_report(report, results)
        except Exception as e:
            logger.exception(f"Failed to parse {file_path}: {e}")


def main():
    # initialize db
    db = Database("data/lab_tracker.db")
    # db.execute_sql_script("src/delete_tables.sql")
    db.execute_sql_script("src/schema.sql")
    db.execute_sql_script("src/insert_labs.sql")

    # todo when multiple labs implemented: could list all subdirs in data/pdf instead of hardcoding/duplicating
    parse_and_insert_per_lab(db, "synlab")
    # parse_and_insert_per_lab(db, "dcbled")


if __name__ == "__main__":
    main()
