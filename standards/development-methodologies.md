# Development Methodologies

Standard transversal para decidir como trabajar: SDD, TDD, refactor
incremental, deuda tecnica y estrategia greenfield o legacy. La integracion con
opencode vive en `ai-workflow-standards.md`.

## Taxonomia

- **OBLIGATORIO**: debe cumplirse siempre salvo decision documentada.
- **RECOMENDADO**: default esperado, con excepcion justificable.
- **OPCIONAL**: usar segun contexto.
- **PROHIBIDO**: no hacer.

## Spec Driven Development

SDD significa escribir una especificacion antes de codear. La spec define
objetivo, alcance, inputs, outputs, edge cases y criterios de aceptacion.

En opencode, SDD empieza antes de la spec: el main thread conversa con el
usuario sobre la tarea o problema hasta llegar a un entendimiento compartido.
Recien entonces se escribe un plan y se decide si conviene resolver inline o
delegar a agentes.

### Niveles De Spec

- **Minima**: objetivo, inputs y outputs, y 1-2 criterios de aceptacion. Para bugs menores o ajustes chicos.
- **Estandar**: objetivo, contexto, alcance explicito, criterios numerados, edge cases y riesgos. Para features chicas, bugs no triviales y refactors acotados.
- **Completa**: incluye alternativas, trade-offs, migracion, impacto, rollback y compatibilidad. Para arquitectura, contratos publicos y refactors grandes.

### SDD Es Obligatorio Cuando

- La tarea toca 4 o mas archivos no mecanicos.
- La tarea cruza modulos, paquetes o repos.
- Cambia un contrato publico: API, schema, evento, interfaz, CLI o comportamiento documentado.
- Introduce una decision arquitectonica, dependencia productiva o patron nuevo.

### SDD Es Opcional Cuando

- Bug fix de pocas lineas en codigo bien conocido.
- Ajuste de copy o estilo trivial.
- Rename o move mecanico sin cambio de comportamiento.

### Formato Canonico

```markdown
# SPEC: <titulo>

## Objetivo

## Contexto

## Alcance
Si:
No:

## Inputs / Outputs

## Criterios De Aceptacion
1.
2.

## Edge Cases

## Riesgos
```

## Test Driven Development

TDD es recomendado para logica de negocio, bugs reproducibles, refactors
criticos y APIs publicas.

Reglas:

- El test debe fallar antes del fix cuando se esta capturando una regresion.
- Evitar TDD teatral: escribir tests despues y simular que guiaron la implementacion.
- Tests deben cubrir comportamiento y contratos, no implementacion accidental.

## Refactor Incremental

- Refactor y feature deben ir separados cuando el cambio deja de ser local.
- La regla de boy scout solo aplica cerca del cambio principal y sin alterar contratos.
- En legacy, refactorizar de paso esta prohibido salvo micro-limpiezas directamente necesarias y verificables.

## Deuda Tecnica

Toda deuda detectada que afecte mantenimiento, seguridad, tests, performance u
operabilidad debe registrarse en el sistema del repo: issue, ADR, debt log o
convencion local.

Formato sugerido:

```markdown
## DEBT: <titulo>
Ubicacion:
Severidad:
Impacto:
Decision:
```

## Estrategia Por Contexto

### Greenfield

- Aplicar standards desde el inicio.
- SDD obligatorio segun tamano.
- TDD recomendado para logica.
- Revisar el cambio completo contra standards.

### Legacy

- Aplicar standards al diff, no al archivo entero.
- Priorizar tests de regresion sobre redisenos ideales.
- No mezclar deuda con feature work.
- Registrar deuda descubierta.

### Mixto

- Codigo nuevo como greenfield.
- Toques a codigo viejo como legacy.
- Documentar fricciones que impiden aplicar standards.
