# Standards Index

Indice operativo para cargar standards on-demand en opencode. Leer este archivo
antes de abrir standards completos.

| Standard | Cargar cuando | TL;DR |
| --- | --- | --- |
| `engineering-principles.md` | Decisiones transversales, calidad, dependencias, seguridad o trade-offs | Cambios chicos, contratos explicitos, seguridad en boundaries, complejidad justificada. |
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
- Para tareas chicas, este indice y las instrucciones activas suelen alcanzar.
- Para tareas medianas o grandes, cargar el standard completo despues de definir el plan.
- Si una tarea toca varios dominios, cargar solo los standards relevantes.
- Si aparece una excepcion a una regla obligatoria, documentarla como decision o deuda, no ignorarla.
