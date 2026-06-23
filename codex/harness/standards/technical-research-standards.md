# Technical Research Standards

## Objetivo

Usar investigacion externa para complementar conocimiento local sin degradar privacidad, calidad ni trazabilidad.

## Cuando Buscar

- Versiones recientes o cambios de framework.
- Conceptos o patrones no cubiertos localmente.
- Errores raros, mensajes poco claros o sintomas no familiares.
- Comparacion de herramientas, ORMs, DBs, providers o practicas operativas.

## Jerarquia De Fuentes

1. Codigo, standards, ADRs y docs del repo.
2. Documentacion oficial, specs, RFCs, changelogs y migration guides.
3. Docs de vendor, SDK o cloud provider.
4. Issues oficiales, discussions del proyecto y ejemplos mantenidos como contexto no normativo.
5. Stack Overflow, blogs y videos como señal secundaria.

## Reglas

- Official docs first para comportamiento normativo.
- Comunidad sirve para descubrir terminology, edge cases, workarounds y pitfalls.
- Issues, discussions y ejemplos pueden orientar, pero siguen siendo senal no normativa hasta corroborarlos con codigo, docs oficiales, specs, RFCs, changelogs o migration guides antes de cambiar la recomendacion final.
- No elevar una respuesta de Stack Overflow a recomendacion final sin corroboracion.
- Distinguir hechos confirmados, inferencias y opinion comunitaria.
- Citar fuente y version cuando la recomendacion pueda cambiar segun release.

## Sanitizacion

- No incluir secretos, tokens, nombres de clientes, repos privados o URLs internas.
- Reducir stack traces a mensajes anonimizados y sintomas tecnicos.
- Consultar por concepto y error, no por contexto sensible.

## Consultas Utiles

- `official docs <framework> transaction isolation`
- `<orm> N+1 eager loading official docs`
- `<tool> migration guide <major version>`
- `<provider> retry idempotency best practices`

## Stack Overflow Y Similares

Usarlos para:

- descubrir nombres correctos del problema;
- identificar anti-patterns comunes;
- encontrar reproducciones pequenas;
- comparar sintomas con otros casos.

No usarlos para:

- decisiones normativas sin corroboracion;
- seguridad sensible;
- configuracion critica de produccion si no hay fuente oficial.

## Salida Esperada

Cuando la investigacion externa influya la respuesta, resumir:

- que se verifico localmente;
- que se confirmo en fuentes oficiales;
- que quedo como senal comunitaria o hipotesis;
- como cambia o no la recomendacion final.
