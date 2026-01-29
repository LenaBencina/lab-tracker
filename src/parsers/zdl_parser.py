from src.parsers.base_parser import ColumnMap, BaseLabParser


class ZDLParser(BaseLabParser):
    lab_name = "Zdravstveni dom Ljubljana"
    table_columns = ["Preiskava", "Rezultat", "Orient.ref.vred.", "Enota"]
    # out of range column does not have a header
    column_map = ColumnMap(
        name=0, reference=3, unit=4, value=2, out_of_range=1
    )  # shifted
    date_labels = ["Čas sprejema"]
