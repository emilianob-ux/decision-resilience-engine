# Estado de implementación — Decision Resilience Engine

Mapa honesto **especificación → código → test**. La especificación vive en
[`docs/pdr/`](pdr/README.md) y [`DRE_TECHNICAL_ARCHITECTURE.md`](DRE_TECHNICAL_ARCHITECTURE.md);
el código, en [`dre/`](../dre/README.md).

Regla de lectura: si una fila no aparece en "Implementado", **no existe en código**,
por más detallado que esté el diseño. Los nombres llevan el sufijo *lite* cuando la
implementación es un proxy barato de lo que describe el documento de arquitectura.

## Implementado (corre y está cubierto por tests)

| Componente | Ubicación | Alcance real | Test |
|---|---|---|---|
| Contratos ICD | `dre/contracts/` | `ExecutionContext` (16 estados), `StressFeedbackPayload` con invariante `recommended_action ∈ action_priority`. | `test_dre_contracts.py`, `test_docs_contract.py` |
| FSM | `dre/orchestrator/fsm.py` | 21 transiciones `(estado, evento) → estado` en una tabla; transición no declarada ⇒ `FSMError`. Sin async, sin concurrencia. | `test_dre_fsm.py`, `test_dre_invariants.py` |
| Orquestación | `dre/orchestrator/engine.py` | Dos recorridos **secuenciales y predefinidos** (`simulate_standard_success`, `simulate_intervention_success`). No hay ruteo dinámico por modo de ejecución ni scheduler. | `test_dre_pipeline.py` |
| Governance SQLite | `dre/governance/sqlite_store.py` | 3 tablas; `write_run` idempotente por `(run_id, data_hash)`; colisión ⇒ `RunIdCollisionError`. Append-only **por convención del código** (solo hace `INSERT`), no por triggers ni permisos de la DB. | `test_dre_governance.py`, `test_dre_invariants.py` |
| Checkpoints / resume | `sqlite_store.save_checkpoint` + `DrePipeline.resume_latest` | Un checkpoint por transición; `resume_latest` reconstruye el contexto exacto del último. Sin TTL ni limpieza. | `test_dre_invariants.py::test_i4_*` |
| Cache de contexto | `dre/storage/memory.py`, `dre/storage/redis_store.py` | Interfaz `ContextStore` + dos backends. El backend Redis está probado contra **fakeredis**, no contra un Redis real. El pipeline usa memoria por defecto. | `test_dre_storage.py` |
| API HTTP | `dre/api/app.py` | `GET /dre/health`, `POST /dre/simulate`, `POST /dre/resume`. Sin auth, sin rate limit, sin paginación: servidor de desarrollo. | `test_dre_api.py` |
| Coherencia de datos | `dre/skills/coherence.py` | Valida prefijo `sha256:` y modo de ejecución. 8 líneas. No verifica el hash contra datos. | `test_dre_skills.py` |
| Forecasting **lite** | `dre/skills/forecasting.py` | Media, desvío, CV y **test KS contra la normal ajustada**. Una sola familia de distribución. Sin KDE, sin selección de familia, sin copulas, sin Bayes. | `test_dre_skills.py` |
| Stress LP | `dre/skills/stress.py` | LP factible con `scipy.linprog` (HiGHS) sobre una lista de Δ en el RHS; devuelve `infeasibility_rate` y `min_slack_global`. Los escenarios se pasan a mano, **no se generan** (sin colas históricas ni Latin Hypercube). | `test_dre_skills.py` |
| Backprop / relajación LP | `dre/skills/backprop.py` | Relajación LP con timeout por hilo. **No reformula nada**: devuelve FEASIBLE/INFEASIBLE/TIMEOUT. El árbol de acciones de §2.1 del doc técnico no está implementado. | `test_dre_skills.py` |
| Drift **lite** | `dre/skills/drift.py` | PSI por histograma de cuantiles + norma Frobenius entre matrices. Sin ventanas deslizantes con estado, sin regla de 3 corridas, sin umbrales aplicados. | `test_dre_skills.py` |
| Causal **Tier-1 lite** | `dre/skills/causal.py` | Solapamiento de histogramas 1-D como proxy de *propensity overlap* + gate en 0.6. **No es inferencia causal**: sin ATE, sin refutación, sin DoWhy. | `test_dre_skills.py` |
| Override sandbox | `dre/skills/override.py` | Clasificador puro de ΔKPI en tres bandas. Sin sandbox de 50 iteraciones, sin `expiry_utc`, sin rollback. | `test_dre_skills.py` |
| Puente de medición | `dre/measurement/mat_runner.py` | `subprocess` → `compound_optimize_runner.py`, parsea el JSON de stdout. Patrón *measurement.command*. | `test_dre_measurement.py` (se saltea sin DB) |

## Diseñado pero no implementado

Todo esto está en [`DRE_TECHNICAL_ARCHITECTURE.md`](DRE_TECHNICAL_ARCHITECTURE.md)
y **no tiene código**:

| Tema | Dónde se promete |
|---|---|
| KDE con FFT, selección de familia, Anderson–Darling, updating bayesiano | §1.1 |
| Copulas gaussianas / t, shrinkage Ledoit–Wolf, ADF/KPSS | §1.1 |
| Generación de escenarios (colas históricas p95/p99, Latin Hypercube) | §1.2 |
| Árbol de reformulación robusta y programación estocástica en dos etapas | §2.1 |
| Causal nivel 2 y 3 (DiD, control sintético, IV, DoWhy/CausalML, CATE) | §3.1 |
| Umbrales de drift aplicados + regla de persistencia de 3 corridas | §4.2 |
| Redis distribuido con TTL 72 h y locking | §5.1, §8 |
| Evidencia de manipulación (`AUDIT_VIOLATION` ante UPDATE/DELETE) | §6.1 |
| Sandbox de override con expiry y rollback automático | §6.2 |
| SLAs de latencia (`<2s` FAST, `<30s` STANDARD) — nunca se midieron | §7 |
| PostgreSQL/DVC, `statsmodels`, `cvxpy`, `asyncio` | §8 |

## Brechas conocidas del MVP

- `ExecutionContext.checkpoint_refs` está declarado y **siempre vacío**: los
  checkpoints se recuperan por `run_id`, no por referencia embebida.
- El *append-only* del ledger es una propiedad del código, no de la base: nada
  impide un `UPDATE` manual sobre el SQLite.
- `execution_mode` existe en el contrato con tres valores, pero el pipeline lo
  **fija en `STANDARD`** (`engine.py:62`, `engine.py:107`) y la API ni siquiera lo
  expone: no hay `ExecutionModeRouter`.
- `iteration_count` nunca se incrementa: la rama `BACKPROP → OPTIMIZING` existe
  en la FSM pero ningún recorrido implementado la usa.
- La API no tiene autenticación; `scripts/run_dre_api.py` es un servidor de
  desarrollo que escucha en `127.0.0.1`.

Backlog priorizado: [`../AUDIT.md`](../AUDIT.md).

## Pruebas

```bash
pytest tests/ -q          # 48 tests
ruff check . && ruff format --check .
bash scripts/demo_dre.sh  # camino feliz + idempotencia + colisión, ~3 s
```
