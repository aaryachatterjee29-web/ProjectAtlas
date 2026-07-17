"""Service layer for the market data package.

Currently exposes :class:`MarketDataService`, which wraps an injected
:class:`~backend.data.providers.MarketDataProvider`. Add additional
services here as the platform grows.
"""

from __future__ import annotations

from backend.data.services.market_data_service import MarketDataService

__all__ = ["MarketDataService"]
