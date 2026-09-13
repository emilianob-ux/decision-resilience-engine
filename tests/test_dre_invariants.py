"""Invariantes del motor, no humo.

Los tests de `test_dre_pipeline.py` verifican que el camino feliz termina en
`MONITORING`. Estos verifican las propiedades por las que existe el motor y que
un refactor podría romper sin que ningún test de humo se entere:

  I1. Idempotencia   — reejecutar un `run_id` con el mismo `data_hash` no crea
                       una segunda fila de registro.
  I2. Colisión       — el mismo `run_id` con otro `data_hash` es un error tipado.
  I3. Append-only    — cada transición deja exactamente un evento; ninguna
                       transición reescribe o borra un evento anterior.
  I4. Resume fiel    — el contexto recuperado del último checkpoint es igual al
                       que devolvió el pipeline, campo por campo.
  I5. FSM cerrada    — toda transición declarada sale de un estado declarado y
                       llega a un estado que el contrato admite; no existen
                       transiciones huérfanas ni estados inalcanzables.
"""

from __future__ import annotations

import sqlite3
import tempfile
import typing
import unittest
from pathlib import Path

from dre.contracts.orchestrator_context import ExecutionContext, OrchestratorState
from dre.governance.errors import RunIdCollisionError
from dre.governance.sqlite_store import SqliteGovernanceStore
from dre.orchestrator.engine import DrePipeline
from dre.orchestrator.fsm import _TRANSITIONS

RUN_ID = "opt_20260506_000100_v5.0"


class TestGovernanceInvariants(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "gov.sqlite"
        self.gov = SqliteGovernanceStore(self.db)
        self.pipe = DrePipeline(self.gov)

    def tearDown(self) -> None:
        self.gov.close()
        self.tmp.cleanup()

    def _registry_rows(self) -> int:
        con = sqlite3.connect(self.db)
        try:
            return con.execute("SELECT COUNT(*) FROM dre_run_registry").fetchone()[0]
        finally:
            con.close()

    def test_i1_rerun_is_idempotent(self) -> None:
        first = self.pipe.simulate_standard_success(RUN_ID, "sha256:demo", rng_seed=7)
        second = self.pipe.simulate_standard_success(RUN_ID, "sha256:demo", rng_seed=7)

        self.assertEqual(first.skill_statuses["registry_write"], "inserted")
        self.assertEqual(second.skill_statuses["registry_write"], "already_existed")
        self.assertEqual(self._registry_rows(), 1, "un run_id debe ocupar una sola fila")

    def test_i2_same_run_id_other_hash_is_typed_error(self) -> None:
        self.pipe.simulate_standard_success(RUN_ID, "sha256:demo", rng_seed=7)
        with self.assertRaises(RunIdCollisionError) as cm:
            self.pipe.simulate_standard_success(RUN_ID, "sha256:otro", rng_seed=7)

        payload = cm.exception.as_json()
        self.assertEqual(payload["error"], "RUN_ID_COLLISION")
        self.assertEqual(payload["data_hash_expected"], "sha256:demo")
        self.assertEqual(payload["data_hash_received"], "sha256:otro")
        self.assertIn("recovery", payload)

    def test_i3_audit_log_is_append_only(self) -> None:
        self.pipe.simulate_standard_success(RUN_ID, "sha256:demo", rng_seed=7)
        con = sqlite3.connect(self.db)
        try:
            rows = con.execute(
                "SELECT id, state_before, state_after, event_type FROM dre_audit_log "
                "WHERE run_id = ? ORDER BY id",
                (RUN_ID,),
            ).fetchall()
        finally:
            con.close()

        # Una fila por transición, en orden, y encadenadas: el estado final de una
        # transición es el estado inicial de la siguiente.
        self.assertEqual(len(rows), 9, "el camino STANDARD son 9 transiciones")
        self.assertEqual(rows[0][1], "IDLE")
        self.assertEqual(rows[-1][2], "MONITORING")
        for prev, nxt in zip(rows, rows[1:]):
            self.assertLess(prev[0], nxt[0], "los ids deben crecer (append-only)")
            self.assertEqual(prev[2], nxt[1], "la bitácora debe encadenar estados")

        # Una segunda corrida agrega eventos; no reescribe los anteriores.
        before = self.gov.audit_event_count()
        self.pipe.simulate_standard_success(RUN_ID, "sha256:demo", rng_seed=7)
        self.assertEqual(self.gov.audit_event_count(), before + 9)

    def test_i4_resume_reconstructs_the_same_context(self) -> None:
        done = self.pipe.simulate_standard_success(RUN_ID, "sha256:demo", rng_seed=7)
        resumed = self.pipe.resume_latest(RUN_ID)
        self.assertEqual(
            done.model_dump(mode="json"),
            resumed.model_dump(mode="json"),
            "resume debe devolver el contexto exacto, no uno equivalente",
        )

    def test_i4b_resume_without_checkpoint_fails_loudly(self) -> None:
        with self.assertRaises(ValueError):
            self.pipe.resume_latest("opt_20990101_000000_v5.0")


class TestFsmInvariants(unittest.TestCase):
    def test_i5_every_transition_uses_contract_states(self) -> None:
        declared = set(typing.get_args(OrchestratorState))
        used = {s for s, _ in _TRANSITIONS} | set(_TRANSITIONS.values())
        self.assertEqual(
            used - declared,
            set(),
            "la FSM usa estados que ExecutionContext rechazaría",
        )

    def test_i5b_no_unreachable_state_in_the_implemented_subset(self) -> None:
        sources = {s for s, _ in _TRANSITIONS}
        targets = set(_TRANSITIONS.values())
        # IDLE es el único estado que puede no ser destino de nadie (es el inicial).
        orphan_sources = sources - targets - {"IDLE"}
        self.assertEqual(orphan_sources, set(), "estados origen inalcanzables")
        # El único estado absorbente del subset implementado es FAILED:
        # COMPLETED sigue a MONITORING y MONITORING vuelve a ROUTING por drift.
        dead_ends = targets - sources
        self.assertEqual(dead_ends, {"FAILED"})

    def test_i5c_states_are_valid_for_the_contract(self) -> None:
        for state in sorted({s for s, _ in _TRANSITIONS} | set(_TRANSITIONS.values())):
            ctx = ExecutionContext(
                run_id=RUN_ID,
                execution_mode="STANDARD",
                current_state=state,  # type: ignore[arg-type]
                iteration_count=0,
            )
            self.assertEqual(ctx.current_state, state)


if __name__ == "__main__":
    unittest.main()
