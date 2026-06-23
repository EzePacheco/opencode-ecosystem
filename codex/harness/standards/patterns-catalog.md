# Patterns Catalog

## Uso

Elegir patrones por problema, no por prestigio. Siempre explicar trade-offs y cuando no usarlos.

## Arquitectura

### Layered Architecture

- Sirve para apps transaccionales simples.
- No usar como excusa para meter toda la logica en services gigantes.

### Vertical Slice Architecture

- Sirve cuando cada feature necesita evolucionar con autonomia.
- No usar si el equipo todavia no puede sostener convenciones por feature.

### Hexagonal / Ports And Adapters

- Sirve para aislar dominio de infraestructura.
- No usar completo si el problema es CRUD simple y no hay multiples adapters.

### CQRS

- Sirve cuando escritura y lectura tienen modelos o escalas muy distintas.
- No usar por moda en un CRUD comun.

### Event-Driven / Pub-Sub

- Sirve para desacoplar workflows y distribuir integraciones.
- No usar sin idempotencia, observabilidad y ownership claro.

## Aplicacion Y Dominio

### Use Case / Application Service

- Coordina una operacion de negocio, transaccion y side effects.
- Evita meter aqui detalles de framework y SQL incidental.

### Domain Service

- Usar cuando una regla no pertenece claramente a una entidad/value object.
- No usar para esconder scripts transaccionales sin modelo.

### Strategy

- Buena para reglas intercambiables: pricing, auth, retries, serialization.
- No usar si solo hay una implementacion estable y ninguna variacion real.

### Factory

- Buena cuando la creacion valida invariants o encapsula armado complejo.
- No usar para reemplazar constructores triviales.

### Decorator

- Buena para logging, metrics, caching, authorization o retries.
- No usar si la composicion vuelve opaca la traza.

### Adapter

- Buena para encapsular APIs externas, SDKs o formatos legacy.
- No usar como wrapper vacio sin traduccion ni boundary.

### Observer

- Buena para eventos in-process de bajo alcance.
- No usar si el orden, error handling o consistencia importan demasiado.

## Persistencia

### Repository

- Buena para separar consultas/commands del dominio o casos de uso.
- No usar si solo agrega indirecciones sobre el ORM sin contrato claro.

### Unit Of Work

- Buena cuando varias escrituras deben confirmarse juntas.
- No usar si la transaccion real ya vive claramente en un caso de uso simple.

### Active Record

- Buena para apps chicas y CRUD veloz.
- Riesgo: mezclar persistencia con reglas de negocio complejas.

### Data Mapper

- Buena para dominios ricos y persistencia compleja.
- Riesgo: costo de mapping y boilerplate innecesario en apps chicas.

## Integracion Y Datos

### Outbox Pattern

- Buena cuando DB y evento externo deben quedar coordinados sin 2PC.
- No usar si no hay consumidores reales o no podes operar el relay.

### Saga / Process Manager

- Buena para workflows distribuidos largos con compensaciones.
- No usar si una sola transaccion local resuelve el problema.

### Cache-Aside

- Buena para lecturas calientes y tolerancia a stale data.
- No usar sin estrategia de invalidacion y metricas de hit rate.

## Operabilidad

### Circuit Breaker

- Bueno ante dependencias inestables.
- No usar sin timeouts, retries acotados y observabilidad.

### Retry With Backoff

- Bueno para fallas transitorias e IO externo.
- No usar sobre errores no idempotentes o permanentes.

## Regla De Seleccion

Antes de recomendar un patron, responder:

1. Que problema concreto resuelve?
2. Cual es la alternativa mas simple?
3. Que costo agrega en complejidad, debugging y onboarding?
4. Que evidencia hay de que el problema realmente existe?
