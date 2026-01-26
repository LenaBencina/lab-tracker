from src.database import Database
from src.parsers.synlab_parser import parse_pdf
from src.config import PDFS_DIR
import os


def main():
    # initialize db
    db = Database("data/lab_tracker.db")
    db.execute_sql_script("src/delete_tables.sql")
    db.execute_sql_script("src/schema.sql")
    db.execute_sql_script("src/insert_labs.sql")

    for file_name in os.listdir(PDFS_DIR):
        file_path = PDFS_DIR / file_name
        report, results = parse_pdf(file_path)
        db.insert_full_report(report, results)


if __name__ == "__main__":
    main()
