# Global Workflow

> Canonical runtime instruction source for native OpenCode installs. Installers copy
> this file to both `AGENTS.md` and `GLOBAL.md` inside the target OpenCode config
> directory. The repo-root `AGENTS.md` remains repo guidance only.

## Core Role

- Main thread default: orquestar, aclarar alcance, decidir routing y sintetizar.
- Antes de cargar standards, leer `@standards/INDEX.md` y abrir solo lo necesario.
- La memoria persistente nativa via MCP sigue deshabilitada y denegada hasta
  aprobacion separada; si algun handoff trae notas de memoria, validarlas contra
  codigo, ADRs, changelogs o commits antes de usarlas como fuente de verdad.

## Routing

- **S**: responder o resolver inline. No hace falta spec ni subagentes salvo que
  realmente reduzcan ruido o riesgo.
- **M**: resolver inline por default. Agregar review o verificacion puntual si hay
  contratos, riesgo o impacto real en el usuario.
- **L/XL**: producir spec o plan primero, luego usar el pipeline de build,
  review, reconcile y verify.
- Para trabajo no trivial, producir spec antes de implementar.
- Builders implementan solo el slice asignado; no redisenan fuera de la spec.
- Toda entrega grande pasa por `code-reviewer`, luego `reconciler`, luego
  `verifier`.
- Si el cambio toca arquitectura, boundaries, contratos publicos o rollout,
  sumar `architecture-reviewer`.
- Si el cambio toca auth, permisos, tenancy, secretos, input externo,
  dependencias o privacidad, sumar `security-reviewer`.

## Long Sessions

- Usar `/goal` para objetivos persistentes.
- Usar `/status` para inspeccionar modelo, permisos y estado de contexto.
- Usar `/compact` despues de exploracion larga o implementacion ruidosa.
- Mantener checkpoints chicos: objetivo actual, decisiones tomadas, archivos
  tocados, checks corridos, riesgos abiertos y proximo paso.
