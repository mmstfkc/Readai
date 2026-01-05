FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Sistem paketleri (OCR vs için sonra genişletebiliriz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Şimdilik minimum python paketleri (FastAPI/Celery sonra eklenecek)
RUN pip install --no-cache-dir --upgrade pip

# Kodlar volume ile gelecek; şimdilik boş
CMD ["bash", "-lc", "python -V && tail -f /dev/null"]
