FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=5000 \
    DATABASE_PATH=/data/notes.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Folder for the SQLite database (mount a volume here to keep notes)
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 5000

CMD ["python", "app.py"]
