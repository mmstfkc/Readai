import os
import time
import json

from .celery_app import celery_app

from app.extractors.dispatcher import ExtractorDispatcher
from app.llm.openai_llm import MockLLM

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
    Pipeline:
    1. Raw OCR extraction (if not exists)
    2. LLM normalization (idempotent, per model)
    """
    dispatcher = ExtractorDispatcher()
    llm = MockLLM()  # will be replaced with a real LLM in the future

    raw_output_path = os.path.join(
        STORAGE_OUTPUT_DIR,
        f"{job_id}_raw.json"
    )

    os.makedirs(STORAGE_OUTPUT_DIR, exist_ok=True)

    # -------------------------------------------------
    # 1️ RAW EXTRACTION (Is there any? Check it.)
    # -------------------------------------------------
    if os.path.exists(raw_output_path):
        with open(raw_output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        raw_text = dispatcher.extract(input_path)
        data = {
            "job_id": job_id,
            "stage": "raw_extraction",
            "text": raw_text,
            "llm": {}
        }

        with open(raw_output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # -------------------------------------------------
    # 2️ LLM NORMALIZATION (idempotent)
    # -------------------------------------------------
    model_name = llm.model_name  # Ex: "mock-llm"

    if "llm" not in data:
        data["llm"] = {}

    if model_name in data["llm"]:
        # Previously processed with this model → No LLM call
        return {
            "job_id": job_id,
            "status": "skipped",
            "reason": f"LLM output already exists for model '{model_name}'",
            "output_path": raw_output_path
        }

    # LLM call
    normalized_text = llm.normalize_text(data["text"])

    data["llm"][model_name] = {
        "normalized_text": normalized_text
    }

    # Update the JSON (same file!)
    with open(raw_output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return {
        "job_id": job_id,
        "status": "completed",
        "llm_model": model_name,
        "output_path": raw_output_path
    }