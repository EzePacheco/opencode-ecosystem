# Security Engineering Standards

Aplicar cuando el cambio toca input externo, auth, permisos, secretos, datos
sensibles, integraciones, browser, archivos, red o supply chain.

## Principios

- Least privilege.
- Secure defaults.
- Fail closed.
- Defense in depth.
- Trust boundaries explicitos.
- Auditoria de acciones sensibles.

## Checklist

- Validar input en boundary.
- Autorizar por recurso, no solo por rol global.
- Verificar ownership y tenancy.
- No loggear secretos, tokens, PII o credenciales.
- Proteger CSRF, XSS, SSRF, path traversal e injection segun superficie.
- Rate limit para endpoints o acciones abusables.
- Timeouts y retries seguros para integraciones externas.
- Dependencias nuevas con mantenimiento y licencia razonables.

## Prohibido

- Secretos en repo, prompts, fixtures reales o logs.
- Confiar en datos del cliente para permisos.
- Usar allowlists o denylists incompletas como unica defensa.
- Degradar seguridad por conveniencia sin ADR y aprobacion.
