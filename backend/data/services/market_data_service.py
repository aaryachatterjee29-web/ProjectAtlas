"""Service layer over a :class:`MarketDataProvider`.

The service exposes the same public method surface as the provider
interface, but every method simply forwards to the injected provider.
This is deliberately thin today: the value is the dependency-injection
boundary, not business logic. As the platform grows, additional
cross-provider concerns (caching, retry, rate-limit backoff, logging,
metrics) belong on this service rather than on individual providers.
"""

from __future__ import annotations

from datetime import date

from backend.data.providers import MarketDataProvider
from backend.data.schemas import HistoricalPrice, Instrument, Quote


class MarketDataService:
    """Thin orchestration layer around an injected market data provider.

    The service does not know which provider it is talking to. Callers
    construct it with any concrete :class:`MarketDataProvider` and use
    the service to access market data. This keeps provider-specific
    classes out of the rest of the application.
    """

    def __init__(self, provider: MarketDataProvider) -> None:
        self._provider = provider

    def connect(self) -> None:
        self._provider.connect()

    def authenticate(self) -> None:
        self._provider.authenticate()

    def health_check(self) -> bool:
        return self._provider.health_check()

    def get_instruments(self, exchange: str) -> list[Instrument]:
        return self._provider.get_instruments(exchange)

    def search_instrument(self, query: str, exchange: str | None = None) -> list[Instrument]:
        return self._provider.search_instrument(query, exchange)

    def get_historical_data(
        self,
        exchange: str,
        symbol: str,
        start: date,
        end: date,
        interval: str = "day",
    ) -> list[HistoricalPrice]:
        return self._provider.get_historical_data(exchange, symbol, start, end, interval)

    def get_latest_quote(self, exchange: str, symbol: str) -> Quote:
        return self._provider.get_latest_quote(exchange, symbol)
