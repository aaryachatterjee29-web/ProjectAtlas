# backend/data/schemas

Provider-independent data shapes.

These Pydantic models are the canonical types that flow between
`MarketDataProvider` implementations and the rest of the application.
They are immutable (`frozen=True`), reject extra fields (`extra=forbid`),
and validate on assignment.

* `Instrument` — a tradable instrument.
* `Quote` — a real-time or near-real-time price quote.
* `HistoricalPrice` — one OHLCV bar of historical data.

No provider-specific types should ever appear outside the provider
layer; conversion happens at the provider boundary.
