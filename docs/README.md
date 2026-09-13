# Índice de documentación

Navegación en 30 segundos. Cada fila dice **cuándo** leer el documento, no solo qué contiene.

## Empezar

| Leé esto si… | Documento |
|---|---|
| Querés ver el motor funcionando ya, sin leer nada | [`../README.md#demo-de-60-segundos`](../README.md) → `bash scripts/demo_dre.sh` |
| Querés correr el laboratorio MAT paso a paso en tu máquina | [tutorial_quickstart.md](tutorial_quickstart.md) |
| Te interesa qué está implementado de verdad vs. qué es diseño | [DRE_IMPLEMENTATION_STATUS.md](DRE_IMPLEMENTATION_STATUS.md) |

## DRE — el motor

| Leé esto si… | Documento |
|---|---|
| Vas a tocar el código y necesitás los contratos exactos | [pdr/02_Interface_Contracts_ICD.md](pdr/02_Interface_Contracts_ICD.md) — espejo verificado de `dre/contracts/` |
| Querés el diseño completo: matemática, FSM, complejidad, stack objetivo | [DRE_TECHNICAL_ARCHITECTURE.md](DRE_TECHNICAL_ARCHITECTURE.md) — **documento de diseño, no de estado** |
| Querés el mapa componente → archivo → test | [DRE_IMPLEMENTATION_STATUS.md](DRE_IMPLEMENTATION_STATUS.md) |
| Querés ver cómo estructuro requisitos, riesgos y V&V | [pdr/README.md](pdr/README.md) — ejercicio de ingeniería de sistemas |
| Buscás el código | [`../dre/README.md`](../dre/README.md) |

## MAT — el laboratorio de medición

| Leé esto si… | Documento |
|---|---|
| Necesitás el esquema SQLite que espera el runner | [DATASET.md](DATASET.md) |
| Querés escribir filtros de señal en JSON | [signal_rules_examples.md](signal_rules_examples.md) |
| Querés reproducir una corrida desde cero | [tutorial_quickstart.md](tutorial_quickstart.md) |

## Decisiones de diseño (histórico)

Specs escritas *antes* de implementar, útiles para ver cómo acoto alcance y qué
descarto a propósito:

| Documento | Qué muestra |
|---|---|
| [specs/2026-04-27-surfer-compound-win-requirements.md](specs/2026-04-27-surfer-compound-win-requirements.md) | Requisitos con IDs (R1–R8), tabúes anti *curve-fitting*, y el gate walk-forward que después se implementó como `--holdout-frac`. |
| [specs/2026-04-27-leverage-pid-controller.md](specs/2026-04-27-leverage-pid-controller.md) | Control PI + feedforward con anti-windup: invariantes no negociables, alcance v1 vs v1.1 explícito. Implementado en `leverage_pi.py`. |

## Mantenimiento

| Leé esto si… | Documento |
|---|---|
| Vas a publicar una release en PyPI | [PUBLISHING_PYPI.md](PUBLISHING_PYPI.md) |
| Buscás la auditoría honesta del repo y el backlog priorizado | [`../AUDIT.md`](../AUDIT.md) |
| Buscás notas de difusión del autor (no documentación técnica) | [internal/](internal/README.md) |
