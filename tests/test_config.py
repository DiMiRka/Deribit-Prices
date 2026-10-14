import pytest

from app.core.config import Settings


def test_tickers_parsed_from_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TICKERS", " BTC_USD, eth_usd ,")

    settings = Settings(_env_file=None)

    assert settings.tickers == ("btc_usd", "eth_usd")
