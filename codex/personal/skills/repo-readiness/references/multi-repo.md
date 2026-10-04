# Multi-repo composition

Este procedimiento compone inventarios independientes por Git repository. Un product workspace puede ser una carpeta padre no-Git que coordina varios repositorios y worktrees; no es Technical Authority. `workspace_inventory.py` descubre Git roots bounded, y luego Codex hace triage de candidatos. No asumas que cualquier carpeta padre convierte sus repos en un único producto.

## Inputs

Preferencia:

1. paths explícitos;
2. lista proporcionada por el usuario;
3. registry opcional, por ejemplo `python3 scripts/memoryctl.py projects --json`, sólo si existe y su salida puede parsearse de forma segura.

Si el cwd no está dentro de Git, usalo como posible product workspace y ejecutá una vez `scripts/workspace_inventory.py`. Respetá su profundidad y límites; sus Git roots son candidatos, no una selección semántica.

Antes de esa discovery, revisá si las exclusiones solicitadas afectan los directorios que recorrería el scanner. Si es así y no podés hacer cumplirlas antes del recorrido, pedí o usá paths explícitos de repositorios. Una vez resuelto cada root, aplicá `repo_inventory.py --respect-gitignore` y/o `--exclude-path` con paths relativos a ese Git root. No generalices una exclusión relativa de un repositorio a otro sin confirmar que corresponda.

La fuente de paths no es autoridad técnica. Cada repositorio se resuelve y audita por separado.

## Fase 1 — triage factual

Para todos los roots deduplicados:

- resolver Git root;
- ejecutar inventory bounded;
- registrar manifests, context files, documentación, contracts, CI, tests, nested roots, warnings y límites;
- no leer documentación profunda;
- no ejecutar scripts del repositorio.

Conservá en el contexto de la ejecución un resumen reutilizable de root, `git_common_dir`, branch, HEAD, estado local y opciones de alcance/exclusión. Compartilo con etapas siguientes en la conversación o en el informe existente; no crees otro registro de coordinación. Repetí discovery sólo si alguno de esos facts cambió o no se puede comprobar.

Deduplicar roots resueltos. Distintos worktrees son checkouts diferentes del mismo repositorio lógico cuando comparten Git common dir; preservalos como evidencia de snapshots. No hagas deep audit redundante por defecto, salvo selección explícita, comparación requerida o una razón concreta. Un worktree no es automáticamente otro componente/product repo.

## Fase 2 — deep audit

Seleccionar sólo repos con:

- riesgo o contracts relevantes;
- authorities ambiguas;
- contexto automático elevado;
- divergencias entre componentes;
- warnings que impidan concluir;
- selección explícita del usuario.

Default: máximo tres deep audits por batch, salvo petición expresa. Resumí los restantes y ofrecé continuar en otro batch. Reutilizá la inventory ya obtenida para el checkout seleccionado.

## Output comparativo

Usá una fila compacta por repo:

```text
repo | type | candidate depth | context | contracts | checks | warnings | deep-audit reason
```

`candidate depth` es una hipótesis de Codex; no es un score del scanner. El informe final debe sintetizar patrones comunes una sola vez y describir sólo las diferencias importantes por repo.

## Cost control

Reutilizá inventories de la misma ejecución, limitá excerpts, no cargues todas las references por repo y no concatenes JSON completos en el reporte humano.

Si el registry falla, current-repo mode y paths explícitos siguen funcionando. No adaptes la skill alrededor de una incompatibilidad no trivial.
