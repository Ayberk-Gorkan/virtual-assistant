import pandas as pd
import os
from langchain.tools import tool

@tool(description="Verilen ürün için son 3 yılın pazar fiyatlarını döner.")
def get_market_price_tool(product_name):
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "data", "market_prices.xls")

        df = pd.read_excel(file_path, header=3)
        df.columns = df.columns.astype(str)
        df.rename(columns={df.columns[0]: "Ürün"}, inplace=True)

        rows = df[df["Ürün"].str.lower().str.contains(product_name.lower(), na=False)]

        if rows.empty:
            return f"{product_name} için fiyat bilgisi bulunamadı."

        for _, row in rows.iterrows():
            fiyatlar = row[["2022", "2023", "2024*"]]
            if not fiyatlar.isin(["-"]).all():
                fiyat_output = "\n".join([
                    f"{yıl[:4]}: {float(fiyatlar[yıl]):.2f} TL/kg"
                    for yıl in fiyatlar.index if fiyatlar[yıl] != "-"
                ])
                return f"{row['Ürün']} için son 3 yılın pazar fiyatları:\n{fiyat_output}"

        return f"{product_name} için 2022–2024 yılları arasında geçerli veri bulunamadı."

    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"
