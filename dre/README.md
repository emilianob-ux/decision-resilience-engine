# Decision Resilience Engine — código (`dre/`)

Implementación **MVP**. La especificación vive en [`docs/pdr/`](../docs/pdr/README.md)
y [`docs/DRE_TECHNICAL_ARCHITECTURE.md`](../docs/DRE_TECHNICAL_ARCHITECTURE.md)
(**documento de diseño, no de estado**). Qué está implementado de verdad, componente
por componente: [`docs/DRE_IMPLEMENTATION_STATUS.md`](../docs/DRE_IMPLEMENTATION_STATUS.md).

## Estructura

| Ruta | Rol | Alcance real |
|------|-----|--------------|
| `contracts/` | Modelos Pydantic del ICD | `ExecutionContext` (16 estados), `StressFeedbackPayload` con invariante `recommended_action ∈ action_priority`. Espejados **verbatim** en el ICD y verificado por test. |
| `orchestrator/` | FSM (`fsm.py`) + pipeline (`engine.py`) | 21 transiciones en tabla; transición no declarada ⇒ `FSMError`. Dos recorridos secuenciales fijos, sin ruteo por modo. |
| `governance/` | Ledger SQLite | 3 tablas, solo `INSERT`; idempotencia y colisión por `(run_id, data_hash)`. Append-only **por convención del código**, no por triggers de la base. |
| `storage/` | `ContextStore` (ABC) + memoria + Redis | El backend Redis se prueba contra `fakeredis`, no contra un Redis real. |
| `skills/` | Funciones numéricas puras | Deliberadamente *lite*: KS-vs-normal, stress LP (HiGHS), PSI+Frobenius, overlap 1-D, clasificador de ΔKPI. `backprop`, `drift` y `override` **no los invoca ningún recorrido del pipeline**. |
| `api/` | FastAPI | `GET /dre/health`, `POST /dre/simulate`, `POST /dre/resume`. Sin auth: servidor de desarrollo. |
| `measurement/` | Puente DRE → runner MAT | `subprocess` + parseo de JSON (patrón *measurement command*). Hoy solo lo ejercita un test. |
| `core/` | Utilidades | `sha256_text`. |

## Correr

```bash
pip install -r requirements.txt -r requirements-dev.txt

bash ../scripts/demo_dre.sh                                   # demo completa, ~2.2 s
python ../scripts/run_dre_api.py --db ../data/dre_governance.sqlite   # solo la API
```

## Tests

```bash
pytest tests/test_dre_*.py tests/test_docs_contract.py -q
```

`tests/test_dre_invariants.py` es el que importa: verifica idempotencia sin fila
duplicada, bitácora **encadenada**, `resume` idéntico campo por campo y la FSM
validada como grafo.

## Como paquete

La wheel incluye `dre/`. La API HTTP es un extra opcional para no obligar a instalar
FastAPI a quien solo quiere el motor:

```python
from dre import DrePipeline  # base
from dre.api.app import create_app  # requiere el extra [api]
```
