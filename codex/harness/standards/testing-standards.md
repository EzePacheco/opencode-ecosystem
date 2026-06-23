# Testing Standards

Tests como evidencia de comportamiento, contratos y regresiones.

## Seleccion De Nivel

- Unit: reglas puras, transformaciones, validaciones y edge cases rapidos.
- Integration: DB, API interna, servicios, adapters, auth, permisos y colas.
- E2E: flujos criticos de usuario, integraciones reales y regresiones de UI.
- Visual o manual: layout, responsive, accesibilidad y estados interactivos.

## Obligatorio

- Bug reproducible: test de regresion que falla antes del fix cuando sea viable.
- Contrato publico: tests de casos positivos y negativos.
- Migracion DB: prueba de migracion y rollback cuando el stack lo soporte.
- Seguridad: tests de acceso denegado, ownership, input invalido y secrets no expuestos.
- UI critica: verificar estados loading, error, empty, success y responsive.

## Calidad De Tests

- Un test debe fallar por una razon clara.
- Evitar mocks que solo prueban que el mock fue configurado.
- Preferir fixtures legibles y builders chicos.
- Nombrar tests por comportamiento: `returns_403_when_user_does_not_own_resource`.
- No subir snapshots enormes sin intencion revisable.

## Cierre

Al cerrar una tarea, reportar:

- Checks ejecutados.
- Checks no ejecutados y motivo.
- Riesgo residual.
