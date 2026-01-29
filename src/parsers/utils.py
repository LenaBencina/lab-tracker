import re
from datetime import datetime, date


def normalize_unit(unit: str) -> str:
    UNIT_MAPPINGS = {
        "109/L": "10E9/L",
        "1012/L": "10E12/L",
        "1,73m2": "1.73m2",
        "1": "L/L",
        "ug/L": "μg/L",
        "ukat/L": "μkat/L",
        "umol/L": "μmol/L",
        "mlU/L": "mIU/L",
    }

    unit = unit.strip().replace("\n", "")
    return UNIT_MAPPINGS.get(unit, unit)


def parse_reference(
    reference: str, phase: str | None = None
) -> tuple[float | None, float | None]:
    # handle multi-phase references (e.g., hormone levels by menstrual cycle phase)
    if "faza" in reference.lower():
        if not phase:
            raise ValueError("Phase must be specified")
        pattern = rf"{re.escape(phase)}[^:]*:?\s*(\d+[.,]\d+)-(\d+[.,]\d+)"
        match = re.search(pattern, reference, re.IGNORECASE)
        if match:
            min_val = float(match.group(1).replace(",", "."))
            max_val = float(match.group(2).replace(",", "."))
            return min_val, max_val
        return None, None

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


def get_out_of_range(min_ref: float, max_ref: float, value: float | str) -> str:
    # handle string results like "<5" or ">90"
    if isinstance(value, str):
        value_str = value.strip().replace(",", ".")
        if value_str.startswith("<"):
            num = float(value_str[1:])
            if min_ref is not None and num <= min_ref:
                return "L"
            return None
        elif value_str.startswith(">"):
            num = float(value_str[1:])
            if max_ref is not None and num >= max_ref:
                return "H"
            return None
        else:
            value = float(value_str)  # convert to float and continue

    # float logic
    if min_ref is not None and max_ref is not None:
        if value < min_ref:
            return "L"
        elif value > max_ref:
            return "H"
        else:
            return None
    elif min_ref is None and max_ref is not None:
        if value >= max_ref:
            return "H"
        else:
            return None
    elif max_ref is None and min_ref is not None:
        if value <= min_ref:
            return "L"
        else:
            return None
    else:
        raise ValueError("Something went wrong when getting out of range values")


# todo: check date vs datetime
def extract_date_from_text(text: str, labels: list[str]) -> date | None:
    for label in labels:
        match = re.search(rf"{re.escape(label)}:\s*(\d{{2}}\.\d{{2}}\.\d{{4}})", text)
        if match:
            return datetime.strptime(match.group(1), "%d.%m.%Y").date()
    return None
