from abc import ABC, abstractmethod
import pdfplumber
import re
import logging
from pathlib import Path
from dataclasses import dataclass

from src.parsers.utils import (
    parse_reference,
    normalize_unit,
    get_out_of_range,
    extract_date_from_text,
)
from src.models import Report, TestResult, Test

logger = logging.getLogger(__name__)


@dataclass
class ColumnMap:
    name: int
    reference: int
    unit: int
    value: int
    out_of_range: int

    def extract_from_row(self, row):
        return (
            row[self.name],
            row[self.reference],
            row[self.unit],
            row[self.value],
            row[self.out_of_range],
        )


class BaseLabParser(ABC):
    @property
    @abstractmethod
    def lab_name(self) -> str: ...

    @property
    @abstractmethod
    def table_columns(self) -> str: ...

    @property
    @abstractmethod
    def column_map(self) -> ColumnMap: ...

    @property
    @abstractmethod
    def date_labels(self) -> list[str]: ...

    @property
    def pdf_password(self) -> str | None:
        """Override if PDF is password protected."""
        return None

    def extract_test_results_from_table(self, table: list) -> list[TestResult]:
        """Main method to extract tests, results, references and out of range flags from a table."""
        header_mixed = table[0][0]
        lines = header_mixed.split("\n")
        category = lines[0]

        # check that table columns are as to be expected
        header_str = next(line for line in lines if line.startswith("Preiskava"))
        columns = re.split(r"\s+(?=[A-Z])", header_str)
        if columns != self.table_columns:
            raise ValueError("Try to parse a non-valid table")

        results = []
        for row in table[1:]:
            name, reference, unit, value, out_of_range_flag = (
                self.column_map.extract_from_row(row)
            )

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
                raise ValueError("Out of range mismatch; check manually")

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

    def extract_report_metadata(self, text: str, file_name: str) -> Report:
        # get collection date
        collection_date = extract_date_from_text(text=text, labels=self.date_labels)
        if not collection_date:
            raise ValueError("Could not extract collection date")

        # get lab number (report number)
        match = re.search(r"Laboratorijska št\.:\s*(\d+)", text)
        report_number = int(match.group(1)) if match else None

        return Report(
            lab_name=self.lab_name,
            report_number=report_number,
            collection_date=collection_date,
            file_name=file_name,
        )

    def parse_pdf(self, file_path: Path) -> tuple[Report, list[TestResult]]:
        with pdfplumber.open(file_path, password=self.pdf_password) as pdf:
            # extract report metadata from first page
            text = pdf.pages[0].extract_text()
            report = self.extract_report_metadata(text, file_path.stem)

            # parse test results from all pages as tables
            all_results = []
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    results = self.extract_test_results_from_table(table)
                    all_results.extend(results)

        return report, all_results
