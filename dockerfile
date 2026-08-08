FROM python:3.11-slim

WORKDIR /app

# Copier les dépendances et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY . .

# Exposer le port (Clever Cloud injectera $PORT)
ENV PORT=8080
EXPOSE 8080

# Lancer l'application avec uvicorn directement en mode ASGI pur
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT}
