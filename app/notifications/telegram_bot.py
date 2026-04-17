import os
import logging
import asyncio

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def send_telegram_alert(product_name: str, store: str,
                         current_price: float, target_price: float,
                         url: str) -> bool:
    """Envia mensagem no Telegram via Bot API."""
    if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        logger.warning("Token/Chat ID do Telegram não configurados — alerta ignorado.")
        return False

    try:
        from telegram import Bot
        text = (
            f"🔔 *Alerta de Preço!*\n\n"
            f"*{product_name}*\n"
            f"🏪 Loja: {store.capitalize()}\n"
            f"💰 Preço atual: *R$ {current_price:,.2f}*\n"
            f"🎯 Sua meta: R$ {target_price:,.2f}\n\n"
            f"[Ver produto]({url})"
        )

        async def _send():
            bot = Bot(token=TELEGRAM_TOKEN)
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode="Markdown",
            )

        asyncio.run(_send())
        logger.info("Mensagem Telegram enviada com sucesso.")
        return True
    except Exception as exc:
        logger.error(f"Falha ao enviar Telegram: {exc}")
        return False
