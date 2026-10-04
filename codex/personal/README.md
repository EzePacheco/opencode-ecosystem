# Harness personal activo — 2026-10-04

Fuente portable del método global y cinco skills personales instaladas en Fedora y Ubuntu. La guía deriva del cierre Ubuntu de hoy; los cuatro bundles genéricos se recuperaron íntegros desde la instalación Fedora revisada. ejecutar-handoff deriva de la instalación Ubuntu. La revisión de procedencia no atribuye un autor Git histórico inexistente a estos bundles.

Esta superficie es independiente de la adaptación histórica codex/ del repositorio. Los instaladores install-codex.sh y el doctor histórico no instalan ni validan este baseline: conservan su alcance previo. No ejecutar esos instaladores para sincronizar este método.

## Aplicación manual

Identificar configuración e instrucciones activas. Respaldar localmente cada destino antes de editar, con permisos privados. Fusionar AGENTS.md preservando diferencias justificadas; copiar los cinco directorios completos de skills a ~/.agents/skills sólo después de resolver colisiones. Fusionar exclusivamente las preferencias de baseline.toml con configuración local, conservando permisos, hooks, MCP, plugins, trust, rutas y secretos propios de cada host. La ausencia de cap personal requiere retirar el antiguo max_concurrent_threads_per_session=3; no promete concurrencia ilimitada.

La memoria nativa permanece desactivada. persistent-memory, MemoriesAI, su vault y hooks quedan fuera del paquete. Ninguna instalación de este paquete autoriza activarlos. Playwright y Auth0 tienen instalaciones separadas por host; no se incluyen dependencias, binarios, credenciales ni config completa aquí.

## Verificación

python3 skills/ejecutar-handoff/scripts/verify_pack.py . manifest.json
python3 -m unittest discover -s skills/repo-readiness/tests -v
python3 -m unittest discover -s skills/architecture-health/tests -v

Las suites usan fixtures temporales locales: 27 tests de readiness y 12 de arquitectura pasaron en Ubuntu al recuperar los bundles. La integridad por hashes no demuestra inyección automática en sesiones ni comportamiento del modelo. Comprobar discovery en una sesión nueva por separado.

## Rollback

Revertir únicamente texto, preferencias y directorios introducidos, tras comprobar que no hay modificaciones posteriores. Restaurar backups privados sólo para archivos aún iguales a la entrega. No restaurar config completa sobre cambios ajenos, ni borrar sesiones, datos, vault o autenticación.
