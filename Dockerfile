# Utilisation d'une image de base Python légère
FROM python:3.10-slim

# Empêcher Python d'écrire des fichiers .pyc et forcer l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install minimal requirements if needed (none strictly needed for headless opencv usually)
# We avoid installing libgl1 and libglib2.0 to keep the image lightweight.

# Définir le répertoire de travail
WORKDIR /app

# Copier le fichier des dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code source
COPY . .

# Exposer le port sur lequel Flask va écouter (Railway uses PORT env var)
EXPOSE 10000

# Lancer l'application Flask.
CMD sh -c "python main.py"
