import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

EMAIL_SENDER   = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")


def send_price_alert(product_name: str, store: str, current_price: float,
                     target_price: float, url: str) -> bool:
    """Envia e-mail de alerta quando preço atinge o alvo."""
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        logger.warning("Credenciais de e-mail não configuradas — alerta ignorado.")
        return False

    subject = f"🎉 Alerta de Preço: {product_name[:50]}"

    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
      <div style="background:#1a1a2e; padding:24px; border-radius:8px;">
        <h2 style="color:#e94560; margin:0 0 16px">🔔 Meta de Preço Atingida!</h2>
        <p style="color:#eee; font-size:16px; margin:0 0 8px"><strong>{product_name}</strong></p>
        <p style="color:#aaa; font-size:14px; margin:0 0 16px">Loja: {store.capitalize()}</p>
        <div style="background:#16213e; padding:16px; border-radius:6px; margin-bottom:16px;">
          <p style="color:#aaa; margin:0; font-size:13px">Preço atual</p>
          <p style="color:#4ecca3; font-size:32px; font-weight:bold; margin:4px 0">
            R$ {current_price:,.2f}
          </p>
          <p style="color:#666; font-size:13px; margin:0">
            Sua meta era: R$ {target_price:,.2f}
          </p>
        </div>
        <a href="{url}" style="background:#e94560; color:white; padding:12px 24px;
           text-decoration:none; border-radius:6px; font-size:14px; display:inline-block;">
          Ver produto →
        </a>
      </div>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RECEIVER
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        logger.info(f"E-mail de alerta enviado para {EMAIL_RECEIVER}")
        return True
    except Exception as exc:
        logger.error(f"Falha ao enviar e-mail: {exc}")
        return False
