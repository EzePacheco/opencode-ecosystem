# Repo profiles

La clasificación combina complejidad, riesgo, contracts, ownership, lifecycle y operación. LOC, cantidad de archivos y número de documentos son señales auxiliares, no el criterio.

## D1 — simple

Un propósito principal, pocos boundaries, bajo blast radius y feedback directo. Baseline habitual: README, código/configuración y tests sólo donde protejan behavior relevante. Un AGENTS pequeño o contributor contract puede justificarse por un gap observable de navegación, reglas locales o portabilidad del equipo, aunque el repo sea simple. Colaboración no eleva el perfil: aplicá la dimensión TEAM PORTABILITY de la rúbrica por separado.

Si el contributor path existente es suficiente, incluso en D1 colaborativo, es válido concluir `DO NOT ADD AGENTS`, `DO NOT ADD CONTRIBUTING` y `DO NOT ADD skills`.

No agregues specs, ADRs, architecture docs, routers o harness ceremonial por profesionalismo.

## D2 — material

Hay módulos o runtimes con ownership distinto, persistence, migrations, schemas, APIs, contracts externos o decisiones materiales. Puede justificar documentación de arquitectura, ADRs, specs, contracts y AGENTS local, sólo donde aclaren decisiones o límites reales.

## D3 — complejo/riesgoso

Hay seguridad, autorización, tenancy, dinero, PII, migraciones irreversibles, compatibilidad pública, múltiples deployables/repos, operación continua, on-call o alto blast radius. Puede justificar arquitectura separada por concerns reales, security/operations docs, lifecycle de ADR/spec, contract checks, runbooks y diagnósticos.

## Casos especiales

### Library

Priorizar API pública, compatibilidad, versionado, changelog contractual y consumer tests cuando existan consumers reales. No exigir runtime operativo.

### Documentation/planning

Priorizar authority, navegación, estado current/future/historical, links y duplicación. No exigir build, tests o architecture docs de software.

### Monorepo

Clasificar el root y las unidades relevantes por separado. Buscar ownership, comandos canónicos, boundaries y configuración compartida; no asumir uniformidad.

### Multi-repo product

Separar coordinación de autoridad técnica. Deduplicar Git roots. Auditar profundamente sólo los repos donde contracts, riesgo, divergencias o selección explícita lo justifiquen.

## Señal de cambio de perfil

Subí de profundidad cuando aparezca un boundary con mayor blast radius o incertidumbre, no cuando falte una herramienta habitual. Bajá la profundidad cuando la evidencia muestre un flujo directo y suficientemente protegido.
