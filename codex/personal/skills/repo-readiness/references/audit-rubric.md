# Audit rubric

Usá esta rúbrica para interpretar facts del scanner. No reemplaza la autoridad del repositorio: código, configuración, schemas, migrations, contracts, tests, documentación vigente y ADRs son la evidencia técnica primaria.

## Context load

Revisá qué se carga automáticamente y qué queda bajo demanda:

- AGENTS root, overrides y precedencia;
- instrucciones duplicadas o contradictorias;
- routers y archivos que sólo agregan navegación;
- tamaño y señal aproximada, sin llamar “demasiado grande” a un archivo por su tamaño aislado;
- diferencia entre current, future e historical.

Un override es útil cuando expresa una frontera local real. La existencia de varios AGENTS no es por sí misma un problema.

Separá instrucciones personales/globales de archivos versionados del repo. Para Codex, verificá la cadena aplicable al directorio de trabajo: global, root y directorios intermedios; un override tiene precedencia sobre AGENTS en el mismo directorio. Un archivo encontrado por el scanner no prueba que esté cargado, versionado o disponible para otro colaborador. Los fallbacks configurados sólo en el entorno personal tampoco prueban portabilidad.

## TEAM PORTABILITY

Cuando el usuario declare un repo compartido o haya evidencia de colaboración, evaluá si un colaborador nuevo —humano o asistido por un agente— puede clonar y encontrar las reglas repo-specific necesarias sin el harness personal del owner. Citá la evidencia de colaboración; no la infieras sólo de que exista Git.

Usá primero `collaboration.contributor_guides`, `collaboration.codeowners`, `collaboration.pull_request_templates` y `collaboration.mailmap` como inventario mecánico de paths presentes. El scanner no inspecciona profundamente esos documentos ni enumera todos los equivalentes posibles; si una ausencia o una ubicación no cubierta cambia la interpretación, complementalo con una búsqueda focal, read-only y bounded de paths versionados y enlaces desde README/docs. Inspeccioná instrucciones de otros agentes sólo si ya aparecen en el repo y son relevantes para duplicación/drift; no hagas un catálogo de vendors. Respetá exclusiones sensibles, symlinks, repos anidados y límites del inventario; reportá cobertura incompleta en vez de inferir ausencia.

Preguntá:

- ¿Qué reglas necesarias dependen de configuración personal o conocimiento humano, y qué evidencia demuestra esa dependencia? No supongas reglas no documentadas; usá `VERIFY` si falta confirmación.
- ¿Hay un shared contributor contract y un camino descubrible hacia setup, estructura relevante, workflows y checks canónicos?
- ¿Puede un agente nuevo encontrar las reglas locales sin conocer la configuración del owner?
- ¿Hay duplicación o contradicciones entre AGENTS, CONTRIBUTING, README, docs e instrucciones agent-specific existentes?
- ¿Qué restricciones obligatorias dependen sólo de prosa y requieren enforcement proporcional?

No asumas que otras herramientas cargan AGENTS automáticamente. Para reglas independientes del agente, preferí una autoridad compartida/tool-neutral y enforcement cuando corresponda; AGENTS puede ser el adapter/map de Codex. Evaluá cada repo seleccionado con su evidencia: compartir owner o workspace no demuestra compartir reglas ni hace portable una configuración personal.

### Collaboration evidence

No asumas que un repositorio es compartido solamente porque pertenece a un producto de equipo.

Cuando team portability sea relevante, determiná primero si existe evidencia:

1. Una instrucción o Source actual indica colaboración.
2. En ausencia de ella, usá `git.branch`, `git.head`, `git.working_tree`, `git.shallow` y `collaboration.git_history` como facts del checkout y del historial Git local bounded. Indicá `commits_inspected` y `limit_reached`; no hagas fetch. Si el scanner no pudo inspeccionar historial o el resultado es incompleto, usá `VERIFY`.
3. Normalizá identidades cuando `.mailmap` lo permita y excluí automatizaciones obvias.
4. Si el historial es shallow/incompleto o las identidades son ambiguas, usá `VERIFY`.

Múltiples contribuidores humanos son evidencia de colaboración para la auditoría actual. Un único contribuidor no demuestra que el repositorio nunca sea compartido: significa que no hay evidencia histórica suficiente para justificar team portability por sí sola.

No agregues AGENTS.md o CONTRIBUTING.md solamente porque haya múltiples contribuidores: todavía debe existir un gap concreto que esos archivos resuelvan.

### Ubicación de responsabilidades

| Responsabilidad | Destino y límite |
| --- | --- |
| Preferencias/principios del desarrollador | Configuración personal/global; no cuenta como contrato suficiente del equipo ni debe copiarse por defecto. |
| Navegación automática y guidance local para Codex | AGENTS pequeño y de alta señal: mapa, reglas no obvias, boundaries, gates y routing condicional. |
| Reglas de contribución para humanos y distintas herramientas | CONTRIBUTING o equivalente compartido; referenciar autoridades canónicas. |
| Arquitectura, rationale, ownership, invariantes, operaciones y decisiones durables | Autoridad documental apropiada cuando no sean baratos de descubrir; AGENTS/CONTRIBUTING navegan hacia ella. |
| Workflow repetido, multi-step y adaptativo | Skill sólo si mejora sobre docs o un script determinista; no almacenar arquitectura o convenciones estáticas como skills. |
| Workflow determinista / invariant verificable | Script existente / tests, contracts, lint o CI proporcional; no depender exclusivamente de memoria del LLM ni agregar tooling sin evidencia. |

### Decisión sobre AGENTS local

Recomendá `ADD` sólo para un gap observable: navegación repo-specific no evidente; invariantes/boundaries relevantes; comandos/gates canónicos importantes; triggers de workflows/skills que deban descubrirse; guidance compartido de agentes hoy dependiente de configuración personal; o reglas legítimamente distintas de un subárbol. Ninguna razón obliga por sí sola a crear un archivo.

Explicá problema, ubicación, contenido mínimo, referencias y qué no duplicar. Excluí principios globales genéricos, hechos baratos de descubrir, documentación profunda y contenido completo de CONTRIBUTING/docs. Para reglas mecánicamente verificables, recomendá enforcement y referenciá el gate, sin reproducir su implementación en instrucciones. Reevaluá AGENTS existentes: pueden merecer `KEEP`, `SIMPLIFY` o `REMOVE` según propósito y evidencia.

### SHARED CONTRIBUTOR CONTRACT

Emití una decisión explícita con `KEEP`, `SIMPLIFY`, `ENFORCE`, `ADD`, `REMOVE`, `DEFER` o `VERIFY` sobre CONTRIBUTING **o su equivalente real**, no sobre un nombre obligatorio. Evaluá existencia, vigencia, propósito, utilidad para humanos/agentes y duplicación con otras autoridades. Identificá reglas compartidas faltantes que hoy dependan sólo del owner.

Según la necesidad observada, el contrato puede orientar setup/desarrollo, estructura, convenciones propias, cómo cambiar o agregar módulos/features, workflows, verificaciones y PR/review, enlazando arquitectura, seguridad, DB u otras autoridades. No es una lista de secciones obligatorias. README, manifests y scripts pueden constituir un contributor path suficiente: en ese caso `KEEP` del camino existente y `DO NOT ADD CONTRIBUTING`. Un documento existente sin propósito actual puede merecer simplificación o eliminación.

## Authorities y documentation

Identificá la fuente de verdad para cada afirmación relevante. Buscá discoverability, duplicación y freshness observable. Separá:

- código y configuración actuales;
- schemas, migrations y contracts;
- instrucciones operativas;
- decisiones históricas.

La memoria puede aportar historia o contexto, pero nunca reemplaza código, configuración o contracts contradictorios.

## Architecture

Evaluá sólo boundaries observables:

- ownership;
- dependencias entre módulos o servicios;
- entradas y salidas;
- reglas escritas sin enforcement;
- límites entre root, packages y deployables.

No exijas DDD, Clean Architecture, capas o diagramas cuando no resuelvan un problema demostrable.

## Contracts y truth

Para cada contract o schema preguntá:

- ¿quién lo consume o mantiene?
- ¿qué código, configuración o migration lo implementa?
- ¿existe compatibilidad o validación observable?
- ¿el documento está actualizado respecto del runtime?

La presencia de un archivo contract no prueba que esté protegido.

## Enforcement

Para cada regla importante preguntá:

> ¿Puede verificarse barato?

Si sí, considerar `prose → prose + enforcement`, sin asumir qué herramienta concreta debe usarse. Preferí el check canónico más pequeño y existente. No agregues CI, hooks o tooling por simetría.

## Feedback loops

Mapeá, sin ejecutarlos automáticamente:

- lint;
- unit/integration tests;
- build;
- contract checks;
- checks locales canónicos;
- E2E;
- diagnósticos;
- feedback pesado o dependiente de servicios.

Para cada loop registrá alcance, costo, side effects y si explica failures. Un script llamado `check` no es automáticamente read-only.

## Harness y agent legibility

Preguntá si un agente puede:

- levantar o inspeccionar el sistema;
- validar un cambio;
- entender un failure;
- encontrar logs y diagnósticos;
- repetir el flujo;
- respetar safety guards.

Para skills, aplicá la separación de responsabilidades anterior. Por defecto, hooks no hacen falta: exigí evidencia de un evento lifecycle real.

## Findings

Usá `KEEP`, `SIMPLIFY`, `ENFORCE`, `ADD`, `REMOVE`, `DEFER` y `VERIFY`. Cada finding necesita evidencia, riesgo/costo y acción. Añadí autoridad afectada y si es mecánicamente verificable cuando corresponda.

`VERIFY` representa evidencia insuficiente. No conviertas incertidumbre en una recomendación de tooling.

## DO NOT ADD

Incluí siempre esta sección. Ausencia != necesidad. Una nueva capa requiere un problema actual respaldado por evidencia observable, un owner razonable y un costo proporcional.
