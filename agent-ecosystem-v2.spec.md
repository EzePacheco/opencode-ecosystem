
# SPEC 2: Ecosistema de Agentes - Roles y Capas de Orquestación Avanzadas

**Spec ID:** SPEC-2026-06-22-AGENT-ECOSYSTEM-V2
**Versión:** 1.0
**Estado:** Aprobado (por definir implementación)
**Fecha:** 2026-06-22
**Autor:** System (basado en análisis comparativo con frameworks SDD)

**Dependencias:**

* SPEC-2026-06-22-AGENT-ECOSYSTEM (Spec 1)

---

# 1. Objetivo

Extender el ecosistema actual con roles y capas de orquestación que mejoren la eficiencia, la calidad y el control humano en flujos de trabajo de Spec-Driven Development, tomando como referencia los frameworks más maduros de la industria:

* GitHub Spec Kit
* Amazon Kiro
* sdd-flow
* Spec Kitty
* BMAD Method

---

# 2. Contexto

El ecosistema actual (Spec 1) cubre los roles básicos de SDD:

* Planner
* Delegator
* Builders especializados
* Reviewers
* Reconciler
* Verifier

Sin embargo, el análisis comparativo con frameworks de referencia revela cuatro áreas de mejora que aumentan la eficiencia y la calidad sin modificar la arquitectura base.

| Área                              | Estado actual                                                                       | Mejora propuesta                                              |
| --------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Eficiencia en tareas pequeñas     | Todas las tareas pasan por el flujo completo de 10 pasos (costoso en tiempo/tokens) | Crear modo Mini-SDD que salte revisores y use un solo builder |
| Contexto del builder              | Los builders solo reciben el spec y @standards/INDEX.md                             | Añadir Reference Files (Gold Standards) al handoff            |
| Arquitectura de proyectos grandes | El Planner hace diseño y descomposición de tareas                                   | Introducir rol opcional Tech Lead                             |
| Aislamiento de contexto           | Todos los builders trabajan en el mismo workspace                                   | Introducir Worktree Manager                                   |
| Control humano                    | Sistema completamente autónomo                                                      | Añadir Human-in-the-loop Gate opcional                        |

---

# 3. Alcance

## YES (Dentro de alcance)

* Implementar el modo Mini-SDD en Delegator.
* Añadir Reference Files al handoff del Delegator.
* Crear el rol Tech Lead (opcional, solo para L/XL).
* Crear el rol Worktree Manager (opcional).
* Añadir Human-in-the-loop Gate opcional en Delegator.
* Actualizar plan.md para soportar los nuevos modos y roles.
* Actualizar SKILL.md con la nueva documentación.

## NO (Fuera de alcance)

* Modificar la arquitectura de los builders existentes.
* Migrar a otro sistema de control de versiones.
* Cambiar los permisos de los agentes existentes.
* Automatización de despliegue (ya cubierto por MCPs).
* Integración con sistemas de tickets (ya cubierto por MCPs).

---

# 4. Contratos Afectados

## build.md (Delegator)

Añade:

* Modo Mini-SDD (`mini: true`)
* Campo `reference_files`
* Opción `human_gate: true`
* Invocación opcional a:

  * tech-lead
  * worktree-manager

## plan.md (Planner)

Añade:

* Clasificación explícita de tamaño:

  * S
  * M
  * L
  * XL

Reglas:

* Si `size = S` → `mini: true`
* Si `size = L` o `XL` → puede delegar diseño a Tech Lead

## Handoff a Builders

Ahora incluye:

```yaml
reference_files:
  - path/to/example/file
```

## Handoff a Verifier

Si `human_gate` está activo:

* El verifier solo se ejecuta después de la aprobación humana.

## SKILL.md

Añade secciones sobre:

* Mini-SDD
* Reference Files
* Tech Lead
* Worktree Manager
* Human-in-the-loop Gate

---

# 5. Edge Cases y Riesgos

| Caso                                                | Riesgo                                      | Mitigación                                         |
| --------------------------------------------------- | ------------------------------------------- | -------------------------------------------------- |
| Mini-SDD se usa para tareas que en realidad son M/L | Calidad insuficiente por saltarse revisores | El Planner debe clasificar el tamaño con evidencia |
| Reference Files desactualizados                     | El builder sigue patrones obsoletos         | El Delegator valida existencia antes de pasarlos   |
| Tech Lead contradice el spec                        | Desviación de objetivos                     | Produce una revisión, no un nuevo spec             |
| Worktrees no eliminados                             | Acumulación de directorios                  | Limpieza automática al finalizar                   |
| Human Gate sin respuesta                            | Flujo bloqueado                             | Timeout configurable                               |

---

# 6. Acceptance Criteria

## A1 — Mini-SDD

Dado un spec marcado como:

```yaml
size: S
```

El Delegator ejecuta:

```text
builder
→ code-reviewer
→ verifier
```

Sin:

* architecture-reviewer
* security-reviewer

---

## A2 — Reference Files

El handoff incluye:

```yaml
reference_files:
  - src/auth/login.go
  - src/users/service.go
```

El builder debe indicar explícitamente que consultó dichos archivos.

---

## A3 — Tech Lead

Para specs:

```yaml
size: L
```

o

```yaml
size: XL
```

El Planner invoca:

```text
tech-lead
```

La salida (`design_delta`) se utiliza para descomponer tareas.

---

## A4 — Worktree Manager

El Delegator puede invocar:

```text
worktree-manager
```

que:

* crea un worktree por slice
* elimina el worktree al finalizar

---

## A5 — Human-in-the-loop

Si:

```yaml
human_gate: true
```

El flujo se pausa después de:

```text
code-reviewer
```

y espera aprobación humana antes de:

```text
reconciler
→ verifier
```

---

## A6 — Documentación

SKILL.md documenta:

* Mini-SDD
* Reference Files
* Tech Lead
* Worktree Manager
* Human-in-the-loop

con ejemplos de uso.

---

# 7. Implementation Slices

## Slice 1 — Mini-SDD

**Responsable:** Delegator (`build.md`)

### Tareas

1. Leer:

```yaml
size: S|M|L|XL
```

2. Si:

```yaml
size: S
```

ejecutar:

```text
builder
→ code-reviewer
→ verifier
```

3. Si:

```yaml
size: M|L|XL
```

ejecutar flujo completo.

### Output

* build.md actualizado

---

## Slice 2 — Reference Files

**Responsables:**

* Delegator
* Builders

### Tareas

Añadir al handoff:

```yaml
reference_files: []
```

Actualizar:

* backend-builder.md
* frontend-builder.md
* database-builder.md
* devops-builder.md

Actualizar plan.md para sugerir reference_files.

### Output

* prompts actualizados

---

## Slice 3 — Tech Lead (Opcional)

**Responsable:** Nuevo subagente

### Configuración

```yaml
model: gpt-5.5
variant: xhigh
temperature: 0.1
```

### Reglas

Recibe:

* spec
* reference_files

Produce:

```yaml
design_delta
```

No:

* escribe código
* modifica el spec

### Cambios

Actualizar:

* plan.md
* build.md

### Output

* tech-lead.md
* plan.md actualizado
* build.md actualizado

---

## Slice 4 — Worktree Manager (Opcional)

**Responsable:** Nuevo subagente

### Configuración

```yaml
model: gpt-5.4-mini
variant: medium
temperature: 0.1
```

### Reglas

Antes del builder:

```text
create worktree
```

Durante ejecución:

```text
handoff worktree path
```

Al finalizar:

```text
commit
merge
cleanup
```

### Activación

```yaml
parallelism > 1
```

### Output

* worktree-manager.md
* build.md actualizado

---

## Slice 5 — Human-in-the-loop Gate

**Responsable:** Delegator

### Campo nuevo

```yaml
human_gate: true|false
```

### Flujo

```text
builder
↓
code-reviewer
↓
HUMAN GATE
↓
reconciler
↓
verifier
```

### Reglas

* Mostrar resumen
* Mostrar diff
* Esperar confirmación

Timeout sugerido:

```yaml
critical: 24h
urgent: 4h
```

### Output

* build.md actualizado

---

## Slice 6 — Documentación y SKILL

**Responsable:** documentation-writer

### Actualizar SKILL.md

Incluir:

1. Mini-SDD
2. Reference Files
3. Tech Lead
4. Worktree Manager
5. Human-in-the-loop

### Actualizar plan.md

Para decidir:

```yaml
mini
human_gate
reference_files
```

### Output

* documentación actualizada

---

# 8. Verification Commands / Evidence Expected

| Slice   | Evidencia esperada                                          |
| ------- | ----------------------------------------------------------- |
| Slice 1 | Spec size=S omite architecture-reviewer y security-reviewer |
| Slice 2 | Builder menciona reference_files consultados                |
| Slice 3 | Planner invoca tech-lead y pasa design_delta                |
| Slice 4 | Worktrees creados y eliminados correctamente                |
| Slice 5 | Flujo se pausa esperando aprobación humana                  |
| Slice 6 | SKILL.md documenta todos los nuevos roles y modos           |

---

# 9. Open Questions

## Q1

¿Tech Lead debe ser un subagente o una responsabilidad adicional del Planner?

**Recomendación:** subagente.

---

## Q2

¿Worktree Manager debe resolver merges automáticamente?

**Recomendación inicial:**

* detectar conflicto
* reportar
* detener flujo

---

## Q3

¿Timeout adecuado para Human Gate?

**Recomendación:**

```yaml
critical: 24h
urgent: 4h
```

Configurable por spec.

---

## Q4

¿Reference Files deben ser obligatorios para ciertos dominios?

Ejemplos:

* autenticación
* billing
* seguridad

**Recomendación:** decisión del Planner según contexto.

---

# 10. Relación con Spec 1

| Item de Spec 1        | Impacto                                                       |
| --------------------- | ------------------------------------------------------------- |
| Modelos y variantes   | Sin cambios. Tech Lead usa xhigh. Worktree Manager usa medium |
| Bucle de verificación | Se mantiene. Human Gate ocurre antes                          |
| Agente QA             | Sin cambios                                                   |
| MCPs                  | Tech Lead y Worktree Manager pueden utilizarlos               |

---

# Resultado Arquitectónico

```text
                 Planner
                    │
          ┌─────────┴─────────┐
          │                   │
       Tech Lead          (opcional)
          │
          ▼
      Delegator
          │
     Human Gate?
          │
          ▼
  ┌──────────────────┐
  │ Worktree Manager │
  └──────────────────┘
          │
          ▼
       Builders
          │
          ▼
    Code Reviewer
          │
    Human Gate?
          │
          ▼
      Reconciler
          │
          ▼
       Verifier
```
