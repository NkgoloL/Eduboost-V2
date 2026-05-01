"""Tasks for automated database backups."""

import subprocess
import os
import structlog
from app.api.core.celery_app import celery_app

log = structlog.get_logger()

@celery_app.task(name="eduboost.tasks.database_backup")
def database_backup():
    """Trigger the database backup script."""
    script_path = "/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/scripts/db_backup.sh"
    
    if not os.path.exists(script_path):
        log.error("backup.script_not_found", path=script_path)
        return {"status": "error", "message": "Backup script not found"}

    try:
        log.info("backup.started")
        result = subprocess.run([script_path], capture_output=True, text=True, check=True)
        log.info("backup.completed", output=result.stdout)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        log.error("backup.failed", error=str(e), output=e.stdout, stderr=e.stderr)
        return {"status": "error", "error": str(e)}
    except Exception as e:
        log.error("backup.exception", error=str(e))
        return {"status": "error", "error": str(e)}
