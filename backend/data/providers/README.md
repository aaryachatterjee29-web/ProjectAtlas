# backend/data/providers

Concrete and abstract market data providers.

## Contents

* `__init__.py` — `MarketDataProvider`, the abstract base class that
  defines the contract every provider must implement.
* `kite_provider.py` — `KiteProvider`, a stub for the Kite Connect
  integration. Every method currently raises `NotImplementedError`.

## Contract

Every concrete provider must:

1. Inherit from `MarketDataProvider`.
2. Implement all seven abstract methods:
   `connect`, `authenticate`, `health_check`, `get_instruments`,
   `search_instrument`, `get_historical_data`, `get_latest_quote`.
3. Convert provider-specific types into the schemas in
   `backend.data.schemas` before returning.
4. Raise only exceptions from `backend.data.exceptions`. SDK-specific
   exceptions must be caught and re-raised as the appropriate typed
   error (e.g. `AuthenticationError` on token failure).
