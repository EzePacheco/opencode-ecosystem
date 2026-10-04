---
name: architecture-health
description: Auditar en modo read-only la salud estructural de un repositorio o producto multi-repo y proponer refactors mínimos basados en evidencia. Usar para auditorías de ownership, cohesión, boundaries, dependencias, estado, contratos y evolución; no para readiness del harness ni para implementar cambios.
---

# Architecture health

Respondé: ¿dónde se degrada materialmente la estructura, qué evidencia lo demuestra y cuál es la mínima dirección de refactor justificable?

## Boundary y seguridad

Auditoría estrictamente **READ-ONLY**. No edites repositorios, implementes findings, crees ADRs/docs, instales dependencias, ejecutes migraciones, deploy, commit o push. No ejecutes checks por llamarse `test`, `lint` o `check`; sólo checks locales, bounded y sin efectos persistentes para verificar un fact concreto. `repo-readiness` evalúa legibilidad/verificabilidad del repositorio y harness; `repo-remediation` conserva su workflow mutating para findings autorizados de readiness/harness. No dupliques ninguno.

## Preflight

Antes de inventariar, leer archivos o ejecutar una verificación, confirmá el checkout Git seleccionado, las instrucciones aplicables, las rutas autorizadas y excluidas, y los efectos del comando previsto. Inspeccioná el scanner/check que vas a ejecutar y verificá en el entorno local la disponibilidad de `python3`, Git y las dependencias que ese comando realmente usa; para checks del proyecto resolvé su runner y dependencias desde sus manifests/configuración del checkout. No instales nada. Si una lectura o un check no cabe en el alcance, o falta la dependencia canónica, no lo sustituyas por un shim o una herramienta global: informá el bloqueo y pedí sólo lo que falta. Reutilizá hechos actuales de discovery de `repo-readiness` cuando correspondan; si root, HEAD, estado local o alcance cambiaron, refrescá sólo lo afectado.

## Workflow

`DISCOVER → MECHANICAL INVENTORY → RESOLVE ARCHITECTURE → SELECT HOTSPOTS → DEEP INSPECT → FINDINGS → DO NOT REFACTOR → REFACTOR CANDIDATES → NEXT ACTION → STOP`

1. **Discover.** Dentro de Git, resolvé el root. En un workspace padre no-Git, resolvé el directorio de la instalación activa de `repo-readiness` usando la ruta publicada en el catálogo de skills disponible y ejecutá una vez `<directorio-resuelto>/scripts/workspace_inventory.py --json <workspace>`. No presupongas una raíz fija como `~/.codex/skills`. Si no podés resolver la ubicación activa sin ambigüedad, reportá el límite y no copies el scanner. Reutilizá su `git_common_dir` para distinguir repos hermanos de worktrees/snapshots del mismo repositorio lógico; no hagas deep audit redundante por defecto. El padre coordina, pero no es Technical Authority. Aplicá AGENTS y autoridades de cada repo seleccionado. Si una exclusión no puede aplicarse antes de discovery, usá paths explícitos de repositorios o reportá el límite; no copies `workspace_inventory`.
2. **Mechanical inventory.** Después del preflight, ejecutá `python3 scripts/architecture_inventory.py --json <git-root>` una vez por checkout seleccionado. `--path <ruta-relativa>` limita la inspección a un archivo o subárbol; se puede repetir. `--metadata-only` evita abrir cuerpos de archivos y devuelve rutas/tamaños/lenguajes, layout, pistas por nombre y metadata local de Git. No aporta LOC, ranking por tamaño basado en LOC ni señales derivadas del contenido. El modo normal sí lee cuerpos de fuentes rastreadas y no rastreadas elegibles; Git ignore excluye no rastreados ignorados, pero no protege rastreados. Sus JSON aportan hechos baratos y límites, nunca diagnósticos. En multi-repo, hacé triage compacto antes de elegir profundidad; no inspecciones todos en profundidad sin evidencia.
3. **Resolve architecture.** Leé de forma focal AGENTS, README, arquitectura, ADRs aceptados, contracts, estructura y código/tests actuales. Separá arquitectura declarada de observable. Identificá ownership, dirección de dependencias e invariants. Clasificá discrepancias relevantes como `ALIGNED`, `DRIFT`, `DOCUMENTATION_STALE` o `VERIFY`; no alinees código a documentación stale.
4. **Select and inspect.** Elegí hotspots combinando señales mecánicas con arquitectura y riesgo. Tamaño o churn por sí solos no son findings. Inspeccioná código, consumidores, tests y contratos sólo de áreas seleccionadas; buscá activamente evidencia que refute la hipótesis de refactor. Si existe tooling local de arquitectura/dependencias/ciclos, usá sus resultados focalmente antes de inventar análisis equivalente. Leé [la rúbrica](references/audit-rubric.md) para la inspección profunda.
5. **Conclude and stop.** Emití sólo findings respaldados por evidencia, `DO NOT REFACTOR`, candidatos mínimos ordenados por impacto/riesgo y el menor siguiente paso útil. No diseñes ni apliques todavía el refactor.

## Output

Incluí siempre `REPO PROFILE`, `ARCHITECTURE BASELINE`, `MECHANICAL SIGNALS`, `HOTSPOTS INSPECTED`, `FINDINGS`, `LARGE FILE ASSESSMENT`, `DO NOT REFACTOR`, `TOP EVIDENCE`, `REFACTOR CANDIDATES`, `NEXT ACTION`. Incluí `ARCHITECTURE DRIFT`, `DATA / PERFORMANCE`, `ENFORCEMENT OPPORTUNITIES` sólo si aplican. Las secciones obligatorias pueden decir `ninguno demostrado` con motivo; no fabriques findings ni casos KEEP.

Findings: sólo `KEEP`, `SIMPLIFY`, `REFACTOR`, `ENFORCE`, `REMOVE`, `DEFER`, `VERIFY`; sin score agregado ni prioridad basada sólo en LOC. Formato:

```text
[PRIORITY] ACTION — Area
Evidence:
Observed responsibility/boundary:
Risk/cost:
Why current structure is insufficient:
Proposed direction:
Mechanically enforceable: yes|no|partial
Confidence: high|medium|low
```

`KEEP` puede indicar que la estructura observada es adecuada; explicá cuando `Why current structure is insufficient` no aplica. Acotá cada `KEEP` al comportamiento y área inspeccionados; una conclusión sobre el archivo no cubre automáticamente sus sub-boundaries. Para cada candidato, indicá scope, problema concreto, dirección de separación, invariants/comportamiento a preservar, contratos afectados y verificación necesaria. `NEXT ACTION` puede ser test de caracterización, medición o confirmación de un invariant; nunca aplicación automática.
