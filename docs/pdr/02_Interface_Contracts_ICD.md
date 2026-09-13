# 02 — Interface Contracts (ICD)

Contratos de interfaz entre componentes del Decision Resilience Engine.

**Estos snippets son un espejo del código que corre**, no pseudocódigo: la fuente de
verdad es [`dre/contracts/`](../../dre/contracts/) y está cubierta por
[`tests/test_dre_contracts.py`](../../tests/test_dre_contracts.py). Si divergen,
gana el código y este archivo es el que está mal.

## 2.1 Handoff crítico: Optimizer → StressTest → Backprop

Implementación: [`dre/contracts/stress_feedback.py`](../../dre/contracts/stress_feedback.py)

```python
# dre/contracts/stress_feedback.py
from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field, model_validator

RecommendedAction = Literal[
    "switch_to_stochastic",
    "add_robustness_buffer",
    "relax_soft_with_penalty",
]


class StressFeedbackPayload(BaseModel):
    """Handoff Optimizer → StressTest → Backprop (ICD §2.1)."""

    failed_constraints: List[str]
    stress_scenarios_failed: List[str]
    slack_violation_magnitude: Dict[str, str]
    recommended_action: RecommendedAction
    action_priority: List[str]
    max_reformulation_iterations: int = Field(default=2, ge=0, le=2)
    robustness_backpropagation_triggered: bool = True

    @model_validator(mode="after")
    def recommended_in_priority(self) -> StressFeedbackPayload:
        if self.recommended_action not in self.action_priority:
            raise ValueError("recommended_action must appear in action_priority")
        return self
```

**Invariante verificado:** `recommended_action` debe pertenecer a `action_priority`.
Se valida con `model_validator(mode="after")` —no con `field_validator`— porque el
validador necesita ver ambos campos ya resueltos, sin depender del orden de
declaración.

## 2.2 Contrato de estado del orquestador (cache volátil / GovernanceCore)

Implementación: [`dre/contracts/orchestrator_context.py`](../../dre/contracts/orchestrator_context.py)

```python
# dre/contracts/orchestrator_context.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

ExecutionMode = Literal["FAST", "STANDARD", "DEEP_AUDIT"]

OrchestratorState = Literal[
    "IDLE",
    "ROUTING",
    "VALIDATING",
    "FORECASTING",
    "CAUSAL",
    "OPTIMIZING",
    "STRESS_TESTING",
    "BACKPROP",
    # Escrituras parcial/final de gobernanza (diagrama FSM técnico §5.2)
    "GOVERNING_PARTIAL",
    "GOVERNING_FINAL",
    "GOVERNING",
    "OVERRIDE",
    "MONITORING",
    "COMPLETED",
    "FAILED",
    "ESCALATED",
]


class ExecutionContext(BaseModel):
    """Volatile orchestrator context (ICD §2.2; persistent cache target = Redis)."""

    run_id: str = Field(..., pattern=r"^opt_\d{8}_\d{6}_v5\.0$")
    execution_mode: ExecutionMode
    current_state: OrchestratorState
    iteration_count: int = Field(ge=0, le=2)
    override_active: bool = False
    stress_scenarios_ref: Optional[str] = None
    checkpoint_refs: List[str] = Field(default_factory=list)
    skill_statuses: Dict[str, Any] = Field(default_factory=dict)
    accumulated_warnings: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Notas de implementación (diferencias deliberadas con el borrador v1.0 del ICD)

| Campo / detalle | Borrador v1.0 | Código actual | Motivo |
|---|---|---|---|
| `current_state` | 14 estados | 16 estados: agrega `GOVERNING_PARTIAL` y `GOVERNING_FINAL` | El diagrama FSM §5.2 ya distinguía escritura parcial y final; el enum no. Gana el diagrama. |
| `skill_statuses` | `Dict[str, str]` | `Dict[str, Any]` | Los skills devuelven reportes estructurados (`forecasting`, `stress`), no strings. |
| `last_updated` | `datetime.utcnow` | `datetime.now(timezone.utc)` | `utcnow()` devuelve un naive datetime y está deprecado desde Python 3.12. |
| Validadores | `field_validator` + `json_encoders` | `model_validator` + serialización por defecto de Pydantic v2 | `json_encoders` está deprecado en Pydantic v2. |

### Brecha conocida

`checkpoint_refs` está declarado en el contrato pero **el pipeline lo deja siempre
vacío**: los checkpoints se persisten en la tabla `dre_checkpoints` y se recuperan
por `run_id` (`SqliteGovernanceStore.load_latest_checkpoint`), no por referencia
embebida en el contexto. Está documentado como brecha en lugar de fingir que el
campo se llena. Ver `AUDIT.md` (P2-1).

## 2.3 Manejo de errores tipado

Implementación: [`dre/governance/errors.py`](../../dre/governance/errors.py) →
`RunIdCollisionError.as_json()`, servido como HTTP **409** por
[`dre/api/app.py`](../../dre/api/app.py).

```json
{
  "error": "RUN_ID_COLLISION",
  "detail": "Same run_id with different data_hash detected",
  "run_id": "opt_20260506_000100_v5.0",
  "data_hash_expected": "sha256:demo",
  "data_hash_received": "sha256:OTRO",
  "recovery": "Generate new run_id or verify input pipeline consistency"
}
```

Reproducible con `bash scripts/demo_dre.sh` (paso 5/5) y cubierto por
`tests/test_dre_api.py::TestDREApi::test_collision_409`.
