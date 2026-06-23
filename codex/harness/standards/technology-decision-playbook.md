# Technology Decision Playbook

## Objetivo

Elegir lenguaje, framework, ORM, DB o tooling por constraints y trade-offs reales.

## Checklist Base

- Problema y escala actual.
- Escala probable en 12-24 meses.
- Skills del equipo y costo de onboarding.
- Ecosistema, mantenimiento y comunidad.
- Observabilidad, seguridad y operabilidad.
- Costo total: licencias, infraestructura, debugging y hiring.
- Lock-in y facilidad de migracion.

## Lenguaje / Framework

- Preferir el camino idiomatico del stack salvo evidencia fuerte en contra.
- No pelear contra el framework si su convencion principal resuelve el 80% del caso.
- Separarse de la convencion solo cuando mejora testing, boundaries o mantenibilidad claramente.

## ORM / Data Access

- Elegir por fit con complejidad del dominio y visibilidad de queries.
- Validar transacciones, eager/lazy loading, migraciones, tracing y escape hatches a SQL.
- Si el ORM oculta demasiado, incorporar patrones o consultas explicitas antes de que aparezcan N+1 y writes ambiguos.

## Base De Datos

- Elegir por access patterns, consistencia requerida, operacion y equipo.
- Relacional cuando hay invariants, joins, transacciones y reporting.
- Documento cuando el shape cambia mucho y las relaciones son limitadas.
- KV/cache cuando prima latencia y simplicidad de lectura/escritura.
- Search engine para busqueda, no como source of truth transaccional.

## Messaging / Async

- Usar colas o eventos cuando el desacople y la resiliencia compensan la complejidad.
- Validar ordering, retries, idempotencia, DLQ, observabilidad y replay.

## DevOps / Platform

- Preferir la opcion mas operable que el equipo pueda sostener.
- No adoptar Kubernetes, service mesh o multi-cloud por prestigio.
- CI/CD debe reflejar el riesgo real del sistema, no solo ejecutar comandos por costumbre.

## Formato De Recomendacion

Para decisiones no triviales, comparar al menos:

1. opcion simple / conservadora;
2. opcion estructurada / escalable;
3. recomendacion con condiciones de cambio.

## Señales De Mala Decision

- Se eligio por moda o porque "asi se hace".
- El equipo no puede debugearlo ni operarlo.
- La complejidad resuelve problemas imaginarios.
- No hay plan de rollback o migracion.
