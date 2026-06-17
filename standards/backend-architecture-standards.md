# Backend Architecture Standards

## Boundaries

- Controller o handler: transporte, parsing y respuesta.
- Use case o service: reglas de negocio y transacciones.
- Repository o gateway: persistencia y servicios externos.
- Job o worker: trabajo async idempotente y observable.

## Reglas

- Mantener logica de negocio fuera de controllers.
- Errores estables y mapeados a respuestas consistentes.
- Operaciones criticas idempotentes o protegidas contra duplicacion.
- Side effects externos despues de persistir estado suficiente para recuperacion.
- Timeouts en llamadas externas.
- Logs con correlation id cuando el stack lo permita.

## Evitar

- Services gigantes sin frontera.
- Repositorios con reglas de negocio.
- Jobs sin retry policy ni DLQ o registro de fallo.
- Transacciones que envuelven llamadas de red.
