# Readai

Invoice & document extraction pipeline (LLM + OCR) with FastAPI, Celery, Redis.

## Current status
✅ Docker skeleton up (api/worker/redis)  
🚧 FastAPI/Celery code will be added step-by-step.

## Quick start
```bash
cp .env.example .env
docker compose -f docker/compose.yml up --build
