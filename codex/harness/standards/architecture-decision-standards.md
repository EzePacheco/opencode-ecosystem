# Architecture Decision Standards

Usar ADR cuando una decision afecta estructura, contratos, dependencias,
despliegue, datos, seguridad o forma de trabajo del equipo.

## Cuando Es Obligatorio

- Nueva dependencia productiva relevante.
- Cambio de arquitectura, patron, framework, proveedor o persistencia.
- Breaking change de API, schema, evento o workflow.
- Excepcion a un standard obligatorio.
- Decision dificil de revertir.

## Template

```markdown
# ADR: <titulo>

## Estado
Proposed | Accepted | Superseded | Deprecated | Rejected

## Contexto

## Decision

## Alternativas Consideradas

## Consecuencias

## Riesgos

## Rollback

## Links
```

## Reglas

- Un ADR explica por que, no solo que.
- No reabrir decisiones aceptadas en cada PR; crear ADR nuevo si cambia el contexto.
- Las excepciones deben tener alcance y fecha o condicion de reevaluacion.
- Si una decision queda obsoleta, marcarla como superseded y enlazar la nueva.
