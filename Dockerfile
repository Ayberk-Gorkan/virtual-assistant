# Dockerfile
# Python 3.10 imaj�n� temel al
FROM python:3.10-slim

# �al��ma dizinini ayarla
WORKDIR /app

# Gereksinimleri (requirements.txt) kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalar�n� kopyala
COPY . .

# Sanal asistan� �al��t�ran ana dosyay� belirle
CMD ["python", "agri_assistant.py"]
