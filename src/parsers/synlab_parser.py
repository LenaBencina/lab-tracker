from src.parsers.base_parser import ColumnMap, BaseLabParser
from src.config import SYNLAB_PDF_PASSWORD


class SynlabParser(BaseLabParser):
    lab_name = "Synevo adria lab"
    table_columns = [
        "Preiskava",
        "Orientacijske referenčne vrednosti",
        "Enota",
        "Rezultat",
    ]
    # out of range column does not have a header
    column_map = ColumnMap(name=0, reference=1, unit=2, value=3, out_of_range=4)
    date_labels = ["Čas odvzema", "Čas sprejema"]
    pdf_password = SYNLAB_PDF_PASSWORD
