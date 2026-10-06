# Harness personal activo — baseline 2026-10-04

Fuente portable del método global y cinco skills personales instaladas en Fedora y Ubuntu. La guía deriva del cierre Ubuntu del 2026-10-04; los cuatro bundles genéricos se recuperaron íntegros desde la instalación Fedora revisada. ejecutar-handoff deriva de la instalación Ubuntu. La revisión de procedencia no atribuye un autor Git histórico inexistente a estos bundles.

Esta superficie es independiente de la adaptación histórica codex/ del repositorio. Los instaladores install-codex.sh y el doctor histórico no instalan ni validan este baseline: conservan su alcance previo. No ejecutar esos instaladores para sincronizar este método.

## Aplicación manual

Identificar configuración e instrucciones activas. Respaldar localmente cada destino antes de editar, con permisos privados. Fusionar AGENTS.md preservando diferencias justificadas; copiar los cinco directorios completos de skills a ~/.agents/skills sólo después de resolver colisiones. Fusionar exclusivamente las preferencias de baseline.toml con configuración local, conservando permisos, hooks, MCP, plugins, trust, rutas y secretos propios de cada host. El fragmento portable no fija un cap personal: el cliente elige su default. Esto no implica concurrencia ilimitada ni autoriza retirar límites locales deliberados por recursos. Retirar el antiguo max_concurrent_threads_per_session=3 requiere confirmar que era el límite histórico arbitrario y tener autorización específica; no lo copies a otro host por paridad.

La memoria nativa permanece desactivada. persistent-memory, MemoriesAI, su vault y hooks quedan fuera del paquete. Ninguna instalación de este paquete autoriza activarlos. Playwright y Auth0 tienen instalaciones separadas por host; no se incluyen dependencias, binarios, credenciales ni config completa aquí.

## Paridad y excepciones por host

La paridad sincroniza método, skills y preferencias de `baseline.toml`; no sustituye la configuración completa de un host. Verifica estas excepciones mediante readback antes de aplicar o usar una integración:

| Frontera | Ubuntu | Fedora |
|---|---|---|
| Defaults personales | Sol medium, Plan high, Luna high | Mismos defaults de `baseline.toml` |
| Memoria nativa | Desactivada | Desactivada |
| MemoriesAI externo, fuera del paquete | Puente SSH manual con proyecto explícito | Owner local; conservar sólo hooks autorizados |
| MCP declarados | Auth0 read-only; Notion/Figma/Buffer disabled | Auth0 read-only; Notion/Figma enabled; Buffer ausente |
| Rutas y launchers | Rutas propias; wrappers con Node absoluto | Rutas propias; no copiar rutas Ubuntu |
| Rules, hooks, permisos y trust | Decisiones locales del host | Decisiones locales; no copiar allows entre hosts |

Los estados MCP declarados no prueban autenticación o ejecución. Atribuye cada check al CLI, binario de app, shell y runtime usados; sus versiones pueden diferir. Conserva credenciales y backups en cada host, y valida resultados estáticos, discovery y runtime por separado. Ninguna excepción autoriza activar memoria/captura, ampliar trust o eludir controles para obtener PASS.

## Entorno técnico y cierre

Resuelve el intérprete, dependencias dev y lockfile del repositorio que vas a verificar. Usa entornos existentes; crea un entorno o instala dependencias sólo dentro del alcance autorizado y respeta las prohibiciones explícitas del pedido. Si Ubuntu carece del runner dev, reporta ese check local como bloqueado: pruebas de biblioteca estándar no sustituyen Ruff/mypy/coverage y un PASS ejecutado en Fedora no es un PASS local Ubuntu. No reduzcas gates por una herramienta ausente.

Inspecciona los efectos del runner y aísla fixtures, raíces de datos y cachés cuando corresponda. Planifica verificaciones según recursos disponibles y evita suites pesadas concurrentes. Cierra con readback del archivo instalado, fuente/revisión y alcance real de cada prueba.

## Verificación

python3 skills/ejecutar-handoff/scripts/verify_pack.py . manifest.json
python3 -m unittest discover -s skills/repo-readiness/tests -v
python3 -m unittest discover -s skills/architecture-health/tests -v

Las suites usan fixtures temporales locales: históricamente, 27 tests de readiness y 12 de arquitectura pasaron en Ubuntu al recuperar los bundles; esa evidencia no es una ejecución actual. verify_pack comprueba inventario y bytes del paquete portable; no exige crear un manifiesto por cada tarea. La integridad por hashes no demuestra inyección automática en sesiones ni comportamiento del modelo. Comprobar discovery en una sesión nueva por separado.

## Rollback

Revertir únicamente texto, preferencias y directorios introducidos, tras comprobar que no hay modificaciones posteriores. Restaurar backups privados sólo para archivos aún iguales a la entrega. No restaurar config completa sobre cambios ajenos, ni borrar sesiones, datos, vault o autenticación.
