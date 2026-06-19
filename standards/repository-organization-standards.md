# Repository Organization Standards

## Principio

La estructura del repo debe reflejar ownership, boundaries, despliegue, testing y los cambios mas frecuentes.

## Opciones Comunes

### Por Feature

- Buena para producto con flujos o dominios claros.
- Facilita ownership y cambios end-to-end.
- Riesgo: utilidades duplicadas si faltan convenciones.

### Por Layer

- Buena para apps chicas o stacks muy convencionales.
- Riesgo: obliga a saltar entre carpetas para seguir una sola feature.

### Hibrida

- Compartidos por layer solo cuando el reuse es real; features para lo demas.
- Suele ser el mejor default en repos medianos.

## Reglas

- Mantener codigo que cambia junto cuando pertenece a la misma capacidad.
- Separar app/domain/infra/ui cuando eso aclare boundaries reales.
- Tests cerca de la unidad cuando mejora legibilidad; centralizados solo si la herramienta lo pide.
- `scripts/`, `ops/` o `infra/` para automatizacion y despliegue; no mezclar con codigo de producto.
- `docs/` o `adr/` para decisiones y guias operativas relevantes.
- Evitar carpetas `utils` o `common` como cajon de sastre.

## Monorepo

Usar monorepo cuando:

- hay shared types/contracts reales;
- se coordinan cambios entre paquetes frecuentemente;
- tooling y CI soportan el costo.

Evitarlo cuando:

- equipos y ciclos son casi independientes;
- la plataforma no soporta bien cache, ownership o pipelines.

## Estructuras De Referencia

### Backend Modular

```text
src/
  modules/
    billing/
      application/
      domain/
      infrastructure/
      transport/
    identity/
  shared/
tests/
scripts/
docs/
```

### Frontend Por Feature

```text
src/
  features/
    checkout/
      components/
      hooks/
      api/
      state/
      tests/
  shared/
  app/
```

### Infra / DevOps

```text
infra/
  terraform/
  helm/
ops/
  runbooks/
  scripts/
.github/
docs/
```

## Smells

- Todo depende de `shared`.
- El dominio vive en `helpers`.
- Una feature necesita tocar 8 carpetas sin necesidad.
- Los boundaries del deploy no coinciden con los del codigo.

## Regla De Cierre

Si una estructura no reduce friccion para cambiar, testear, desplegar o encontrar ownership, no esta organizando: esta decorando.
