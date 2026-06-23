# API Contract Standards

## Contratos

Un contrato API incluye endpoint, metodo, auth, request, response, errores,
paginacion, versionado, headers relevantes y compatibilidad.

## Reglas

- Cambios breaking requieren spec completa, compatibilidad o versionado.
- Errores deben tener codigo estable y mensaje seguro.
- Paginacion explicita para listas no triviales.
- Webhooks o eventos deben ser versionados e idempotentes.
- Validar input y devolver errores accionables.
- Documentar cambios observables.

## Error Shape Sugerido

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "Resource not found",
    "request_id": "..."
  }
}
```

## Review

- Casos positivos.
- Casos negativos.
- Compatibilidad.
- Seguridad de datos.
- Observabilidad.
