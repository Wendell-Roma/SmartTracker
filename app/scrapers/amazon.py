import logging
import re
from typing import Optional

from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper, ScrapedProduct

logger = logging.getLogger(__name__)


def _parse_price(text: str) -> Optional[float]:
    """Converte 'R$\xa01.234,56' → 1234.56"""
    cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
    # Se houver mais de um ponto, o último é decimal
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(cleaned)
    except ValueError:
        return None


class AmazonScraper(BaseScraper):
    store_name = "amazon"

    # Seletores CSS em ordem de prioridade (Amazon muda com frequência)
    _PRICE_SELECTORS = [
        "span.a-price > span.a-offscreen",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        "#price_inside_buybox",
        "span#price",
        ".a-price .a-offscreen",
    ]

    _TITLE_SELECTORS = [
        "#productTitle",
        "#title",
    ]

    def scrape(self, url: str) -> ScrapedProduct:
        resp = self._get(url)
        if resp is None:
            return ScrapedProduct(
                name="Erro ao acessar página", price=None,
                available=False, store=self.store_name, url=url,
            )

        soup = BeautifulSoup(resp.text, "lxml")

        # ── Título ──────────────────────────────────────────────────────────
        name = "Produto não encontrado"
        for sel in self._TITLE_SELECTORS:
            tag = soup.select_one(sel)
            if tag:
                name = tag.get_text(strip=True)
                break

        # ── Preço ────────────────────────────────────────────────────────────
        price: Optional[float] = None
        for sel in self._PRICE_SELECTORS:
            tag = soup.select_one(sel)
            if tag:
                price = _parse_price(tag.get_text())
                if price:
                    break

        # ── Disponibilidade ──────────────────────────────────────────────────
        unavailable = soup.select_one("#availability span")
        available = True
        if unavailable:
            txt = unavailable.get_text(strip=True).lower()
            available = "indisponível" not in txt and "unavailable" not in txt

        logger.info(f"[Amazon] {name[:50]} → R${price}")
        return ScrapedProduct(
            name=name, price=price,
            available=available,
            store=self.store_name, url=url,
        )

    @classmethod
    def supports(cls, url: str) -> bool:
        return "amazon.com.br" in url or "amzn.to" in url
