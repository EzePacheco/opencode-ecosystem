# Standards Index

Indice operativo para cargar standards on-demand en opencode. Leer este archivo
antes de abrir standards completos.

| Standard | Cargar cuando | TL;DR |
| --- | --- | --- |
| `engineering-principles.md` | Decisiones transversales, calidad, dependencias, seguridad o trade-offs | Cambios chicos, contratos explicitos, seguridad en boundaries, complejidad justificada. |
| `software-design-fundamentals.md` | Dudas de modelado, boundaries, cohesion, coupling, capas, modularidad o complejidad | Empezar por invariantes, ownership, boundaries y costo de complejidad antes de elegir patrones o herramientas. |
| `patterns-catalog.md` | Patron de diseno, patron arquitectonico, integracion, persistencia o comparacion entre alternativas | Elegir patrones por problema y trade-off, no por moda; incluir cuando no usar cada patron. |
| `repository-organization-standards.md` | Organizacion de repo, carpetas, modulos, monorepo, feature folders o layering | La estructura debe reflejar ownership, boundaries, despliegue, testing y cambios frecuentes. |
| `technology-decision-playbook.md` | Elegir lenguaje, framework, ORM, base de datos, cache, cola, cloud o herramienta de DevOps | Comparar opciones por constraints, team fit, operabilidad, costo y lock-in antes de decidir. |
| `technical-research-standards.md` | Falta contexto, hay dudas version-specific, conceptos nuevos o hace falta validar con web | Official docs first; comunidad como senal secundaria; queries sanitizadas; distinguir hechos de opiniones. |
| `architecture-decision-standards.md` | ADRs, decisiones arquitectonicas, excepciones a reglas obligatorias o conflictos | Registrar contexto, alternativas, decision, consecuencias y rollback cuando el cambio sea estructural. |
| `development-methodologies.md` | Planificacion, SDD, TDD, deuda tecnica, legacy, refactor o estrategia de entrega | Spec antes de codear cuando el riesgo lo amerita; tests segun contrato y regresion; refactor acotado; deuda documentada. |
| `testing-standards.md` | Tests, regresiones, verificacion, CI o cierre de tareas riesgosas | Tests cubren contratos y regresiones; elegir unit, integration o E2E segun riesgo. |
| `security-engineering-standards.md` | Auth, permisos, secretos, tokens, input externo, XSS, CSRF, SSRF, supply chain o privacidad | Defense in depth, least privilege, secure defaults, fail closed y boundaries explicitos. |
| `backend-architecture-standards.md` | Controllers, services, use cases, jobs, colas o logica backend | Separar transporte, casos de uso, persistencia y efectos externos; idempotencia en operaciones criticas. |
| `api-contract-standards.md` | Endpoints, clientes, errores, paginacion, versionado, webhooks o contratos publicos | Contratos estables, errores canonicos, compatibilidad y versionado explicito. |
| `database-architecture-standards.md` | Schema, migraciones, queries, transacciones, ORM, indices o seeds | Constraints reales, migraciones reversibles, transacciones claras e indices alineados a queries. |
| `frontend-architecture-standards.md` | UI, componentes, formularios, routing, estado o API clients | UI por feature, estado local primero, API client centralizado, accesibilidad y responsive verificables. |
| `distributed-systems-standards.md` | Colas, pub/sub, webhooks, retries, DLQ, circuit breakers o integraciones externas | Asumir falla, idempotencia desde diseno, backpressure, observabilidad y contratos versionados. |
| `operability-standards.md` | CI/CD, deploy, secrets, logs, metricas, health checks, incidentes o performance | Produccion operable: rollback, alertas accionables, runbooks y logs utiles. |
| `ai-workflow-standards.md` | Uso de opencode, agents, skills, MCP, contexto, verificacion, handoffs o guardrails | Main thread orquesta; skills y references se cargan on-demand; subagentes solo cuando aportan aislamiento, paralelismo o review fresca. |

## Reglas De Uso

- No abrir todos los standards por las dudas.
- Para mentoring, cargar fundamentals/patterns/repository-organization/technology-decision/research solo cuando agreguen signal real a la respuesta.
- Para tareas chicas, este indice y las instrucciones activas suelen alcanzar.
- Para tareas medianas o grandes, cargar el standard completo despues de definir el plan.
- Si una tarea toca varios dominios, cargar solo los standards relevantes.
- Si aparece una excepcion a una regla obligatoria, documentarla como decision o deuda, no ignorarla.
