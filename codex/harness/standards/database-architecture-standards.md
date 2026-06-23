# Database Architecture Standards

## Reglas

- Constraints reales para invariantes criticas.
- Migraciones reversibles cuando sea razonable.
- Backfills en batches para tablas grandes.
- Indices alineados a queries reales.
- Transacciones alrededor de cambios que deben ser atomicos.
- No esconder N+1 bajo helpers u ORM.

## Migraciones

Checklist:

- Puede correr en produccion sin bloquear demasiado?
- Tiene rollback o plan de forward fix?
- Maneja datos existentes?
- Cambia contrato de API o app?
- Necesita deploy en fases?

## Prohibido

- Drop o rename destructivo sin backup, migracion o aprobacion.
- Confiar solo en validacion de app para integridad critica.
- Seeds con datos sensibles reales.
