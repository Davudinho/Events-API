# Offizielles Python-Image (schlanke Variante)
FROM python:3.11-slim

# Kein Bytecode schreiben, ungepufferte Ausgabe
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Arbeitsverzeichnis im Container
WORKDIR /app

# Zuerst Requirements kopieren und installieren
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Restlichen Code kopieren
COPY . .

# Flask-API läuft auf Port 5000
EXPOSE 5000

# Startkommando: deine App wie lokal starten
# (in app-2.py wird create_app() aufgerufen und host=0.0.0.0, port=5000 gesetzt)[file:15]
CMD ["python", "app.py"]