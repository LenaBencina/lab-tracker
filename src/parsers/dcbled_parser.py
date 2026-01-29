from pathlib import Path
import logging
import pdfplumber
import re

from src.parsers.utils import (
    parse_reference,
    normalize_unit,
    get_out_of_range,
    extract_date_from_text,
)
from src.models import Report, Test, TestResult

logger = logging.getLogger(__name__)


class DCBledParser:
    lab_name = "DC Bled"
    date_labels = ["Datum obravnave"]

    def extract_report_metadata(self, text: str, file_name: str) -> Report:
        collection_date = extract_date_from_text(text=text, labels=self.date_labels)
        if not collection_date:
            raise ValueError("Could not extract collection date")

        return Report(
            lab_name="DC Bled",
            report_number=None,
            collection_date=collection_date,
            file_name=file_name,
        )

    @staticmethod
    def extract_celiac_markers(results_text: str) -> list[TestResult]:
        """Extract iga ttg and total iga tests from text - special cases."""

        test_results = []

        # IgA tTG e.g. 5,8 (norm. pod 9)
        iga_ttg_match = re.search(
            r"IgA tTG:\s*(?P<value>\d+,?\d*)\s*\((?P<reference>[^)]+)\)", results_text
        )
        if iga_ttg_match:
            iga_ttg_value = iga_ttg_match.group("value").replace(",", ".")
            iga_ttg_ref = iga_ttg_match.group("reference")
            ref_match = re.search(r"pod\s*(\d+)", iga_ttg_ref)
            iga_ttg_ref_max = float(ref_match.group(1)) if ref_match else None
            iga_ttg_ref_min = None
            test = Test(name="IgA tTG", category="celiac markers")
            test_result = TestResult(
                test=test,
                reference_min=iga_ttg_ref_min,
                reference_max=iga_ttg_ref_max,
                unit="U/mL",
                result=iga_ttg_value,
                out_of_range=get_out_of_range(
                    iga_ttg_ref_min, iga_ttg_ref_max, iga_ttg_value
                ),
            )
            test_results.append(test_result)

        # cel. IgA e.g. 0,95; sometimes missing reference ranges
        cel_iga_match = re.search(
            r"cel\.\s*IgA\s*:?\s*(?P<value>\d+,?\d*)(?:\s*\((?P<reference>[^)]+)\))?",
            results_text,
        )
        if cel_iga_match:
            cel_iga_value = cel_iga_match.group("value").replace(",", ".")
            cel_iga_ref = cel_iga_match.group("reference")

            if cel_iga_ref:
                # parse from report
                cel_iga_ref_min, cel_iga_ref_max = parse_reference(
                    cel_iga_ref.replace(",", ".")
                )
            else:
                # default reference range
                cel_iga_ref_min, cel_iga_ref_max = 0.63, 4.84

            test = Test(name="total serum IgA", category="celiac markers")
            test_result = TestResult(
                test=test,
                reference_min=cel_iga_ref_min,
                reference_max=cel_iga_ref_max,
                unit="g/L",
                result=cel_iga_value,
                out_of_range=get_out_of_range(
                    cel_iga_ref_min, cel_iga_ref_max, cel_iga_value
                ),
            )
            test_results.append(test_result)
        return test_results

    @staticmethod
    def extract_results_text(full_text: str) -> str:
        """Extract current results, excluding historical entries."""

        start_marker = "Sporočam vam izvide laboratorijskih preiskav:"
        results_text = full_text.split(start_marker)[1]  # everything after the string

        # remove historical entries (lines starting with dates)
        end_match = re.search(r"\d{2}\.\d{2}\.\d{4}:", results_text)
        if end_match:
            results_text = results_text[: end_match.start()]

        return results_text.replace("\n", " ")

    @staticmethod
    def extract_test_result(m: re.Match) -> TestResult:
        test = Test(name=m.group("name"), category=None)
        min_ref, max_ref = parse_reference(m.group("reference"))
        value_str = m.group("value").replace(",", ".")
        return TestResult(
            test=test,
            unit=normalize_unit(m.group("unit")),
            result=value_str,
            reference_min=min_ref,
            reference_max=max_ref,
            out_of_range=get_out_of_range(min_ref, max_ref, float(value_str)),
        )

    def parse_pdf(self, file_path: Path) -> tuple[Report, list[TestResult]]:
        with pdfplumber.open(file_path) as pdf:
            text = pdf.pages[0].extract_text()

        # extract report metadata from first page
        report = self.extract_report_metadata(text, file_path.stem)

        pattern = re.compile(
            r"(?P<name>[a-žA-Ž][a-žA-Ž0-9\s\-]+?)\s+"  # starts with letter, then letters/digits/spaces/hyphens (non-greedy)
            r"(?P<value>\d+[,.]?\d*)\s+"  # whitespace separator
            r"(?P<unit>[^(]+?)\s*"  # number with optional comma or dot decimal
            r"\((?P<reference>[^)]+)\)"
        )  # reference in parentheses

        results_text = self.extract_results_text(text)
        all_results = [
            self.extract_test_result(m) for m in pattern.finditer(results_text)
        ]
        all_results.extend(self.extract_celiac_markers(results_text))

        logger.info("Parsed %d test results", len(all_results))
        return report, all_results
