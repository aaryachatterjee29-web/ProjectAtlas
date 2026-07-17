"""Abstract base class for market data providers.

Any concrete provider (Kite, Alpha Vantage, a custom CSV reader, ...) must
implement the seven methods defined here. The rest of the application
talks to providers only through this interface and through
:class:`~backend.data.services.market_data_service.MarketDataService`,
never through provider-specific classes.

Contract
--------
* All methods are synchronous. Async support can be added later by
  introducing a sibling ``AsyncMarketDataProvider`` if needed.
* All return values are provider-independent schema objects
  (see :mod:`backend.data.schemas`). Provider-specific types must be
  converted to schemas before returning.
* All errors are raised as exceptions from
  :mod:`backend.data.exceptions`. No provider SDK exception should leak
  past a provider implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from backend.data.schemas import HistoricalPrice, Instrument, Quote


class MarketDataProvider(ABC):
    """Abstract base class for all market data providers."""

    @abstractmethod
    def connect(self) -> None:
        """Establish any persistent connection or session with the provider.

        Idempotent: calling ``connect()`` on an already-connected provider
        should be a no-op.
        """

    @abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the provider using configured credentials.

        Implementations should raise :class:`~backend.data.exceptions.AuthenticationError`
        on failure.
        """

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the provider is reachable and authenticated."""

    @abstractmethod
    def get_instruments(self, exchange: str) -> list[Instrument]:
        """Return the list of instruments available on the given exchange."""

    @abstractmethod
    def search_instrument(self, query: str, exchange: str | None = None) -> list[Instrument]:
        """Search for instruments matching ``query``.

        If ``exchange`` is given, results are restricted to that exchange.
        Raises :class:`~backend.data.exceptions.InstrumentNotFound` only if
        the search itself fails; an empty result list means "no matches".
        """

    @abstractmethod
    def get_historical_data(
        self,
        exchange: str,
        symbol: str,
        start: date,
        end: date,
        interval: str = "day",
    ) -> list[HistoricalPrice]:
        """Return historical OHLCV bars for an instrument.

        ``interval`` follows the provider's native vocabulary
        (e.g. ``"day"``, ``"minute"``).
        """

    @abstractmethod
    def get_latest_quote(self, exchange: str, symbol: str) -> Quote:
        """Return the most recent price quote for an instrument."""
