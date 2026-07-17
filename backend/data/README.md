# backend/data

Market data abstraction layer.

## Why this abstraction exists

Project Atlas needs market data, but no application code should know
which provider supplies it. The provider layer isolates the rest of the
platform from provider-specific SDKs, response shapes, and failure
modes. Three concrete benefits:

1. **Portability.** Swapping Kite for a different provider (or a test
   fixture) is a wiring change, not a refactor of business logic.
2. **Testability.** A mock provider can be injected into
   `MarketDataService` so unit tests never make network calls.
3. **Stability of contracts.** Provider-specific types never escape
   this package. Everything else sees the same `Instrument`,
   `Quote`, and `HistoricalPrice` schemas regardless of source.

## Folder layout

```
data/
├── __init__.py
├── exceptions.py             # AuthenticationError, RateLimitError, ...
├── providers/
│   ├── __init__.py           # MarketDataProvider (ABC)
│   ├── kite_provider.py      # KiteProvider (stub)
│   └── README.md
├── services/
│   ├── __init__.py
│   ├── market_data_service.py
│   └── README.md
└── schemas/
    ├── __init__.py           # Instrument, Quote, HistoricalPrice
    └── README.md
```

## How dependency injection is used

`MarketDataService` does not construct its own provider. A caller
passes a `MarketDataProvider` instance into the service's constructor:

```python
service = MarketDataService(KiteProvider())
service.authenticate()
quotes = service.get_historical_data("NSE", "INFY", start, end)
```

This lets the application decide (e.g. in a FastAPI dependency) which
concrete provider to use, and lets tests substitute a mock without
touching the service.

## How a new provider is added

1. Create `backend/data/providers/<name>_provider.py` with a class
   that inherits from `MarketDataProvider`.
2. Implement all seven abstract methods, converting provider-specific
   types into the schemas in `backend.data.schemas` before returning.
3. Raise exceptions from `backend.data.exceptions`; do not let SDK
   exceptions escape.
4. Wire the new provider into the application (e.g. in a FastAPI
   dependency factory) instead of `KiteProvider`.

No other module of the application needs to change.
