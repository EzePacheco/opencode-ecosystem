# Frontend Architecture Standards

## Reglas

- Organizar por feature cuando el repo lo permita.
- Componentes chicos con responsabilidades claras.
- Estado local primero; global solo cuando varias zonas lo necesitan.
- API client centralizado para contratos y errores.
- Formularios con validacion, loading, error y success.
- Accesibilidad basica: labels, focus, keyboard y contrast.
- Responsive verificado en mobile y desktop.

## UI Review

- No hay overlap de texto o controles.
- Estados empty, loading, error y success existen.
- Acciones destructivas tienen confirmacion o undo segun riesgo.
- Inputs tienen mensajes de error utiles.
- El layout no depende de texto corto o datos felices.

## Prohibido

- Duplicar llamadas HTTP ad hoc en componentes.
- Ocultar errores silenciosamente.
- Usar color como unica senal.
- Introducir librerias UI sin justificar fit con el sistema existente.
