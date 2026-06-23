# Distributed Systems Standards

## Principios

- La red falla.
- Los mensajes pueden duplicarse.
- El orden no siempre esta garantizado.
- La latencia cambia.
- Las dependencias externas tienen limites.

## Reglas

- Idempotencia por diseno para consumers, webhooks y jobs.
- Retries con backoff y limite.
- DLQ o registro equivalente para fallos permanentes.
- Timeouts y circuit breakers donde aplique.
- Correlation id para trazabilidad.
- Contratos versionados entre servicios.
- Backpressure o rate limits para productores rapidos.

## Prohibido

- Retry infinito.
- Procesamiento no idempotente de mensajes at-least-once.
- Acoplar disponibilidad de user flow critico a servicio externo no esencial sin fallback.
