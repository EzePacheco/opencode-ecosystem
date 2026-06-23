# SPEC V3: Ecosistema de Agentes - Orquestación, QA, Verificación y Roles Avanzados

## Metadata

- **Spec ID:** `SPEC-2026-06-22-AGENT-ECOSYSTEM-V3`
- **Versión:** `3.0`
- **Estado:** `Aprobado para implementación faseada`
- **Fecha:** `2026-06-22`
- **Autor:** Orc Plan
- **Reemplaza / consolida:**
  - `SPEC-2026-06-22-AGENT-ECOSYSTEM`
  - `SPEC-2026-06-22-AGENT-ECOSYSTEM-V2`

---

## 1. Objetivo

Unificar, corregir y extender el ecosistema nativo de agentes OpenCode para soportar:

- modelo de agentes consistente y verificable;
- handoffs estructurados entre reviewers, reconciler y verifier;
- bucle controlado `verifier → reconciler → verifier`;
- agente QA para pruebas E2E;
- clasificación de tamaño `S/M/L/XL`;
- modo Mini-SDD seguro;
- reference files en handoffs;
- rol opcional `tech-lead`;
- rol opcional `worktree-manager`;
- human-in-the-loop gate;
- integración MCP controlada y least-privilege;
- documentación, installers y doctors alineados.

La implementación debe preservar el principio central del repo:

> Orc Plan planifica y especifica. Del Build implementa, coordina builders, revisa, reconcilia y verifica. Builders no rediseñan fuera de la spec.

---

## 2. Contexto

El repo contiene el setup nativo OpenCode en la raíz y la adaptación Codex bajo `codex/`.

Esta spec aplica **solo al setup nativo OpenCode de la raíz**, salvo que se indique explícitamente lo contrario.

Estado actual relevante:

- `agents/build.md` coordina builders, reviewers, reconciler y verifier, pero no tiene bucle de rework.
- `agents/plan.md` ya es spec-writable solo para `*.spec.md`.
- `agents/explore-mini.md` usa `openai/gpt-5.4-mini`, pero su descripción y los doctors pueden estar desalineados.
- `doctor-opencode.sh` y `doctor-opencode.ps1` hardcodean la matriz de agentes.
- Los doctors esperan `agents/explore.md`; si falta, la verificación falla.
- No existen todavía:
  - `agents/qa-builder.md`
  - `agents/tech-lead.md`
  - `agents/worktree-manager.md`

---

## 3. Decisiones Arquitectónicas

### D1 — Implementación faseada, pero objetivo completo

Se implementan todas las capacidades de Spec 1 y Spec 2, pero en fases obligatorias para evitar romper el runtime:

1. Baseline y doctors.
2. Handoffs estructurados.
3. Rework loop.
4. QA builder.
5. Size classification, Mini-SDD y reference files.
6. Tech Lead.
7. Human Gate.
8. Worktree Manager.
9. MCP integration.
10. Docs y validación final.

### D2 — Plan no orquesta builders

`plan.md` puede declarar:

- `size`
- `mini`
- `reference_files`
- `needs_qa`
- `human_gate`
- `tech_lead_recommended`
- `worktree_recommended`

Pero **no invoca builders directamente**.

La invocación corresponde a `build.md`.

### D3 — Mini-SDD no omite reviewers críticos por riesgo

Mini-SDD puede saltar reviewers especializados solo si el cambio es realmente de bajo riesgo.

Aunque `size = S`, debe incluir `architecture-reviewer` o `security-reviewer` si toca:

- permisos;
- agentes;
- MCPs;
- auth;
- secretos;
- privacidad;
- supply chain;
- contratos públicos;
- installers/doctors;
- workflow runtime.

### D4 — MCPs se agregan con least privilege

MCPs externos se configuran de forma segura:

- no secretos hardcodeados;
- servidores deshabilitados o documentados si faltan credenciales;
- permisos explícitos por agente;
- `agent-memory_*` sigue en `deny` salvo decisión futura separada.

### D5 — Worktree Manager no hace commit/merge automático sin aprobación

`worktree-manager` puede preparar worktrees y limpiar recursos.

No puede hacer:

- commit;
- merge;
- push;
- reset;
- rebase;
- force push;

sin aprobación humana explícita.

### D6 — Human Gate tiene una única posición canónica

Si `human_gate: true`, el flujo pausa después de `code-reviewer` y antes de aplicar findings con `reconciler`.

Flujo:

```text
builder(s)
→ code-reviewer
→ HUMAN GATE
→ reconciler
→ verifier
→ optional rework loop
4. Alcance
YES — Dentro de alcance
Área	Incluido
Baseline	Corregir matriz de agentes, explore, explore-mini, doctors e installers si aplica
Handoffs	Estandarizar salida code-reviewer → reconciler
Rework loop	Implementar loop verifier → reconciler → verifier con máximo 3 iteraciones
QA	Crear qa-builder.md para E2E con Playwright cuando el spec lo requiera
Mini-SDD	Agregar size, mini, reglas de reviewer gating
Reference files	Añadir reference_files a handoffs de builders
Tech Lead	Crear tech-lead.md como subagente read-only de diseño para L/XL
Human Gate	Agregar pausa humana opcional en build.md
Worktree Manager	Crear rol opcional con restricciones fuertes
MCP	Añadir integración MCP segura y documentada
Docs	Actualizar README.md, CHANGELOG.md, skills y standards relevantes
Validation	Actualizar doctor-opencode.sh y doctor-opencode.ps1
NO — Fuera de alcance
Área	Excluido
Codex	No tocar codex/ salvo pedido explícito
Runtime externo	No desplegar servicios externos
Secretos	No agregar tokens, keys ni .env
Memoria persistente	No habilitar agent-memory
Commits automáticos	No hacer commit/merge/push automático
Rediseño total	No reemplazar la arquitectura de agentes
Framework externo	No migrar a otro orquestador
5. Contratos Afectados
agents/plan.md
Debe producir specs/handoffs con campos opcionales:
size: S|M|L|XL
mini: true|false
needs_qa: true|false
human_gate: true|false
reference_files:
  - path/to/file
tech_lead_recommended: true|false
worktree_recommended: true|false
risk_flags:
  - permissions
  - mcp
  - security
  - architecture
  - public_contract
Reglas:
- plan no implementa.
- plan no invoca builders.
- plan sí debe marcar riesgos que impiden Mini-SDD inseguro.
agents/build.md
Debe convertirse en el coordinador principal del flujo.
Debe soportar:
size: S|M|L|XL
mini: true|false
needs_qa: true|false
human_gate: true|false
reference_files: []
max_rework_iterations: 3
Flujo canónico:
1. Validar spec/handoff
2. Clasificar riesgo
3. Decidir Mini-SDD vs full SDD
4. Invocar tech-lead si aplica
5. Preparar reference_files
6. Invocar worktree-manager si aplica
7. Delegar builders
8. Invocar qa-builder si needs_qa=true
9. Consolidar diff
10. Invocar reviewers requeridos
11. Si human_gate=true, pausar y pedir aprobación
12. Enviar findings aceptados a reconciler
13. Invocar verifier
14. Si verifier devuelve rework-required, repetir reconciler/verifier hasta 3 intentos
15. Cerrar con evidencia
agents/code-reviewer.md
Debe emitir findings estructurados.
Formato requerido:
{
  "verdict": "accepted | rework-required",
  "findings": [
    {
      "id": "CR-001",
      "severity": "critical | high | medium | low",
      "file": "path/to/file",
      "line": 123,
      "problem": "Descripción del problema",
      "impact": "Impacto concreto",
      "suggestion": "Cambio recomendado",
      "blocking": true
    }
  ],
  "open_questions": [],
  "verification_gaps": []
}
agents/reconciler.md
Debe aceptar findings estructurados desde:
- code-reviewer
- architecture-reviewer
- security-reviewer
- verifier
Debe reportar:
{
  "applied_findings": ["CR-001"],
  "rejected_findings": [
    {
      "id": "CR-002",
      "reason": "Motivo con evidencia"
    }
  ],
  "files_changed": [],
  "checks_run": [],
  "residual_risk": []
}
agents/verifier.md
Debe emitir:
{
  "verdict": "accepted | partially-verified | rework-required",
  "commands_executed": [],
  "acceptance_coverage": [],
  "failures": [
    {
      "id": "V-001",
      "severity": "high",
      "problem": "Qué falló",
      "suggestion": "Qué debe corregir reconciler"
    }
  ],
  "unverified_areas": []
}
Si devuelve rework-required, build.md debe reenviar los failures a reconciler.
Máximo:
max_rework_iterations: 3
6. Nuevos Agentes
agents/qa-builder.md
Responsabilidad:
- generar o actualizar pruebas E2E cuando needs_qa: true;
- usar Playwright cuando el proyecto lo soporte;
- no rediseñar producto;
- reportar comandos y evidencia.
Configuración sugerida:
mode: subagent
model: openai/gpt-5.5
variant: high
temperature: 0.1
Debe recibir:
spec:
reference_files:
allowed_test_paths:
verification_commands:
Debe reportar:
files_changed:
tests_added:
commands_run:
failures:
residual_risk:
agents/tech-lead.md
Responsabilidad:
- revisar specs L/XL;
- detectar gaps de arquitectura;
- producir design_delta;
- no editar código;
- no modificar specs directamente.
Configuración sugerida:
mode: subagent
model: openai/gpt-5.5
variant: xhigh
temperature: 0.1
Output:
design_delta:
  decisions:
  risks:
  affected_contracts:
  suggested_slices:
  blockers:
agents/worktree-manager.md
Responsabilidad:
- preparar worktrees opcionales para trabajo paralelo;
- reportar paths;
- limpiar worktrees si es seguro;
- no hacer commit/merge/push sin aprobación explícita.
Configuración sugerida:
mode: subagent
model: openai/gpt-5.4-mini
variant: medium
temperature: 0.1
Permitido:
git worktree list
git worktree add
git worktree remove
git status --short
Prohibido sin aprobación humana:
git commit
git merge
git push
git reset
git rebase
git clean
7. Edge Cases y Riesgos
Caso	Riesgo	Mitigación
explore.md falta	Doctor falla	Restaurar o crear agents/explore.md; actualizar doctors
Doctors esperan modelo viejo	Verificación falsa negativa	Actualizar matriz en bash y PowerShell
Mini-SDD salta reviewers críticos	Riesgo de seguridad/arquitectura	Usar risk_flags obligatorios
Rework loop infinito	Costo y loops sin salida	Máximo 3 iteraciones
Findings JSON inválido	Reconciler no puede actuar	Validar schema; si falla, pedir re-emisión
QA sin Playwright instalado	Falla de test	Reportar como partially-verified o instalar si está en scope
MCP con secretos	Filtración	No hardcodear credenciales
Worktree con conflictos	Pérdida de trabajo	Reportar y detener; no auto-resolver
Human Gate sin respuesta	Bloqueo	Timeout configurable o cierre como blocked
8. Acceptance Criteria
ID	Criterio	Verificación
A1	explore-mini usa openai/gpt-5.4-mini y docs/doctors coinciden	Doctor pasa; grep de modelo
A2	agents/explore.md existe o doctors dejan de exigirlo justificadamente	Doctor pasa
A3	code-reviewer produce JSON estructurado	Review de diff de prueba
A4	reconciler consume findings estructurados	Simulación con findings JSON
A5	verifier puede devolver rework-required estructurado	Simulación o fixture
A6	build.md implementa loop máximo 3	Inspección + prueba simulada
A7	Existe qa-builder.md	Archivo presente + doctor actualizado
A8	qa-builder se invoca solo cuando needs_qa=true	Handoff de ejemplo
A9	plan.md documenta size, mini, risk_flags, reference_files	Inspección
A10	Mini-SDD no salta security/architecture cuando hay risk flags	Caso simulado
A11	tech-lead.md existe y es read-only	Inspección permisos
A12	worktree-manager.md existe con restricciones de git	Inspección permisos
A13	Human Gate tiene flujo único y documentado	build.md + docs
A14	MCPs se configuran sin secretos y con permisos mínimos	Inspección config
A15	README.md, CHANGELOG.md, skills y standards reflejan V3	Inspección
A16	./install.sh "$tmp/opencode" && ./doctor-opencode.sh "$tmp/opencode" pasa	Comando real
A17	doctor-opencode.ps1 pasa si pwsh está disponible	Comando real o skipped con razón
9. Implementation Slices
Slice 0 — Baseline y Consistencia Actual
Responsable: Del Build / DevOps Builder
Archivos permitidos:
- agents/explore.md
- agents/explore-mini.md
- doctor-opencode.sh
- doctor-opencode.ps1
- README.md
- CHANGELOG.md
Tareas:
1. Resolver ausencia de agents/explore.md.
2. Alinear explore-mini a openai/gpt-5.4-mini.
3. Actualizar descripción stale de explore-mini.
4. Actualizar matriz en doctors.
5. Verificar que install + doctor no falle por managed files faltantes.
Output:
- baseline verificable antes de agregar nuevos roles.
Slice 1 — Handoffs Estructurados
Responsable: Builder asignado a agentes/prompts
Archivos permitidos:
- agents/code-reviewer.md
- agents/reconciler.md
- agents/architecture-reviewer.md
- agents/security-reviewer.md
Tareas:
1. Definir JSON de findings.
2. Exigir id, severity, file, line, problem, impact, suggestion, blocking.
3. Hacer que reconciler acepte ese formato.
4. Mantener reviewers read-only.
Output:
- reviewers y reconciler con contrato común.
Slice 2 — Rework Loop
Responsable: Builder asignado a orquestación
Archivos permitidos:
- agents/build.md
- agents/verifier.md
- agents/reconciler.md
Tareas:
1. Agregar loop verifier → reconciler → verifier.
2. Limitar a 3 iteraciones.
3. Definir salida rework-required.
4. Si sigue fallando tras 3 intentos, escalar al humano.
Output:
- flujo de rework controlado.
Slice 3 — QA Builder
Responsable: Builder asignado a QA
Archivos permitidos:
- agents/qa-builder.md
- agents/build.md
- agents/verifier.md
- doctor-opencode.sh
- doctor-opencode.ps1
Tareas:
1. Crear qa-builder.md.
2. Invocarlo cuando needs_qa=true.
3. Documentar Playwright como mecanismo preferido.
4. No instalar dependencias salvo que el proyecto ya lo permita o el spec lo pida.
5. Actualizar doctors para incluir el nuevo agente.
Output:
- QA builder disponible y verificable.
Slice 4 — Size, Mini-SDD y Reference Files
Responsable: Builder asignado a Plan/Build
Archivos permitidos:
- agents/plan.md
- agents/build.md
- builders especializados:
- agents/backend-builder.md
- agents/frontend-builder.md
- agents/database-builder.md
- agents/devops-builder.md
Tareas:
1. Agregar size: S|M|L|XL.
2. Agregar mini: true|false.
3. Agregar risk_flags.
4. Agregar reference_files.
5. Builders deben confirmar qué reference files consultaron.
6. Mini-SDD permitido solo si no hay risk flags críticos.
Output:
- handoffs más precisos y modo mini seguro.
Slice 5 — Tech Lead
Responsable: Builder asignado a nuevos agentes
Archivos permitidos:
- agents/tech-lead.md
- agents/plan.md
- agents/build.md
- doctors
Tareas:
1. Crear tech-lead.md.
2. Invocarlo para specs L/XL o cuando tech_lead_recommended=true.
3. Output debe ser design_delta, no nuevo spec.
4. Build usa design_delta para mejorar slices, no para rediseñar scope.
Output:
- revisión de diseño opcional para trabajo grande.
Slice 6 — Human Gate
Responsable: Builder asignado a orquestación
Archivos permitidos:
- agents/build.md
- skills/workflow-sdd/SKILL.md
- docs
Tareas:
1. Agregar human_gate: true|false.
2. Pausar después de code-reviewer.
3. Mostrar resumen, findings y diff esperado.
4. Continuar solo con aprobación humana.
5. Si no hay aprobación, cerrar como blocked.
Output:
- gate humano claro y único.
Slice 7 — Worktree Manager
Responsable: DevOps Builder
Archivos permitidos:
- agents/worktree-manager.md
- agents/build.md
- doctors
- docs
Tareas:
1. Crear worktree-manager.md.
2. Soportar creación/listado/remoción segura de worktrees.
3. Prohibir commit/merge/push/reset/rebase sin aprobación.
4. Build puede invocarlo si worktree_recommended=true o parallelism > 1.
5. Conflictos detienen flujo y escalan al humano.
Output:
- worktree manager seguro.
Slice 8 — MCP Integration
Responsable: DevOps Builder / Security-aware builder
Archivos permitidos:
- opencode.jsonc
- agents/*.md solo donde corresponda
- README.md
- docs
- doctors si validan MCPs
Tareas:
1. Mantener agent-memory_*: deny.
2. Configurar MCPs sin secretos hardcodeados.
3. Priorizar:
- Filesystem MCP;
- Sequential Thinking MCP;
- GitHub MCP si hay credenciales externas;
- Sentry MCP para errores si hay credenciales externas;
- Deployment MCP solo si se define plataforma.
4. Si falta plataforma/credencial, documentar MCP como optional-disabled.
5. No ampliar permisos de agentes existentes salvo justificación explícita.
Output:
- MCPs seguros, documentados y verificables.
Slice 9 — Docs, Skills, Standards y Changelog
Responsable: Documentation Writer
Archivos permitidos:
- README.md
- CHANGELOG.md
- skills/workflow-sdd/SKILL.md
- skills/spec/SKILL.md
- standards/ai-workflow-standards.md
- docs/**/*.md
Tareas:
1. Documentar flujo V3.
2. Documentar Mini-SDD seguro.
3. Documentar QA builder.
4. Documentar rework loop.
5. Documentar human gate.
6. Documentar MCP policy.
7. Documentar worktree restrictions.
Output:
- documentación alineada con runtime.
Slice 10 — Final Doctor / Install Validation
Responsable: Verifier
Comandos esperados:
bash -n ./doctor-opencode.sh
tmp="$(mktemp -d)" && ./install.sh "$tmp/opencode" && ./doctor-opencode.sh "$tmp/opencode"
Si pwsh existe:
pwsh -NoProfile -File "./doctor-opencode.ps1" -Target "$tmp/opencode"
Evidencia esperada:
- install completo;
- doctor bash pasa;
- doctor PowerShell pasa o se reporta como skipped por falta de pwsh;
- no hay managed files faltantes;
- matriz de agentes consistente.
10. Verification Commands / Evidence Expected
Slice	Evidencia
Slice 0	Doctor pasa con matriz actualizada
Slice 1	JSON de reviewer válido
Slice 2	Simulación de rework-required ejecuta reconciler y re-verifier
Slice 3	qa-builder.md existe y Build lo invoca con needs_qa=true
Slice 4	Mini-SDD respeta risk_flags
Slice 5	tech-lead.md produce design_delta
Slice 6	human_gate=true pausa después de review
Slice 7	Worktree manager no permite commit/merge automático
Slice 8	MCPs no contienen secretos y respetan permisos
Slice 9	README/CHANGELOG/skills/standards actualizados
Slice 10	install + doctor pasan
11. Handoff a Del Build
Implementar esta spec V3 en fases, sin rediseñar fuera de scope.
Prioridad obligatoria:
 1. Slice 0
 2. Slice 1
 3. Slice 2
 4. Slice 3
 5. Slice 4
 6. Slice 5
 7. Slice 6
 8. Slice 7
 9. Slice 8
10. Slice 9
11. Slice 10
Reglas para Del Build:
- No tocar codex/.
- No habilitar secretos.
- No hacer commit/merge/push.
- No ampliar permisos sin justificar en el reporte.
- No saltar review final.
- Toda entrega debe pasar por:
- code-reviewer
- reconciler
- verifier
- Agregar architecture-reviewer porque esta spec cambia workflow y contratos.
- Agregar security-reviewer porque toca permisos, MCPs y agentes.
12. Resultado Esperado
Al finalizar, el ecosistema debe quedar con esta arquitectura:
                  Orc Plan
                     │
                     ▼
             Spec / Handoff V3
                     │
                     ▼
                Del Build
                     │
        ┌────────────┼────────────┐
        │            │            │
    Tech Lead?   Worktree?    Reference Files
        │            │            │
        └────────────┼────────────┘
                     ▼
                  Builders
                     │
                     ▼
                QA Builder?
                     │
                     ▼
              Code Reviewer
                     │
                     ▼
               Human Gate?
                     │
                     ▼
                Reconciler
                     │
                     ▼
                 Verifier
                     │
          ┌──────────┴──────────┐
          │                     │
       accepted          rework-required
                                │
                                ▼
                          Reconciler
                                │
                                ▼
                            Verifier
                         max 3 attempts
