# Operability Standards

## Produccion Operable

Un cambio operable se puede desplegar, observar, depurar y revertir.

## Checklist

- Health checks reflejan dependencias criticas.
- Logs ayudan a diagnosticar sin exponer secretos.
- Metricas o eventos para flujos importantes.
- Alertas accionables, no ruido.
- Rollback o forward fix definido para cambios riesgosos.
- Config y secretos fuera del codigo.
- Runbook para operaciones no obvias.

## Incidentes

Postmortem liviano:

- Que paso.
- Impacto.
- Causa.
- Deteccion.
- Resolucion.
- Prevencion.

## Prohibido

- Deploy riesgoso sin plan de rollback.
- Alertas que nadie atiende.
- Logs con PII o secrets.
