import os
import time
import json

from .celery_app import celery_app

from app.extractors.dispatcher import ExtractorDispatcher

STORAGE_OUTPUT_DIR = os.getenv("STORAGE_OUTPUT_DIR", "/app/storage/outputs")

@celery_app.task(bind=True)
def ping(self):
    time.sleep(1)
    return {
        "status": "ok",
        "worker": "readai-worker",
        "message": "pong"
    }

@celery_app.task(bind=True)
def process_job(self, job_id: str, input_path: str):
    dispatcher = ExtractorDispatcher()

    extracted_text = dispatcher.extract(input_path)

    os.makedirs(STORAGE_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(STORAGE_OUTPUT_DIR, f"{job_id}_raw.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "job_id": job_id,
                "stage": "raw_extraction",
                "text": extracted_text
            },
            f,
            ensure_ascii=False,
            indent=2
        )

    return {
        "job_id": job_id,
        "status": "completed",
        "output_path": output_path
    }