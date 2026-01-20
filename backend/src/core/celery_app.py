from celery import Celery
from celery.schedules import crontab # Importante para definir horas exactas
import os

REDIS_URL = os.getenv("REDIS_URL")

celery_app = Celery(
    "inspector_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
    imports=["src.worker.tasks"],
    
    # 🔧 Optimizaciones de Worker
    worker_prefetch_multiplier=int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", "2")),
    task_acks_late=True,           # Confirma tarea solo después de completarla
    task_reject_on_worker_lost=True,  # Re-encola si worker muere
)

# === DEFINICIÓN DE JOBS (CRONOGRAMA) ===
celery_app.conf.beat_schedule = {
    
    # 1. Sincronización Automática (Cada 5 minutos)
    "sync-inventory-every-5-mins": {
        "task": "tasks.run_automatic_sync",
        "schedule": crontab(minute="*/5"), # Cada 5 min (0, 5, 10...)
        "args": (False,) # is_manual = False
    },

    # 2. Reinicio Automático de Inspectores (Todos los días a las 5:00 AM)
    "restart-inspectors-daily-5am": {
        "task": "tasks.run_automatic_restart", # Aún no creamos esta función, ¡vamos a ello!
        "schedule": crontab(hour=5, minute=0), 
        "args": (False,)
    },
    
    # Aquí puedes agregar más jobs (Backups, Limpieza, etc.)
}