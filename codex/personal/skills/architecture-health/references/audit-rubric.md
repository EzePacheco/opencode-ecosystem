# Rúbrica de inspección arquitectónica

Usá estas preguntas para cada hotspot seleccionado. Contrastá hipótesis con código, consumidores, contratos y tests; un indicio no basta para declarar deuda. Conservá la arquitectura existente salvo falla concreta de su boundary. Preferí una corrección focal a una reorganización amplia.

La auditoría es bounded: declará qué hotspots y comportamientos inspeccionaste. Findings y decisiones `KEEP` se limitan a esa evidencia; no haber inspeccionado un área no demuestra que esté sana. No amplíes la muestra sólo para cubrir cada módulo o deployable.

## Responsabilidades y ownership

- **Cohesión / reasons to change:** ¿qué responsabilidades independientes tiene la unidad y por qué motivos reales cambiarían? ¿Mezcla concerns que evolucionan por separado? Muchos métodos o LOC no prueban baja cohesión; un archivo pequeño también puede mezclar ownership.
- **Ownership:** ¿quién posee el estado, protege cada invariant y puede escribirlo? ¿Una responsabilidad está dispersa o duplicada entre capas/componentes? ¿El lifecycle tiene dueño claro?
- **Change coupling:** con historial disponible, ¿concerns independientes cambian juntos repetidamente? Churn, autores y conflictos son pistas, no hallazgos. Sin historial, marcá la dimensión `unavailable`, sin penalizar.
- **Duplicación / reuse:** distinguí texto repetido de conceptos con la misma razón de cambio. Una abstracción compartida puede acoplar conceptos que evolucionan distinto. No recomendés DRY automáticamente.

## Boundaries y efectos

- **Dependency direction:** buscá imports que contradigan boundaries confirmados, deep imports que salten interfaces públicas, ciclos materiales, acoplamiento bidireccional y application/domain dependientes de adapters/UI sin motivo. Validá con tooling existente cuando lo haya.
- **State and effects:** ¿hay estado mutable compartido, efectos externos mezclados con lógica independiente, ownership ambiguo del lifecycle o reintentos/concurrencia relevantes? Mostrá la ruta observable del efecto.
- **Transaction / concurrency / idempotency:** sólo cuando el dominio lo requiera, preguntá qué atomicidad necesita, quién posee la transacción, qué races son posibles, qué locking/constraints existen y qué semántica tienen replay/retry. No sugieras transacciones, locks o idempotencia por defecto.
- **Contract / implementation parity:** cuando memory/SQL, fake/real, cache/authority, local/remote, proveedores u otros adapters representan el mismo contrato consumido, una interfaz o firma común sólo demuestra compatibilidad estructural: no demuestra paridad de atomicidad, fallas/rollback, retries/idempotencia, ausencia/not-found, ordering, validación, efectos, concurrencia o garantías de consistencia. Preguntá si los consumidores pueden confiar en los mismos invariants observables relevantes con cada implementación. Las implementaciones internas pueden diferir.
  - Si el hotspot material incluye varias implementaciones, contrastá de forma bounded uno o pocos comportamientos con invariants relevantes. Priorizá operaciones que mutan estado, tienen rutas de error o dependen de retries, transacciones o concurrencia. Seguí una ruta concreta de éxito y/o falla según el invariant; no compares todos los métodos mecánicamente.
  - `KEEP` sólo si la evidencia inspeccionada sostiene paridad suficiente para esos invariants; `REFACTOR` si demuestra una divergencia material; `VERIFY` si hay sospecha razonable y falta evidencia. No declares `KEEP` para todo el boundary por compartir interfaz, ownership conceptual, tests o capa. Si inspeccionaste una parte del contrato, acotá la conclusión a esa parte.
- **Testability:** ¿puede probarse el comportamiento focal sin levantar áreas no relacionadas? Setup/mocks excesivos son pista. Priorizá tests de invariants sobre detalles incidentales.

## Arquitectura, datos y enforcement

- **Architecture drift:** confrontá arquitectura declarada con estructura actual y autoridad vigente. Clasificá `ALIGNED`, `DRIFT`, `DOCUMENTATION_STALE` o `VERIFY` cuando importe. Un documento desactualizado no autoriza modificar código. Si falla un boundary, buscá primero su corrección focal.
- **Data / performance:** separá `ARCHITECTURAL / MAINTAINABILITY RISK` de `RUNTIME PERFORMANCE RISK`. Una query sospechosa justifica medición, no un finding de performance automático. Para riesgo runtime, pedí cardinalidad, volumen, latencia, frecuencia, hot path, EXPLAIN/plan, métricas o SLO conocido. No recomendés cache, índice, Redis, denormalización o lock por defecto. La complejidad estructural no demuestra lentitud.
- **Enforcement:** una vez confirmado el boundary, ¿puede comprobarse mecánicamente de modo barato y fiable? Ejemplos: forbidden imports, dirección de dependencias, API pública de módulo, contract parity, constraint de DB o architecture test existente. No codifiques una arquitectura equivocada.

## Archivos grandes y decisiones

Para cada archivo excepcionalmente grande, combiná responsibilities, reasons-to-change, fan-out, estado compartido, concerns entre capas, testability, churn y ownership. Clasificá su estructura como `KEEP`, `REFACTOR CANDIDATE` o `VERIFY`. LOC nunca basta. Evaluá por separado los sub-boundaries inspeccionados: una estructura global `KEEP` o `VERIFY` puede coexistir con un finding `REFACTOR` focal en paridad contractual. No uses la conclusión global para tapar esa divergencia ni generalices el finding focal al archivo entero. Si proponés refactor, separá por ownership, responsabilidad, lifecycle, reason-to-change o contract boundary; no propongas “dividir en archivos más chicos”.

`DO NOT REFACTOR` es una búsqueda activa de contraevidencia. Enumerá hotspots inspeccionados cuyo tamaño, churn, centralidad o complejidad superficial no demostró problema estructural suficiente. No rellenes artificialmente si todos muestran fallas. `DEFER` expresa una oportunidad con costo/beneficio insuficiente hoy; `VERIFY` expresa evidencia faltante. Los candidatos finales se ordenan por impacto y riesgo, nunca por tamaño.
