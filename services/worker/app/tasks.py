import os
import json
import time

from .celery_app import celery_app
from app.extractors.dispatcher import ExtractorDispatcher
from app.llm.local_llm import LocalLLM

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
    """
    Pipeline (worker-only):
    1. Create job JSON if not exists
    2. Raw OCR extraction (if missing)
    3. LLM normalization (idempotent)
    """

    os.makedirs(STORAGE_OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(STORAGE_OUTPUT_DIR, f"{job_id}.json")

    # -------------------------------------------------
    # 0️⃣ CREATE JOB JSON (FIRST TIME)
    # -------------------------------------------------
    if not os.path.exists(output_path):
        data = {
            "job_id": job_id,
            "input": {
                "path": input_path
            },
            "raw_extraction": None,
            "llm": {}
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    dispatcher = ExtractorDispatcher()
    llm = LocalLLM()
    model_name = llm.model_name

    # -------------------------------------------------
    # 1️⃣ RAW OCR EXTRACTION
    # -------------------------------------------------
    if data.get("raw_extraction") is None:
        raw_text = dispatcher.extract(input_path)

        data["raw_extraction"] = {
            "text": raw_text
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------
    # 2️⃣ LLM NORMALIZATION (IDEMPOTENT)
    # -------------------------------------------------
    if model_name in data.get("llm", {}):
        return {
            "job_id": job_id,
            "status": "skipped",
            "reason": f"LLM output already exists for model '{model_name}'"
        }

    normalized_text = llm.normalize_text(
        data["raw_extraction"]["text"]
    )

    data["llm"][model_name] = {
        "normalized_text": normalized_text
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "job_id": job_id,
        "status": "completed",
        "llm_model": model_name
    }
