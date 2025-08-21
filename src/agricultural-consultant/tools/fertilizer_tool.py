import os
from langchain.tools import tool

@tool(description="Verilen bitki için önerilen gübre türünü döner.")
def get_fertilizer_tool(plant_name: str) -> str:
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_dir, "data", "fertilizer_needs.md")

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        recommendation = ""
        found = False

        for line in lines:
            if line.strip().lower() == f"## {plant_name.lower()}":
                found = True
                continue
            if found:
                if line.startswith("## "):
                    break
                recommendation += line.strip() + " "
        
        return recommendation.strip() if recommendation else "Veri bulunamadı."
    except FileNotFoundError:
        return "Veri dosyası bulunamadı."
