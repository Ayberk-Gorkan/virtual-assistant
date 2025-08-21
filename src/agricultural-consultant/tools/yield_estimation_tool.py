import pandas as pd
import os
from openpyxl.utils import column_index_from_string
from langchain.tools import tool

@tool(description="Verilen ürün için 2022-2024 yılları arasındaki verim bilgilerini döner.")
def get_yield_data_tool(product_name: str) -> str:
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "data", "yield_data.xls")

        df = pd.read_excel(file_path, sheet_name=0, header=None)

        start_row = df[df.apply(lambda row: row.astype(str).str.contains("Verim", case=False).any(), axis=1)].index[0] + 1

        header_row_index = start_row - 1
        year_col_idx = df.iloc[header_row_index].astype(str).str.contains(r'\bYıl\b', case=False).idxmax()

        product_map = {
            "buğday": "C",
            "arpa": "G",
            "mısır": "J",
            "çeltik": "K",
            "çavdar": "L",
            "yulaf": "M",
            "kaplıca": "N",
            "darı": "O",
            "kuşyemi": "P",
            "mahlut": "Q",
            "tritikale": "R",
            "sorgum": "S",
            "karabuğday": "T"
        }

        col_letter = product_map.get(product_name.lower())
        if not col_letter:
            return f"{product_name} için desteklenen verim bilgisi yok."

        col_idx = column_index_from_string(col_letter) - 1

        year_series = df.iloc[start_row:start_row+50, year_col_idx].astype(str).str.extract(r'(\d{4})')[0]
        value_series = df.iloc[start_row:start_row+50, col_idx]

        valid = year_series.notna()
        years = year_series[valid].astype(int)
        values = value_series[valid].reset_index(drop=True)

        result = []
        for year, value in zip(years, values):
            if year in [2022, 2023, 2024] and pd.notna(value):
                result.append(f"{year}: {value} kg/da")

        return "\n".join(result) if result else f"{product_name} için 2022-2024 verisi bulunamadı."

    except Exception as e:
        return f"Bir hata oluştu: {e}"
