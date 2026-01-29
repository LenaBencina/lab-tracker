import pdfplumber
import re
import logging
from datetime import datetime
from pathlib import Path

from src.parsers.utils import parse_reference, normalize_unit, get_out_of_range
from src.config import SYNLAB_PDF_PASSWORD
from src.models import Report, TestResult, Test

logger = logging.getLogger(__name__)


def extract_test_results_from_table(table: list) -> list[TestResult]:
    header_mixed = table[0][0]
    lines = header_mixed.split("\n")
    category = lines[0]

    # check that table columns are as to be expected
    header_str = next(line for line in lines if line.startswith("Preiskava"))
    columns = re.split(r"\s+(?=[A-Z])", header_str)
    if columns != [
        "Preiskava",
        "Orientacijske referenčne vrednosti",
        "Enota",
        "Rezultat",
    ]:
        raise ValueError("Try to parse a non-valid table")

    results = []
    for row in table[1:]:
        name, reference, unit, value, out_of_range_flag = row[0:5]
        # name, out_of_range_flag, value, reference, unit = row[0:5]

        if value is None or value == "":
            logger.info(f"Detected useless row without a value: {row}")
            continue

        test = Test(name=name.replace("\n", ""), category=category)

        min_ref, max_ref = parse_reference(
            reference, phase="Folik"
        )  # todo: make this configurable when/if needed

        # calculate out of range to double check
        out_of_range_calc = get_out_of_range(min_ref, max_ref, value)
        out_of_range_reported = out_of_range_flag or None
        if out_of_range_calc != out_of_range_reported:
            raise ValueError("Out of range mismatch. Check manually!")

        result = TestResult(
            test=test,
            reference_min=min_ref,
            reference_max=max_ref,
            unit=normalize_unit(unit),
            result=value,
            out_of_range=out_of_range_reported,
        )
        results.append(result)
    return results


def get_collection_date(label: str, text: str) -> datetime | None:
    # match = re.search(rf"{re.escape(label)}:\s*(\d{2}\.\d{2}\.\d{4})", text)
    match = re.search(rf"{re.escape(label)}:\s*(\d{{2}}\.\d{{2}}\.\d{{4}})", text)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    return None


def extract_report_metadata(text: str, file_name: str) -> Report:
    # get collection date
    collection_date = get_collection_date(label="Čas odvzema", text=text)
    if not collection_date:
        collection_date = get_collection_date(label="Čas sprejema", text=text)
    if not collection_date:
        raise ValueError("Could not extract collection date")

    # get lab number (report number)
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
        # extract report metadata from first page
        text = pdf.pages[0].extract_text()
        report = extract_report_metadata(text, file_path.stem)

        # parse test results from all pages as tables
        all_results = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                results = extract_test_results_from_table(table)
                all_results.extend(results)

    return report, all_results
