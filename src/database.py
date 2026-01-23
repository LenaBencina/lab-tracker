import sqlite3

from src.models import Report, Test, TestResult


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def execute_sql_script(self, file_path):
        with open(file_path, "r") as sql_file:
            sql_script = sql_file.read()

        with self._connect() as conn:
            conn.executescript(sql_script)
            conn.commit()

    def insert_report(self, report: Report) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO report (lab_name, report_number, file_path, collection_date) VALUES (?, ?, ?, ?)",
                (
                    report.lab_name,
                    report.report_number,
                    report.file_path,
                    str(report.collection_date),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def insert_test(self, test: Test):
        # todo
        return

    def insert_test_result(self, test_result: TestResult):
        # todo
        return
