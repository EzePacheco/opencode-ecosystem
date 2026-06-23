# SPEC: Ecosistema de Agentes - Mejoras y Unificaciones

## Metadata

- **Spec ID:** `SPEC-2026-06-22-AGENT-ECOSYSTEM`
- **Versión:** `1.0`
- **Estado:** `Aprobado (por definir implementación)`
- **Fecha:** `2026-06-22`
- **Autor:** `System (basado en análisis y recomendaciones)`

## 1. Objetivo

Unificar, optimizar y extender el ecosistema de agentes de desarrollo para convertirlo en un sistema de ingeniería de software autónomo, seguro y eficiente, siguiendo los estándares de la industria: **Spec-Driven Development**, **Multi-Agent Verification** y bucles de calidad.

## 2. Contexto

El sistema actual consta de 17 agentes/prompts que cubren desde mentoría hasta verificación final, pasando por planificación, construcción especializada y revisión adversaria.

Se ha identificado que:

- El flujo de trabajo es casi completo, pero carece de bucles de retroalimentación entre verificación y reconciliación.
- Los handoffs entre agentes son textuales y ambiguos, especialmente entre `code-reviewer` y `reconciler`.
- Falta un agente dedicado a pruebas (QA) que orqueste herramientas de E2E.
- La capa de MCPs está subutilizada, limitando la integración con repositorios, despliegues y monitoreo.
- El modelo `gpt-5.3-codex` en `explore-mini` está deprecado.

## 3. Alcance (YES / NO)

| YES (Dentro de alcance) | NO (Fuera de alcance) |
| --- | --- |
| Ajuste de modelos, variantes y temperaturas | Rediseño completo de la arquitectura de agentes |
| Creación del agente `qa-builder` | Migración a otro framework de orquestación |
| Unificación de formato de handoffs (estructurados) | Implementación de memoria persistente (queda en `deny`) |
| Implementación del bucle `Verifier ↔ Reconciler` | Cambios en los permisos base de los agentes (se mantienen) |
| Adición de MCPs recomendados (`GitHub`, `Filesystem`, `Sequential Thinking`, `Deployment`, `PostHog/Sentry`) | Integración con otros sistemas externos no mencionados |
| Migración de `explore-mini` a `gpt-5.4-mini` | Automatización de tests de carga/rendimiento (fuera de alcance inicial) |
| Actualización de `Delegator` y `Planner` para soportar nuevos agentes y MCPs |  |
| Documentación de los nuevos flujos en `SKILL.md` |  |

## 4. Contratos Afectados

| Contrato | Impacto |
| --- | --- |
| Handoff `code-reviewer → reconciler` | Pasa de texto libre a formato estructurado (JSON con `findings[]`). |
| Handoff `verifier → reconciler` | Ahora puede recibir `rework-required` y desencadenar un bucle. |
| `build.md` (Delegator) | Añade paso `10.1` para bucle de verificación y paso `4.1` para invocar `qa-builder`. |
| `plan.md` (Planner) | Debe incluir en sus specs la necesidad de pruebas E2E y orquestar `qa-builder` cuando corresponda. |
| `verifier.md` | Debe ejecutar `npx playwright test` si el spec lo requiere. |

## 5. Edge Cases y Riesgos

| Caso | Riesgo | Mitigación |
| --- | --- | --- |
| Bucle de verificación infinito | Gastar tokens y tiempo sin resolución | Máximo de 3 iteraciones; escalar a humano si persiste. |
| `reconciler` recibe hallazgos en formato incorrecto | Falla al aplicar cambios | `code-reviewer` debe generar siempre el formato estructurado; `reconciler` debe validar el esquema. |
| `qa-builder` no tiene acceso a MCPs | No puede generar ni ejecutar pruebas | Asegurar que el agente tenga permisos para invocar MCPs configurados en el sistema. |
| El modelo `gpt-5.4-mini` en `explore-mini` no es suficiente para tareas complejas | Exploración superficial | Mantener `explore` principal con `gpt-5.5`; `explore-mini` solo para tareas muy acotadas. |

## 6. Acceptance Criteria

| Criterio | Verificación |
| --- | --- |
| A1: Formato de hallazgos estructurado | `code-reviewer` produce salida en JSON con campos `severity`, `file`, `line`, `problem`, `suggestion`. |
| A2: Bucle de verificación | Si `verifier` devuelve `rework-required`, `reconciler` recibe los hallazgos y aplica cambios; `verifier` se ejecuta de nuevo hasta `accepted` o 3 intentos. |
| A3: Agente QA | Existe `qa-builder.md` que, dado un spec, genera y ejecuta pruebas E2E con Playwright, reportando cobertura y fallos. |
| A4: MCPs integrados | `GitHub MCP`, `Filesystem MCP`, `Sequential Thinking MCP`, `Deployment MCP` (según plataforma), y `PostHog/Sentry MCP` están configurados y son invocables por los agentes correspondientes. |
| A5: Modelos unificados | Todos los agentes usan modelos de la familia `GPT-5.4/5.5`; `explore-mini` usa `gpt-5.4-mini`. |
| A6: Documentación actualizada | `SKILL.md` refleja los nuevos flujos, incluyendo el bucle de verificación y la integración con MCPs. |

## 7. Implementation Slices

### Slice 1: Unificación de Modelos

- **Responsable:** Mantenimiento del sistema
- **Tareas:**
  - Cambiar en `explore-mini.md` el modelo de `gpt-5.3-codex` a `gpt-5.4-mini`.
  - Revisar que ningún otro agente use versiones antiguas de GPT (solo `gpt-5.5` y `gpt-5.4-mini`).
- **Output:** Archivos YAML actualizados.

### Slice 2: Formato Estructurado de Hallazgos

- **Responsable:** `code-reviewer`
- **Tareas:**
  - Modificar `code-reviewer.md` para que su salida sea un objeto JSON con array `findings`.
  - Actualizar `reconciler.md` para parsear y aplicar ese formato.
- **Output:** Archivos de prompts actualizados.

### Slice 3: Bucle de Verificación

- **Responsable:** `Delegator` (`build.md`)
- **Tareas:**
  - Añadir paso `10.1`: si `verifier` devuelve `rework-required`, pasar hallazgos a `reconciler`.
  - Añadir paso `10.2`: ejecutar `verifier` de nuevo después de `reconciler`.
  - Añadir paso `10.3`: repetir hasta `accepted` o 3 iteraciones; escalar a humano.
- **Output:** `build.md` actualizado.

### Slice 4: Agente QA (`qa-builder`)

- **Responsable:** Nuevo subagente
- **Tareas:**
  - Crear `qa-builder.md` con configuración: modelo `gpt-5.5`, variante `high`, temperatura `0.1`.
  - Definir reglas:
    - Orquestar `@playwright/mcp` y `@joekannan/playwright-framework-mcp`.
    - Generar tests E2E a partir del spec.
    - Ejecutar tests y reportar cobertura/fallos.
  - Actualizar `Delegator` para invocar `qa-builder` cuando el spec lo requiera.
- **Output:** Nuevo archivo `qa-builder.md` y actualización de `build.md`.

### Slice 5: Integración de MCPs

- **Responsable:** Configuración del sistema
- **Tareas:**
  - Instalar y configurar `Filesystem MCP` y `Sequential Thinking MCP`.
  - Instalar `Deployment MCP` (según plataforma: `Vercel`, `Render`, `Cloudflare`, etc.).
  - Instalar `PostHog` o `Sentry MCP` para monitoreo de errores en producción.
  - Actualizar permisos de los agentes que necesiten invocar estos MCPs (por ejemplo, `Verifier` para leer logs de despliegue).
- **Output:** Configuración de MCPs en el sistema y permisos actualizados.

### Slice 6: Documentación y Skill

- **Responsable:** `documentation-writer`
- **Tareas:**
  - Actualizar `SKILL.md` para incluir:
    - El nuevo flujo de QA.
    - El bucle de verificación.
    - La integración con MCPs.
  - Asegurar que `plan.md` y `build.md` referencien las nuevas capacidades.
- **Output:** Archivos de documentación actualizados.

## 8. Verification Commands / Evidence Expected

| Slice | Comando o Evidencia |
| --- | --- |
| Slice 1 | `cat explore-mini.md \| grep "model:"` → debe mostrar `gpt-5.4-mini`. |
| Slice 2 | Ejecutar `code-reviewer` en un diff de ejemplo; la salida debe ser JSON válido con array `findings`. |
| Slice 3 | Simular un `verifier` que devuelve `rework-required`; observar que `Delegator` ejecuta `reconciler` y repite `verifier`. |
| Slice 4 | Llamar a `qa-builder` con un spec de ejemplo; debe generar un archivo de test y ejecutarlo con Playwright. |
| Slice 5 | Verificar que los MCPs están listados en la configuración del sistema y que los agentes pueden invocarlos. |
| Slice 6 | Revisar `SKILL.md`; debe mencionar explícitamente el bucle de verificación y la integración con MCPs. |

## 9. Open Questions

| Pregunta | Responsable |
| --- | --- |
| ¿El agente `qa-builder` debe generar tests unitarios además de E2E? | Decidir en base a la cobertura deseada (se sugiere inicialmente solo E2E). |
| ¿Qué `Deployment MCP` elegir? ¿`Vercel`, `Render`, `Cloudflare`, o uno específico de la plataforma? | Depende del stack actual; consensuar con el equipo de operaciones. |
| ¿Se debe permitir que `reconciler` cree nuevos archivos (tests) o solo modifique existentes? | Se sugiere permitir creación de nuevos archivos de test si el spec lo indica. |
| ¿El bucle de verificación debe incluir también a `architecture-reviewer` o `security-reviewer`? | No, solo código y tests; arquitectura y seguridad se revisan antes de la implementación. |
