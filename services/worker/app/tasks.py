from .celery_app import celery_app
import time

@celery_app.task(bind=True)
def ping(self):
    time.sleep(1)
    return {
        "status": "ok",
        "worker": "readai-worker",
        "message": "pong"
    }
