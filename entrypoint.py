"""
Entrypoint para rodar o dashboard Flask + scheduler APScheduler
no mesmo processo (útil para containers simples).

Para produção com alto volume, rode-os em containers separados
via docker-compose com o serviço 'scheduler' independente.
"""
import threading
import logging
import os

from app.db.database import init_db
from app.scheduler import check_all_products, CHECK_INTERVAL_HOURS
from app.dashboard.app import app as flask_app

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        check_all_products,
        trigger=IntervalTrigger(hours=CHECK_INTERVAL_HOURS),
        id="price_check",
        next_run_time=datetime.now(),
    )
    scheduler.start()
    logger.info(f"⏰ Scheduler rodando em background (a cada {CHECK_INTERVAL_HOURS}h)")
    return scheduler


if __name__ == "__main__":
    init_db()
    scheduler = start_scheduler()

    try:
        flask_app.run(
            host="0.0.0.0",
            port=int(os.getenv("PORT", 5000)),
            debug=False,
            use_reloader=False,
        )
    finally:
        scheduler.shutdown()
