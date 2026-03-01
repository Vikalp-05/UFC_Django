import pytest
from unittest.mock import patch
from scrape_ufc import clean, norm, scrape_rankings


def test_clean():
    assert clean("  A   B ") == "A B"


def test_norm():
    assert norm("Hello-World!!") == "hello world"


@patch("scrape_ufc.session.get")
def test_scrape_rankings_returns_dict(mock_get):
    mock_get.return_value.text = "<html></html>"
    result = scrape_rankings()
    assert isinstance(result, dict)