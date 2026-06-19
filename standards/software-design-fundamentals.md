# Software Design Fundamentals

## Objetivo

Usar fundamentos antes de elegir patrones, frameworks o abstracciones.

## Preguntas Base

- Cual es el objetivo real?
- Cual es el contrato observable?
- Donde viven los invariants?
- Quien es owner de cada dato?
- Que boundary separa reglas de negocio, IO y efectos externos?
- Que cambio futuro es mas probable?
- Que nivel de complejidad puede sostener el equipo?

## Heuristicas

- Alta cohesion y bajo acoplamiento ganan sobre capas teoricas bonitas.
- Mantener invariants cerca del lugar donde pueden romperse.
- Preferir flujo de datos claro a magia de framework.
- Separar policy de mechanism: reglas de negocio aparte de transporte, UI o ORM.
- Encapsular complejidad repetida; no encapsular solo por anticipacion.
- Dependencias hacia adentro cuando haya dominio claro; hacia afuera solo para adaptadores.
- Diseño simple primero; abstraccion despues de la segunda o tercera repeticion significativa.

## Boundaries Minimos

- Entrada/salida: HTTP, CLI, jobs, eventos, UI.
- Casos de uso: coordinan reglas, transacciones y efectos.
- Dominio: invariants, politicas, value objects, decisiones.
- Infraestructura: DB, cache, colas, terceros, filesystem.

## Señales De Buena Estructura

- Un cambio de regla de negocio no exige tocar transporte y persistencia a la vez.
- Tests de reglas no necesitan red ni DB real.
- Los nombres reflejan el dominio, no la libreria.
- Los errores se propagan con significado, no como strings anonimos.
- La estructura ayuda a encontrar ownership rapido.

## Smells

- God service, god component o helper global multiuso.
- Controladores o handlers con reglas de negocio densas.
- Dominio acoplado a ORM, framework web o UI toolkit.
- Abstracciones que solo envuelven una llamada sin reducir complejidad.
- Carpetas por tipo que obligan a saltar por todo el repo para seguir una feature.

## Arquitecturas Comunes

### Layered

- Buena para CRUD y equipos chicos.
- Riesgo: services gigantes y dominio anemico.

### Vertical Slice

- Buena cuando las features cambian mas que las capas.
- Riesgo: duplicacion accidental si faltan convenciones.

### Hexagonal / Ports And Adapters

- Buena cuando hay multiples integraciones o alta necesidad de testear dominio aislado.
- Riesgo: sobreingenieria en apps simples.

### Modular Monolith

- Buena cuando se necesita separacion fuerte sin costo operativo de microservicios.
- Riesgo: modulos falsos sin boundaries reales.

### Microservices

- Usar solo si hay necesidad real de despliegue, escalado, aislamiento o ownership independiente.
- Riesgo: multiplicar latencia, contratos y carga operativa demasiado pronto.

## Regla De Cierre

Si una decision no mejora claridad, seguridad, testabilidad, operabilidad o cambio futuro probable, probablemente no merece una nueva abstraccion.
