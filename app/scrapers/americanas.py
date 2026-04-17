import logging
import re
import json
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


class AmericanasScraper(BaseScraper):
    store_name = "americanas"

    def scrape(self, url: str) -> ScrapedProduct:
        resp = self._get(url)
        if resp is None:
            return ScrapedProduct(
                name="Erro ao acessar página", price=None,
                available=False, store=self.store_name, url=url,
            )

        soup = BeautifulSoup(resp.text, "lxml")

        name  = "Produto não encontrado"
        price = None

        # JSON-LD primeiro
        for script in soup.find_all("script", {"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    data = data[0]
                if data.get("@type") in ("Product", "ItemPage"):
                    name = data.get("name", name)
                    offers = data.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0]
                    raw = offers.get("price")
                    price = float(raw) if raw else None
                    break
            except Exception:
                continue

        # Fallbacks HTML
        if not price:
            for sel in [
                "[class*='src__BestPrice']",
                "[class*='priceSales']",
                "[class*='price__']",
                "span[class*='Price']",
            ]:
                tag = soup.select_one(sel)
                if tag:
                    price = _parse_price(tag.get_text())
                    if price:
                        break

        if name == "Produto não encontrado":
            h1 = soup.find("h1")
            if h1:
                name = h1.get_text(strip=True)

        available = not bool(soup.find(string=re.compile(r"indispon[íi]vel", re.I)))

        logger.info(f"[Americanas] {name[:50]} → R${price}")
        return ScrapedProduct(
            name=name, price=price,
            available=available,
            store=self.store_name, url=url,
        )

    @classmethod
    def supports(cls, url: str) -> bool:
        return "americanas.com.br" in url
