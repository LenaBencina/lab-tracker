from src.database import Database
from src.parsers.synlab_parser import parse_pdf
from src.config import PDFS_DIR


def main():
    # initialize db
    db = Database("data/lab_tracker.db")
    db.execute_sql_script("src/schema.sql")
    db.execute_sql_script("src/insert_labs.sql")

    # import a pdf
    file_name = "L_Izvid_6459599_125716978_1_2_0_1.PDF"
    file_name = "L_Izvid_6459603_125417967_1_2_0_0.PDF"
    # file_name = "L_Izvid_6459613_125915074_1_2_0_0.PDF"

    file_path = PDFS_DIR / file_name
    report, all_tests, all_results = parse_pdf(file_path)

    # save to database
    db.insert_report(report)


if __name__ == "__main__":
    main()
