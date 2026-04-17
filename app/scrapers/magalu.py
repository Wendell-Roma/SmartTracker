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


class MagaluScraper(BaseScraper):
    store_name = "magalu"

    def scrape(self, url: str) -> ScrapedProduct:
        resp = self._get(url)
        if resp is None:
            return ScrapedProduct(
                name="Erro ao acessar página", price=None,
                available=False, store=self.store_name, url=url,
            )

        soup = BeautifulSoup(resp.text, "lxml")

        # Magalu embute dados em JSON-LD
        name  = "Produto não encontrado"
        price = None

        script = soup.find("script", {"type": "application/ld+json"})
        if script:
            try:
                data = json.loads(script.string)
                # Pode ser lista ou dict
                if isinstance(data, list):
                    data = data[0]
                name  = data.get("name", name)
                offers = data.get("offers", {})
                if isinstance(offers, list):
                    offers = offers[0]
                raw = offers.get("price") or offers.get("lowPrice")
                price = float(raw) if raw else None
            except Exception:
                pass

        # Fallback: seletores HTML
        if not price:
            for sel in ["[data-testid='price-value']", "p[class*='Price']", "span[class*='price']"]:
                tag = soup.select_one(sel)
                if tag:
                    price = _parse_price(tag.get_text())
                    if price:
                        break

        if not name or name == "Produto não encontrado":
            title_tag = soup.find("h1")
            if title_tag:
                name = title_tag.get_text(strip=True)

        available = bool(soup.select_one("[data-testid='add-to-cart-button']") or
                         soup.find(string=re.compile(r"adicionar ao carrinho", re.I)))

        logger.info(f"[Magalu] {name[:50]} → R${price}")
        return ScrapedProduct(
            name=name, price=price,
            available=available,
            store=self.store_name, url=url,
        )

    @classmethod
    def supports(cls, url: str) -> bool:
        return "magazineluiza.com.br" in url or "magalu.com.br" in url
