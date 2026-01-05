from .celery_app import celery_app
import time
import os

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
    """
    Dummy job processor.
    Later: OCR + LLM pipeline will be here.
    """
    time.sleep(2)

    return {
        "job_id": job_id,
        "status": "completed",
        "input_path": input_path,
        "message": "Dummy processing finished"
    }