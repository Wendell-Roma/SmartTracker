from app.scrapers.base import BaseScraper, ScrapedProduct
from app.scrapers.mercadolivre import MercadoLivreScraper
from app.scrapers.amazon import AmazonScraper
from app.scrapers.magalu import MagaluScraper
from app.scrapers.americanas import AmericanasScraper
from app.scrapers.kabum import KabumScraper

_SCRAPERS: list[type[BaseScraper]] = [
    MercadoLivreScraper,
    AmazonScraper,
    MagaluScraper,
    AmericanasScraper,
    KabumScraper,
]


def get_scraper(url: str) -> BaseScraper:
    """Retorna o scraper correto para a URL fornecida."""
    for cls in _SCRAPERS:
        if cls.supports(url):
            return cls()
    raise ValueError(f"Nenhum scraper disponível para a URL: {url}")


__all__ = [
    "BaseScraper", "ScrapedProduct", "get_scraper",
    "MercadoLivreScraper", "AmazonScraper",
    "MagaluScraper", "AmericanasScraper", "KabumScraper",
]
