import logging
import re
from typing import Optional

from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper, ScrapedProduct

logger = logging.getLogger(__name__)


def _parse_price(text: str) -> Optional[float]:
    cleaned = re.sub(r"[^\d,]", "", text).replace(",", ".")
    parts = cleaned.split(".")
    if len(parts) > 2:
        cleaned = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(cleaned)
    except ValueError:
        return None


class KabumScraper(BaseScraper):
    """
    KaBuM! tem HTML bastante limpo — ideal para iniciantes estudarem o código.
    """
    store_name = "kabum"

    def scrape(self, url: str) -> ScrapedProduct:
        resp = self._get(url)
        if resp is None:
            return ScrapedProduct(
                name="Erro ao acessar página", price=None,
                available=False, store=self.store_name, url=url,
            )

        soup = BeautifulSoup(resp.text, "lxml")

        # Título
        name = "Produto não encontrado"
        h1 = soup.find("h1")
        if h1:
            name = h1.get_text(strip=True)

        # Preço à vista
        price = None
        for sel in [
            "span.finalPrice",
            "span[class*='priceCard']",
            "[class*='regularPrice']",
            "h4.finalPrice",
        ]:
            tag = soup.select_one(sel)
            if tag:
                price = _parse_price(tag.get_text())
                if price:
                    break

        # Disponibilidade
        unavail = soup.find(string=re.compile(r"indispon[íi]vel|esgotado", re.I))
        available = unavail is None and price is not None

        logger.info(f"[KaBuM] {name[:50]} → R${price}")
        return ScrapedProduct(
            name=name, price=price,
            available=available,
            store=self.store_name, url=url,
        )

    @classmethod
    def supports(cls, url: str) -> bool:
        return "kabum.com.br" in url
