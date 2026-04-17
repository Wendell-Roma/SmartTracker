import os
import logging
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from app.db.database import get_session, init_db
from app.db.models import Product, PriceHistory
from app.scrapers import get_scraper
from app.notifications.email_sender import send_price_alert
from app.notifications.telegram_bot import send_telegram_alert

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

CHECK_INTERVAL_HOURS = float(os.getenv("CHECK_INTERVAL_HOURS", 6))


def check_all_products():
    """Verifica preço de todos os produtos ativos."""
    logger.info("━" * 50)
    logger.info(f"🔍 Iniciando verificação — {datetime.now():%d/%m/%Y %H:%M}")

    with get_session() as session:
        products = session.query(Product).filter(Product.active == True).all()

        if not products:
            logger.info("Nenhum produto ativo para verificar.")
            return

        for product in products:
            try:
                scraper = get_scraper(product.url)
                result  = scraper.scrape(product.url)

                entry = PriceHistory(
                    product_id=product.id,
                    price=result.price or 0,
                    available=result.available,
                )
                session.add(entry)
                session.commit()

                logger.info(
                    f"✅ [{product.store}] {product.name[:40]} "
                    f"→ R${result.price} (disponível: {result.available})"
                )

                # Verifica alerta
                if (
                    result.price
                    and product.target_price
                    and result.price <= product.target_price
                    and result.available
                ):
                    logger.info(f"🎉 META ATINGIDA para: {product.name}")
                    send_price_alert(
                        product_name=product.name,
                        store=product.store,
                        current_price=result.price,
                        target_price=product.target_price,
                        url=product.url,
                    )
                    send_telegram_alert(
                        product_name=product.name,
                        store=product.store,
                        current_price=result.price,
                        target_price=product.target_price,
                        url=product.url,
                    )

            except Exception as exc:
                logger.error(f"❌ Erro ao processar {product.url}: {exc}")

    logger.info("✔ Verificação concluída.")


def run_scheduler():
    init_db()
    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(
        check_all_products,
        trigger=IntervalTrigger(hours=CHECK_INTERVAL_HOURS),
        id="price_check",
        next_run_time=datetime.now(),  # roda imediatamente ao iniciar
    )
    logger.info(f"⏰ Scheduler iniciado — verificando a cada {CHECK_INTERVAL_HOURS}h")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler encerrado.")


if __name__ == "__main__":
    run_scheduler()
