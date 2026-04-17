"""
Testes básicos dos scrapers.
Execute com: pytest tests/ -v
"""
import pytest
from unittest.mock import patch, MagicMock
from app.scrapers.mercadolivre import MercadoLivreScraper, _extract_item_id
from app.scrapers.amazon import AmazonScraper, _parse_price
from app.scrapers import get_scraper


# ── Utilitários ──────────────────────────────────────────────────────────────

def test_extract_ml_id():
    url = "https://www.mercadolivre.com.br/produto/MLB-123456789"
    assert _extract_item_id(url) == "MLB123456789"


def test_parse_amazon_price():
    assert _parse_price("R$\xa01.234,56") == 1234.56
    assert _parse_price("R$ 99,90")       == 99.90
    assert _parse_price("abc")            is None


# ── Factory ──────────────────────────────────────────────────────────────────

def test_get_scraper_ml():
    s = get_scraper("https://www.mercadolivre.com.br/produto/MLB-1")
    assert isinstance(s, MercadoLivreScraper)

def test_get_scraper_amazon():
    s = get_scraper("https://www.amazon.com.br/dp/B09XYZ")
    assert isinstance(s, AmazonScraper)

def test_get_scraper_unsupported():
    with pytest.raises(ValueError):
        get_scraper("https://www.shopeedesconhecida.com/item/123")


# ── Scraper com mock de HTTP ──────────────────────────────────────────────────

ML_API_RESPONSE = {
    "title": "Notebook Teste",
    "price": 2999.90,
    "status": "active",
    "available_quantity": 5,
}

def test_mercadolivre_scrape():
    scraper = MercadoLivreScraper()
    with patch("app.scrapers.mercadolivre.requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.json.return_value = ML_API_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = scraper.scrape("https://www.mercadolivre.com.br/MLB123456789")
        assert result.name  == "Notebook Teste"
        assert result.price == 2999.90
        assert result.available is True
