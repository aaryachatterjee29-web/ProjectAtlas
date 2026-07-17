"""Market data package for Project Atlas.

This package isolates the platform from any specific data provider
(Kite today; Alpha Vantage, a CSV reader, or an internal test fixture
tomorrow). See the subpackage READMEs for details:

* :mod:`backend.data.providers` - the provider abstraction and concrete
  implementations.
* :mod:`backend.data.services` - the orchestration layer that the rest
  of the application uses.
* :mod:`backend.data.schemas` - provider-independent data shapes.
"""

from __future__ import annotations

from backend.data.schemas import HistoricalPrice, Instrument, Quote

__all__ = ["HistoricalPrice", "Instrument", "Quote"]
