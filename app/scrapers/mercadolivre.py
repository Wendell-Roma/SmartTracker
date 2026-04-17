import os
import logging
import re
from typing import Optional

import requests
from dotenv import load_dotenv
from app.scrapers.base import BaseScraper, ScrapedProduct

load_dotenv()
logger = logging.getLogger(__name__)

ML_APP_ID      = os.getenv("ML_APP_ID", "")
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET", "")
ML_API_BASE    = "https://api.mercadolibre.com"


def _extract_item_id(url: str) -> Optional[str]:
    """Extrai o ID do item da URL do Mercado Livre (ex: MLB-123456789)."""
    match = re.search(r"(MLB-?\d+)", url.upper())
    return match.group(1).replace("-", "") if match else None


class MercadoLivreScraper(BaseScraper):
    """
    Usa a API oficial do Mercado Livre — muito mais estável que scraping HTML.
    Não requer autenticação para consultar preços públicos.
    Docs: https://developers.mercadolivre.com.br
    """

    store_name = "mercadolivre"

    def scrape(self, url: str) -> ScrapedProduct:
        item_id = _extract_item_id(url)

        if not item_id:
            logger.error(f"[MercadoLivre] Não foi possível extrair ID da URL: {url}")
            return ScrapedProduct(
                name="Erro: ID não encontrado",
                price=None, available=False,
                store=self.store_name, url=url,
            )

        api_url = f"{ML_API_BASE}/items/{item_id}"
        try:
            resp = requests.get(api_url, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            name      = data.get("title", "Produto sem nome")
            price     = float(data.get("price") or 0) or None
            available = data.get("status") == "active" and int(data.get("available_quantity", 0)) > 0

            logger.info(f"[MercadoLivre] {name[:50]} → R${price}")
            return ScrapedProduct(
                name=name, price=price,
                available=available,
                store=self.store_name, url=url,
            )

        except Exception as exc:
            logger.error(f"[MercadoLivre] Erro ao buscar {item_id}: {exc}")
            return ScrapedProduct(
                name="Erro na consulta", price=None,
                available=False, store=self.store_name, url=url,
            )

    @classmethod
    def supports(cls, url: str) -> bool:
        return "mercadolivre.com.br" in url or "mercadolibre.com" in url
