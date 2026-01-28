import sqlite3
import logging

from src.models import Report, Test, TestResult

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def execute_sql_script(self, file_path):
        with open(file_path, "r") as sql_file:
            sql_script = sql_file.read()

        with self.connect() as conn:
            conn.executescript(sql_script)
            conn.commit()

    def report_exists(self, file_name: str) -> bool:
        with self.connect() as conn:
            cursor = conn.execute(
                "SELECT 1 FROM report WHERE file_name = ?", (file_name,)
            )
            return cursor.fetchone() is not None

    def insert_full_report(self, report: Report, all_results: list[TestResult]):
        with self.connect() as conn:
            try:
                report_id = self._insert_report(conn, report)
                for result in all_results:
                    test_name = self._get_or_insert_test(conn, result.test)
                    self._insert_test_result(conn, result, report_id, test_name)

                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to insert report {report_id}: {e}")
                raise

    @staticmethod
    def _insert_report(conn, report: Report) -> int:
        cursor = conn.execute(
            "INSERT INTO report (lab_name, report_number, file_name, collection_date) VALUES (?, ?, ?, ?)",
            (
                report.lab_name,
                report.report_number,
                report.file_name,
                str(report.collection_date),
            ),
        )
        report_id = cursor.lastrowid
        return report_id

    @staticmethod
    def _get_or_insert_test(conn, test: Test) -> str:
        # without reporting the change this is enough
        # conn.execute(
        #     "INSERT OR IGNORE INTO test (name, category) VALUES (?, ?)",
        #     (test.name, test.category),
        # )
        cursor = conn.execute("SELECT 1 FROM test WHERE name = ?", (test.name,))
        if cursor.fetchone() is None:
            conn.execute(
                "INSERT INTO test (name, category) VALUES (?, ?)",
                (test.name, test.category),
            )
            logger.info(f"New test inserted: {test.name}")
        return test.name

    @staticmethod
    def _insert_test_result(conn, result: TestResult, report_id, test_name):
        conn.execute(
            """INSERT INTO test_result (
                    report_id,
                    test_name,
                    reference_min,
                    reference_max,
                    unit,
                    result,
                    out_of_range
               ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report_id,
                test_name,
                result.reference_min,
                result.reference_max,
                result.unit,
                result.result,
                result.out_of_range,
            ),
        )
        return
