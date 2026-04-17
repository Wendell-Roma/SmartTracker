import os
import time
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import requests
from fake_useragent import UserAgent
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TIMEOUT        = int(os.getenv("REQUEST_TIMEOUT", 15))
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", 3))


@dataclass
class ScrapedProduct:
    name:      str
    price:     Optional[float]
    available: bool
    store:     str
    url:       str


class BaseScraper(ABC):
    """Classe base para todos os scrapers."""

    store_name: str = "unknown"

    def __init__(self):
        self._ua = UserAgent()
        self._session = requests.Session()

    # ── helpers ──────────────────────────────────────────────────────────────

    @property
    def _headers(self) -> dict:
        return {
            "User-Agent": self._ua.random,
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    def _get(self, url: str) -> Optional[requests.Response]:
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                resp = self._session.get(
                    url, headers=self._headers, timeout=TIMEOUT
                )
                resp.raise_for_status()
                return resp
            except requests.RequestException as exc:
                logger.warning(f"[{self.store_name}] Tentativa {attempt}/{RETRY_ATTEMPTS} falhou: {exc}")
                if attempt < RETRY_ATTEMPTS:
                    time.sleep(random.uniform(2, 5))
        return None

    # ── interface pública ─────────────────────────────────────────────────────

    @abstractmethod
    def scrape(self, url: str) -> ScrapedProduct:
        """Busca preço e disponibilidade de um produto."""
        ...

    @classmethod
    def supports(cls, url: str) -> bool:
        """Retorna True se este scraper suporta a URL fornecida."""
        return False
