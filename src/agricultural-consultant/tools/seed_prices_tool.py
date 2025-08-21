import os 
from langchain.tools import tool

@tool(description="Verilen ürün için tohum fiyatını döner.")
def get_seed_price_tool(crop_name: str) -> str:
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "data", "seed_prices.txt")

        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                if ":" in line:
                    name, price = line.strip().split(":")
                    if name.strip().lower() == crop_name.lower():
                        return f"{name.strip().capitalize()} tohumu fiyatı: {price.strip()}"
        return "Aradığınız bitkinin tohum fiyatı veri tabanımızda bulunamadı."
    except FileNotFoundError:
        return "Tohum fiyat dosyası bulunamadı."
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}"