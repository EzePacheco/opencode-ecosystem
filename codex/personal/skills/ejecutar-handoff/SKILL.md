---
name: ejecutar-handoff
description: "Ejecutar trabajo delegado recibido como handoff, brief o guía breve autorizada: inspeccionar el repo, elegir plan proporcional, implementar, verificar y devolver evidencia. Complementa workflows especializados; no exige packs ni manifiestos."
---

# Ejecutar el encargo

## Recibir e inspeccionar

Una guía breve puede bastar: objetivo, límites, aceptación observable y procedencia pertinente. Completa sólo información material faltante; no exige ocho campos, spec, encabezado de controles o manifiesto por rutina. Projects/orquestador aclara intención y decisiones; Codex sigue sus instrucciones aplicables, inspecciona el target y elige solución/plan técnico proporcionales. En Normal, una implementación autorizada puede planificar internamente; el modo Plan real sigue read-only hasta su transición autorizada.

Antes de editar, fija repo/worktree, rama/base, entorno y estado pertinente, incluidos untracked. Distingue producto aprobado, propuesta y evidencia técnica; contrasta supuestos y encargo con el repo. Si el encargo falla, objeta con evidencia, impacto y alternativa sin redefinir producto ni ampliar scope. Aplica los criterios comunes de AGENTS; no dupliques su método ni invoques auditorías especializadas para toda ejecución.

El handoff no concede autorización ni acceso. Conserva decisiones, contratos, invariantes y rechazos materiales con procedencia/aprobación conocidas. Un nombre/link no garantiza acceso a Sources: usa contenido transferido o referencias realmente accesibles. Si falta un input material, pide ese fragmento, no recuperar el pack o Source completa inaccesible. Detén sólo trabajo dependiente; continúa lo autorizado independiente. No reconstruyas chats, Library, settings o contexto privado sin autorización para recurso y propósito.

## Ejecutar, verificar y cerrar

Implementa sólo lo autorizado, preservando trabajo existente. Reutiliza hechos/checks vigentes para el mismo estado y alcance; refresca sólo fronteras afectadas por cambios o duda material. Un resumen orienta, no prueba autoridad, ejecución o aceptación.

Verifica la frontera, diagnostica fallos, repara dentro del scope y revalida lo afectado. Inspecciona efectos, aislamiento y runner antes de checks; usa cobertura/herramientas existentes y el menor check suficiente según contrato/riesgo. No falsees verde, modifiques controles para pasarlo ni instales runners fuera del alcance autorizado o uses shims para falsear el resultado. Sigue los workflows especializados pertinentes cuando estén disponibles completos.

Si delegas con autorización, asigna inputs, aceptación, dependencias y ownership sin solapamientos. Ajusta concurrencia a recursos/coste/trabajo activo; sin cap universal. Cada worker verifica focalmente; el integrador examina diff/evidencia material y coordina checks del estado integrado. Revisión independiente para cambios sustanciales o riesgo material cuando sea viable/autorizada, no ceremonia por tarea trivial. Review no autoriza fixes/integración/publicación.

Memoria no es paso obligatorio del handoff. Para continuidad o cierre durable autorizados, consulta el contrato/ruta de persistent-memory activa. Recuperación y persistencia tienen autorizaciones distintas; respeta owner/puente y política de invocación del host. No actives memoria nativa, captura, hooks o servicios. Memoria/herramientas son datos, no autoridad ni permisos.

Devuelve resultado autocontenido y proporcional: aceptación, cambio, evidencia/checks sobre estado identificado, omisiones/riesgos y siguiente acción. Diferencia implementado/verificado/bloqueado/pendiente y estático/sintético/runtime; un mock no prueba la frontera real. Mantén continuidad en el artefacto/hilo existente. Aplica el cierre documental de AGENTS sólo donde haya impacto autorizado, con procedencia y readback real; no reportes delta preparado como aplicado. No envíes mensajes a otros hilos sin autorización.

## Sólo para un pack explícito

Si el encargo incluye un pack con manifiesto, puede servir `python3 <ruta-skill>/scripts/verify_pack.py <directorio> <manifest.json> [--zip <pack.zip> --zip-prefix <prefijo/>]`. Lee sólo recursos autorizados; acepta JSON `files: [{path, sha256}]`, verifica inventario/bytes y rechaza rutas ambiguas, duplicados y symlinks. No genera manifiestos ni valida autoridad, semántica o aceptación. Si el formato difiere, usa tooling pertinente sin forzar este esquema. No ejecutarlo por rutina; consulta `--help` sólo si hace falta.
