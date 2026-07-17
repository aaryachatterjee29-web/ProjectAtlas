"""Custom exceptions for the market data layer.

All provider-facing errors are normalized into a small hierarchy so that
the rest of the application can handle them uniformly regardless of which
provider was used. Catching the base ``DataProviderError`` is the
recommended default; specific subclasses exist for fine-grained handling
(e.g. backing off on ``RateLimitError``).
"""

from __future__ import annotations


class DataProviderError(Exception):
    """Base class for all market data provider errors.

    Use this when you want to catch any provider failure without
    distinguishing the underlying cause.
    """


class AuthenticationError(DataProviderError):
    """Raised when provider authentication or token validation fails."""


class RateLimitError(DataProviderError):
    """Raised when a provider rejects a request due to rate limiting.

    Carries an optional ``retry_after`` hint (seconds) so callers can
    back off intelligently.
    """

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class InstrumentNotFound(DataProviderError):
    """Raised when a requested instrument cannot be located by the provider."""
