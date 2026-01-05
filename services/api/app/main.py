import os
import uuid
import shutil
from datetime import datetime

from fastapi import FastAPI, UploadFile, File

from app.celery_client import celery_client

STORAGE_INPUT_DIR = os.getenv("STORAGE_INPUT_DIR", "/app/storage/inputs")

app = FastAPI(
    title="Readai API",
    version="0.1.0",
    description="LLM-powered document & invoice extraction pipeline"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "readai-api",
        "timestamp": datetime.utcnow().isoformat(),
        "storage": {
            "inputs": os.path.exists("/app/storage/inputs"),
            "outputs": os.path.exists("/app/storage/outputs"),
            "meta": os.path.exists("/app/storage/meta"),
        }
    }

@app.post("/api/jobs")
def create_job(file: UploadFile = File(...)):
    # 1️⃣ Job ID
    job_id = str(uuid.uuid4())

    # 2️⃣ Dosyayı kaydet
    os.makedirs(STORAGE_INPUT_DIR, exist_ok=True)
    input_path = os.path.join(STORAGE_INPUT_DIR, f"{job_id}_{file.filename}")

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3️⃣ Worker'a task gönder
    celery_client.send_task(
        "app.tasks.process_job",
        args=[job_id, input_path]
    )

    # 4️⃣ API response (hemen döner)
    return {
        "job_id": job_id,
        "status": "queued",
        "filename": file.filename,
        "created_at": datetime.utcnow().isoformat()
    }