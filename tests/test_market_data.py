"""Unit tests for the market data abstraction layer."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.data.exceptions import (
    AuthenticationError,
    DataProviderError,
    InstrumentNotFound,
    RateLimitError,
)
from backend.data.providers import MarketDataProvider
from backend.data.providers.kite_provider import KiteProvider
from backend.data.schemas import Quote
from backend.data.services import MarketDataService


def test_abstract_provider_cannot_be_instantiated() -> None:
    """The ABC must refuse direct instantiation."""
    with pytest.raises(TypeError):
        MarketDataProvider()  # type: ignore[abstract]


def test_partial_implementation_cannot_be_instantiated() -> None:
    """A subclass that skips an abstract method must also be uninstantiable."""

    class IncompleteProvider(MarketDataProvider):
        def connect(self) -> None:
            pass

    with pytest.raises(TypeError):
        IncompleteProvider()  # type: ignore[abstract]


def test_kite_provider_is_a_market_data_provider() -> None:
    """KiteProvider is a concrete (but stub) MarketDataProvider."""
    provider = KiteProvider()
    assert isinstance(provider, MarketDataProvider)


def test_kite_provider_methods_raise_not_implemented() -> None:
    """KiteProvider is currently a stub; every method raises NotImplementedError."""
    provider = KiteProvider()
    with pytest.raises(NotImplementedError):
        provider.connect()
    with pytest.raises(NotImplementedError):
        provider.authenticate()
    with pytest.raises(NotImplementedError):
        provider.health_check()
    with pytest.raises(NotImplementedError):
        provider.get_instruments("NSE")
    with pytest.raises(NotImplementedError):
        provider.search_instrument("INFY")
    with pytest.raises(NotImplementedError):
        provider.get_historical_data("NSE", "INFY", date(2026, 1, 1), date(2026, 1, 31))
    with pytest.raises(NotImplementedError):
        provider.get_latest_quote("NSE", "INFY")


def test_service_accepts_injected_provider(mock_provider: object) -> None:
    """MarketDataService constructor takes any MarketDataProvider."""
    service = MarketDataService(mock_provider)  # type: ignore[arg-type]
    assert service is not None


def test_service_delegates_connect(mock_provider: object) -> None:
    provider = mock_provider  # type: ignore[assignment]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    service.connect()
    assert ("connect", (), {}) in provider.calls  # type: ignore[attr-defined]


def test_service_delegates_authenticate(mock_provider: object) -> None:
    provider = mock_provider  # type: ignore[assignment]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    service.authenticate()
    assert ("authenticate", (), {}) in provider.calls  # type: ignore[attr-defined]


def test_service_delegates_health_check(mock_provider: object) -> None:
    provider = mock_provider  # type: ignore[assignment]
    provider.health_check_return = True  # type: ignore[attr-defined]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    assert service.health_check() is True
    assert ("health_check", (), {}) in provider.calls  # type: ignore[attr-defined]


def test_service_delegates_get_instruments(mock_provider: object) -> None:
    provider = mock_provider  # type: ignore[assignment]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    result = service.get_instruments("NSE")
    assert result == []
    assert ("get_instruments", ("NSE",), {}) in provider.calls  # type: ignore[attr-defined]


def test_service_delegates_search_instrument(mock_provider: object) -> None:
    provider = mock_provider  # type: ignore[assignment]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    result = service.search_instrument("INFY", "NSE")
    assert result == []
    assert ("search_instrument", ("INFY", "NSE"), {}) in provider.calls  # type: ignore[attr-defined]


def test_service_delegates_get_historical_data(
    mock_provider: object, sample_historical: object
) -> None:
    provider = mock_provider  # type: ignore[assignment]
    provider.historical = sample_historical  # type: ignore[attr-defined]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    result = service.get_historical_data("NSE", "INFY", date(2026, 1, 1), date(2026, 1, 31), "day")
    assert result == sample_historical  # type: ignore[comparison-overlap]
    assert (
        "get_historical_data",
        ("NSE", "INFY", date(2026, 1, 1), date(2026, 1, 31), "day"),
        {},
    ) in provider.calls  # type: ignore[attr-defined]


def test_service_delegates_get_latest_quote(mock_provider: object, sample_quote: object) -> None:
    provider = mock_provider  # type: ignore[assignment]
    provider.quote = sample_quote  # type: ignore[attr-defined]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    result = service.get_latest_quote("NSE", "INFY")
    assert result is sample_quote
    assert ("get_latest_quote", ("NSE", "INFY"), {}) in provider.calls  # type: ignore[attr-defined]


def test_service_propagates_provider_exceptions(mock_provider: object) -> None:
    """Exceptions raised by the provider must reach the caller unchanged."""
    provider = mock_provider  # type: ignore[assignment]
    provider.raise_on["authenticate"] = AuthenticationError("bad token")  # type: ignore[attr-defined]
    service = MarketDataService(provider)  # type: ignore[arg-type]
    with pytest.raises(AuthenticationError):
        service.authenticate()


def test_rate_limit_error_carries_retry_after() -> None:
    err = RateLimitError("slow down", retry_after=2.5)
    assert err.retry_after == 2.5
    assert isinstance(err, DataProviderError)


def test_instrument_not_found_is_data_provider_error() -> None:
    err = InstrumentNotFound("missing")
    assert isinstance(err, DataProviderError)
    assert str(err) == "missing"


def test_schema_quote_is_immutable(sample_quote: object) -> None:
    """Schemas are frozen; mutation must be rejected."""
    with pytest.raises(ValidationError):
        sample_quote.last_price = Decimal("1")  # type: ignore[attr-defined]


def test_schema_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Quote(
            exchange="NSE",
            symbol="INFY",
            last_price=Decimal("1"),
            timestamp=datetime(2026, 1, 1),
            something_else="oops",
        )
