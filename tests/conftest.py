"""Shared pytest fixtures and helpers for the test suite."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pytest

from backend.data.providers import MarketDataProvider
from backend.data.schemas import HistoricalPrice, Instrument, Quote


class MockMarketDataProvider(MarketDataProvider):
    """In-memory provider used by unit tests.

    Every method records its call in ``self.calls`` and returns a
    pre-configured return value (set via attributes on the instance or
    on the test fixture). The mock never touches the network.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

        self.connect_return: None = None
        self.authenticate_return: None = None
        self.health_check_return: bool = True
        self.instruments: list[Instrument] = []
        self.search_results: list[Instrument] = []
        self.historical: list[HistoricalPrice] = []
        self.quote: Quote | None = None
        self.raise_on: dict[str, BaseException] = {}

    def _record(self, name: str, *args: Any, **kwargs: Any) -> None:
        self.calls.append((name, args, kwargs))
        if name in self.raise_on:
            raise self.raise_on[name]

    def connect(self) -> None:
        self._record("connect")
        return self.connect_return

    def authenticate(self) -> None:
        self._record("authenticate")
        return self.authenticate_return

    def health_check(self) -> bool:
        self._record("health_check")
        return self.health_check_return

    def get_instruments(self, exchange: str) -> list[Instrument]:
        self._record("get_instruments", exchange)
        return list(self.instruments)

    def search_instrument(self, query: str, exchange: str | None = None) -> list[Instrument]:
        self._record("search_instrument", query, exchange)
        return list(self.search_results)

    def get_historical_data(
        self,
        exchange: str,
        symbol: str,
        start: date,
        end: date,
        interval: str = "day",
    ) -> list[HistoricalPrice]:
        self._record("get_historical_data", exchange, symbol, start, end, interval)
        return list(self.historical)

    def get_latest_quote(self, exchange: str, symbol: str) -> Quote:
        self._record("get_latest_quote", exchange, symbol)
        assert self.quote is not None, "test must set mock.quote before calling get_latest_quote"
        return self.quote


@pytest.fixture
def mock_provider() -> MockMarketDataProvider:
    """Fresh mock provider for each test."""
    return MockMarketDataProvider()


@pytest.fixture
def sample_quote() -> Quote:
    return Quote(
        exchange="NSE",
        symbol="INFY",
        last_price=Decimal("1500.00"),
        bid=Decimal("1499.50"),
        ask=Decimal("1500.50"),
        timestamp=datetime(2026, 7, 17, 9, 30, 0),
    )


@pytest.fixture
def sample_historical() -> list[HistoricalPrice]:
    return [
        HistoricalPrice(
            exchange="NSE",
            symbol="INFY",
            date=date(2026, 7, 16),
            open=Decimal("1490"),
            high=Decimal("1510"),
            low=Decimal("1485"),
            close=Decimal("1505"),
            adjusted_close=Decimal("1505"),
            volume=1_000_000,
        ),
    ]
