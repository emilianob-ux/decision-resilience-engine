# Decision Resilience Engine (DRE)

**A decision engine that doesn't lie about its own state: every transition lands in
an append-only ledger, re-running is idempotent, and any run resumes from its last
checkpoint.**

[![CI](https://github.com/emilianob-ux/decision-resilience-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/emilianob-ux/decision-resilience-engine/actions/workflows/ci.yml)
[![Python 3.11 | 3.12](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-48%20passing-brightgreen.svg)](tests/)

**▶ Try it first:** [`bash scripts/demo_dre.sh`](#60-second-demo) — the full demo in
one command, ~3 seconds.

**Versión en español (canónica):** [README.md](README.md)

---

## The problem

A decision pipeline that runs for hours and dies halfway leaves three questions
unanswered: *what state was it in?*, *can I re-run it without duplicating work?* and
*can I prove afterwards why it decided what it decided?* The usual answer is scattered
logs and a `try/except` that restarts from zero.

**This repo is my answer to those three questions**, built small and covered by tests
that verify it.

## Who it's for

- **Engineers** building long-running orchestration who need resumability and audit
  trails, not just retries.
- **Quants / researchers** who want a reproducible measurement bench: the MAT lab
  (BTC/ETH futures) plugs into the engine as a *measurement command*.
- **Anyone evaluating my work:** this repo exists to show how I separate contracts,
  state and effects; how I choose what *not* to build; and how I document what's
  missing.

## What exists today (MVP) vs. what's aspirational

| | Today (implemented + tested) | Roadmap / designed only |
|---|---|---|
| **Orchestration** | Table-driven FSM, 21 transitions, 16 states; an undeclared transition raises `FSMError` | Execution-mode router (FAST/DEEP_AUDIT); everything runs as `STANDARD` today |
| **Governance** | SQLite: idempotent registry keyed on `(run_id, data_hash)`, chained append-only audit log, collision ⇒ typed HTTP 409 | DB-level triggers rejecting `UPDATE`/`DELETE`; PostgreSQL |
| **Resilience** | Checkpoint per transition; `resume` returns the **identical** context, field by field | Checkpoint TTL and cleanup policy |
| **Volatile state** | `ContextStore` (ABC) + memory and Redis backends (tested against `fakeredis`) | Real distributed Redis with locking |
| **API** | `GET /dre/health`, `POST /dre/simulate`, `POST /dre/resume` (FastAPI; correct 422/404/409) | Auth, rate limiting, gRPC |
| **Numeric skills** | Deliberately *lite*: KS-vs-normal forecasting, LP stress (HiGHS), PSI+Frobenius drift, Tier-1 causal overlap, override classifier | KDE+FFT, copulas, two-stage stochastic programming, DoWhy/CausalML |
| **Measurement (MAT)** | Compound BTC/ETH backtest with funding, sliding windows and walk-forward (`--holdout-frac`) | Unit tests for the runner (see [AUDIT.md](AUDIT.md) P1-5) |

Full component → file → test map, plus the explicit list of what is **not**
implemented: [`docs/DRE_IMPLEMENTATION_STATUS.md`](docs/DRE_IMPLEMENTATION_STATUS.md).

## 60-second demo

```bash
git clone https://github.com/emilianob-ux/decision-resilience-engine
cd decision-resilience-engine
pip install -r requirements.txt -r requirements-dev.txt
bash scripts/demo_dre.sh
```

One command, ~3 seconds, no second terminal. It starts the API on a clean SQLite
ledger and demonstrates the three properties the engine is built around:

```
==> 3/5  POST /dre/resume  (rebuilds the context from the last checkpoint)
current_state = MONITORING

==> 4/5  Idempotency: same run_id + same data_hash => the run is NOT duplicated
registry_write = already_existed

==> 5/5  Collision: same run_id + DIFFERENT data_hash => typed HTTP 409
     HTTP 409
{
    "error": "RUN_ID_COLLISION",
    "data_hash_expected": "sha256:demo",
    "data_hash_received": "sha256:OTRO",
    "recovery": "Generate new run_id or verify input pipeline consistency"
}

==> Persisted ledger (append-only SQLite)
     runs = 1   audit events = 18   checkpoints = 18
```

*Two identical submissions, one registry row, 18 audit events, 409 on collision.
That's the entire argument of this repo, executable.*

## Why this shows engineering judgment

1. **Invariants are tested, not claimed.** `tests/test_dre_invariants.py` doesn't
   check that the happy path ends well: it checks that the audit log is **chained**
   (each event's `state_after` is the next one's `state_before`), that `resume`
   returns the exact context (full `model_dump`, not just the state), and that the
   FSM has no unreachable states — validated as a graph, without executing it.

2. **Documentation is a contract CI enforces.** The ICD claims to mirror
   `dre/contracts/`; `tests/test_docs_contract.py` asserts the snippets are the file
   **verbatim** and fails when they drift. The same file guards against the two
   Mermaid syntax errors that were breaking the diagrams on GitHub, and against the
   import regression that had the demo broken.

3. **I choose what not to build, and I say so.** The skills are named *lite* because
   they are cheap proxies: `forecasting` is a KS test against a fitted normal, not
   KDE with FFT. It says so in the code (`kind: "univariate_gaussian_proxy"`), in the
   implementation status doc, and in the audit. I'd rather ship a repo that says
   "this is a proxy" than one that says "causal inference" over 25 lines.

> **Disclaimer:** experimental research software. **Not financial advice.** The MAT
> component measures probabilities over historical or synthetic data; past
> performance does not imply future results.

---

## The FSM that actually runs

These are the 21 transitions in `dre/orchestrator/fsm.py` — the implementation, not a
design sketch. Each transition writes exactly one audit event and one checkpoint. The
only absorbing state is `FAILED`: `COMPLETED` moves to `MONITORING`, which can return
to `ROUTING` on drift. The `BACKPROP` and `ESCALATED` branches are declared and tested
in the table, but **no implemented path walks them yet** (see [AUDIT.md](AUDIT.md) P2-4).

The rendered diagram lives in the [Spanish README](README.md#la-fsm-que-realmente-corre)
and in [`docs/DRE_TECHNICAL_ARCHITECTURE.md`](docs/DRE_TECHNICAL_ARCHITECTURE.md) §5.2.

---

## Two quickstarts

This repo has **two separate layers**. You don't need the second one to evaluate the
first.

### 1. DRE — the engine (start here)

```bash
pip install -r requirements.txt -r requirements-dev.txt

bash scripts/demo_dre.sh              # full demo, one command
# or, manually:
python scripts/run_dre_api.py --db data/dre_governance.sqlite
```

| Endpoint | What it does | Typed errors |
|---|---|---|
| `GET /dre/health` | Liveness | — |
| `POST /dre/simulate` | Walks the full FSM, persisting audit log + checkpoints | `422` invalid payload · `409` `RUN_ID_COLLISION` |
| `POST /dre/resume` | Rebuilds the context from the latest checkpoint | `404` no checkpoint for that `run_id` |

`run_id` must match `^opt_\d{8}_\d{6}_v5\.0$` — that's part of the contract, not a
convention: a malformed id returns 422.

### 2. MAT — the measurement lab (optional)

Compound BTC/ETH futures backtest with funding costs, sliding windows and
walk-forward validation. **It's the engine's measurement bench, not the product.**

```bash
python scripts/bootstrap_synthetic_candles_db.py     # synthetic dataset, ~0.3 s
pytest tests/ -q                                     # 48 tests
python compound_optimize_runner.py --db data/synthetic_signal_tune.db --holdout-frac 0.2
```

Output: JSON on stdout with `p_win_terminal`, `p_ruin`, `p_survive_medium` and the
`walk_forward` block (in-sample vs holdout plus deltas).

The bridge between layers is `dre/measurement/mat_runner.py`: it invokes the runner as
a subprocess and parses its JSON (*measurement command* pattern). Today only a test
exercises it; the DRE pipeline doesn't call it yet.

---

## Documentation

| Read this if… | Document |
|---|---|
| You want to know what's really implemented and what isn't | [`docs/DRE_IMPLEMENTATION_STATUS.md`](docs/DRE_IMPLEMENTATION_STATUS.md) |
| You're going to touch the code and need the exact contracts | [`docs/pdr/02_Interface_Contracts_ICD.md`](docs/pdr/02_Interface_Contracts_ICD.md) |
| You want the full design (**a design doc, not a status report**) | [`docs/DRE_TECHNICAL_ARCHITECTURE.md`](docs/DRE_TECHNICAL_ARCHITECTURE.md) |
| You want to see how I write requirements before coding | [`docs/specs/`](docs/specs/) |
| You want the honest critique of this very repo | [`AUDIT.md`](AUDIT.md) |
| You're running the MAT lab step by step | [`docs/tutorial_quickstart.md`](docs/tutorial_quickstart.md) |
| Full index | [`docs/README.md`](docs/README.md) |

---

## Why this repo exists

I work from a simple conviction: **a system that can't explain how it reached its
current state isn't trustworthy, no matter how often it's right.** So here governance
isn't a logging layer bolted on top of the engine — it *is* the engine: the FSM fails
loudly on an undeclared transition, the ledger is append-only, idempotency is keyed on
`(run_id, data_hash)` rather than a timestamp, and `resume` is tested by comparing the
whole context, not just the final state.

The design calls I'll defend, in order: **explicit contracts** over conventions;
**reproducibility** (seeds, synthetic dataset, versioned metric contracts) over
flattering results; and **stating what's missing** over inflating what's there —
which is why this repo ships an [AUDIT.md](AUDIT.md) that criticizes it.

I'm looking for **backend / platform / data infrastructure** roles where correctness
and auditability matter more than feature velocity. If you're building long-running
orchestration, resumable pipelines, or systems with audit requirements, get in touch —
and if you find a claim in this repo that doesn't hold up, open an issue: that's the
contribution I value most.

---

## Quality gates

```bash
ruff check . && ruff format --check .   # lint + format (ruff pinned exactly)
pytest tests/ -q                        # 48 tests
bash scripts/demo_dre.sh                # end-to-end demo
```

CI runs both on Python 3.11 and 3.12, generates the synthetic dataset, runs the MAT
smoke check and validates build artifacts with `twine check --strict`.

## Installing as a package

The wheel ships the `dre/` engine plus the MAT modules. The HTTP API is an extra:

```bash
pip install "git+https://github.com/emilianob-ux/decision-resilience-engine.git"
```

To evaluate the repo, **clone it**: the demo and the tests live in the repository, not
in the wheel.

<sub><b>PyPI note.</b> This project was historically published as
<code>sistema-optimizacion-mat</code> (latest there: 0.2.0, MAT modules only). The new
name <code>decision-resilience-engine</code> is <b>not on PyPI yet</b>. The checklist
for the first upload is in
<a href="docs/PUBLISHING_PYPI.md"><code>docs/PUBLISHING_PYPI.md</code></a>.</sub>

## License and security

- License: [MIT](LICENSE) · Vulnerability reports: [SECURITY.md](SECURITY.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
