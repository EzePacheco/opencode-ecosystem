# Engineering Principles

Principios no negociables para trabajo de software asistido por LLMs.

## Reglas

- Cambios chicos y verificables ganan sobre reescrituras amplias.
- Los contratos publicos se tratan como producto: API, schema, eventos, CLI, tipos exportados y UX observable.
- La seguridad vive en los boundaries: input externo, auth, permisos, secretos, multi-tenancy, integraciones y supply chain.
- No agregar abstracciones hasta que reduzcan complejidad real o dupliquen un patron probado.
- Preferir convenciones existentes del repo sobre estilo personal.
- Toda excepcion relevante se documenta como ADR, debt log o nota de tarea.
- El codigo que no se puede verificar debe salir con riesgo explicito.

## Decision Check

Antes de implementar:

1. Que contrato cambia?
2. Que puede romperse?
3. Como se verifica?
4. Que deuda se acepta?
5. Que rollback existe?

## Prohibido

- Cambios destructivos sin aprobacion explicita.
- Introducir dependencias productivas sin justificar mantenimiento, seguridad y alternativa.
- Mezclar feature, refactor y migracion grande en un solo cambio sin plan.
- Resolver deuda no relacionada como side effect.
