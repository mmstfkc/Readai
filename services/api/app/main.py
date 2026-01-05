from fastapi import FastAPI
from datetime import datetime
import os

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
