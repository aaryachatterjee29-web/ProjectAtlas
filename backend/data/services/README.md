# backend/data/services

Service layer over the provider abstraction.

Currently exposes `MarketDataService`, a thin pass-through that accepts
any `MarketDataProvider` via constructor injection. Cross-cutting
concerns (caching, retry, rate-limit handling, logging, metrics) belong
on this service as the platform grows.
