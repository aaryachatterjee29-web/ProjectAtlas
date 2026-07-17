"""Stub Kite provider for Project Atlas.

This is an architecture-only placeholder. The real implementation will
integrate with the Kite Connect SDK and will live in this file once the
SDK is approved as a dependency. Until then every method raises
``NotImplementedError`` so the rest of the system has a concrete class
to wire against, but no provider-specific code is committed.
"""

from __future__ import annotations

from datetime import date

from backend.data.providers import MarketDataProvider
from backend.data.schemas import HistoricalPrice, Instrument, Quote


class KiteProvider(MarketDataProvider):
    """Concrete ``MarketDataProvider`` backed by Kite Connect.

    Implementation status: not implemented. Every method raises
    ``NotImplementedError``. Subclasses or future commits to this module
    will replace the stubs with real SDK calls.
    """

    def connect(self) -> None:
        raise NotImplementedError("KiteProvider.connect is not yet implemented.")

    def authenticate(self) -> None:
        raise NotImplementedError("KiteProvider.authenticate is not yet implemented.")

    def health_check(self) -> bool:
        raise NotImplementedError("KiteProvider.health_check is not yet implemented.")

    def get_instruments(self, exchange: str) -> list[Instrument]:
        raise NotImplementedError("KiteProvider.get_instruments is not yet implemented.")

    def search_instrument(self, query: str, exchange: str | None = None) -> list[Instrument]:
        raise NotImplementedError("KiteProvider.search_instrument is not yet implemented.")

    def get_historical_data(
        self,
        exchange: str,
        symbol: str,
        start: date,
        end: date,
        interval: str = "day",
    ) -> list[HistoricalPrice]:
        raise NotImplementedError("KiteProvider.get_historical_data is not yet implemented.")

    def get_latest_quote(self, exchange: str, symbol: str) -> Quote:
        raise NotImplementedError("KiteProvider.get_latest_quote is not yet implemented.")
