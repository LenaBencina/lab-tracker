import pdfplumber
import re
import logging
from datetime import datetime
from pathlib import Path

from src.config import SYNLAB_PDF_PASSWORD
from src.models import Report, TestResult, Test

logger = logging.getLogger(__name__)


def parse_reference(reference: str) -> tuple[float | None, float | None]:
    if "-" in reference:
        min_ref, max_ref = reference.split(" - ")
        return float(min_ref), float(max_ref)
    elif "<" in reference:
        _, max_ref = reference.split("<")
        return None, float(max_ref)
    elif ">" in reference:
        _, min_ref = reference.split(">")
        return float(min_ref), None
    else:
        raise ValueError("New reference type; not implemented yet")


def parse_table(table: list) -> list[TestResult]:
    header_mixed = table[0][0]
    # category, header_str = header_mixed.split('\n')

    lines = header_mixed.split("\n")
    category = lines[0]
    header_str = next(line for line in lines if line.startswith("Preiskava"))

    columns = re.split(r"\s+(?=[A-Z])", header_str)
    # todo: columns check
    print(columns)

    rows = table[1:]

    tests = []
    results = []
    for row in rows:
        # skip weird rows
        if row[3] is None:
            # print(f"Skipping row {row}")
            logger.info(f"Skipping row: {row}")
            continue
        min_ref, max_ref = parse_reference(row[1])
        test = Test(name=row[0].replace("\n", ""), category=category)
        result = TestResult(
            test=test,
            reference_min=min_ref,
            reference_max=max_ref,
            unit=row[2],
            result=row[3],
            out_of_range=row[4],
        )
        tests.append(test)
        results.append(result)
        # print(test)
    return results


def parse_report_metadata(text: str, file_name: str) -> Report:
    # collection date
    match = re.search(r"Čas odvzema:\s*(\d{2}\.\d{2}\.\d{4})", text)
    if match:
        date_str = match.group(1)
        collection_date = datetime.strptime(date_str, "%d.%m.%Y").date()

    # lab number (report number)
    match = re.search(r"Laboratorijska št\.:\s*(\d+)", text)
    report_number = int(match.group(1)) if match else None

    return Report(
        lab_name="Synevo adria lab",
        report_number=report_number,
        collection_date=collection_date,
        file_name=file_name,
    )


def parse_pdf(file_path: Path) -> tuple[Report, list[TestResult]]:
    with pdfplumber.open(file_path, password=SYNLAB_PDF_PASSWORD) as pdf:
        text = pdf.pages[0].extract_text()  # metadata from first page
        report = parse_report_metadata(text, file_path.stem)
        all_results = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                results = parse_table(table)
                all_results.extend(results)
    return report, all_results
