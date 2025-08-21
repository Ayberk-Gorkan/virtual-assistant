# Dockerfile
# Python 3.10 imajýný temel al
FROM python:3.10-slim

# Çalýþma dizinini ayarla
WORKDIR /app

# Gereksinimleri (requirements.txt) kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarýný kopyala
COPY . .

# Sanal asistaný çalýþtýran ana dosyayý belirle
CMD ["python", "agri_assistant.py"]
