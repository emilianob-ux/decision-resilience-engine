# Changelog

Format based on Keep a Changelog.

## [Unreleased]

### Fixed

- **`scripts/run_dre_api.py` no arrancaba nunca** (`ModuleNotFoundError: No module
  named 'dre'`): al invocar el script por ruta, Python antepone `scripts/` a
  `sys.path`, no la raíz del repo. Era el primer comando del quickstart del README.
- **CI con rojo latente:** `ruff>=0.9,<1` + `ruff format --check .` fallaba con
  `ruff 0.9.10` (por `compound_optimize_runner.py`) y con `0.16.7` (por un snippet
  Markdown). `ruff` pineado exacto a `0.16.7` en `requirements-dev.txt`,
  `pyproject.toml` y `.pre-commit-config.yaml` (que además apuntaba a `v0.15.12`).
- **Dos de los tres diagramas Mermaid no renderizaban en GitHub** (paréntesis sin
  comillas en etiquetas `[...]` y `\n` literal). Validado: 3/3 parsean con `mermaid@11`.
- `import dre` exigía FastAPI porque `dre/__init__.py` importaba `create_app` de
  forma ansiosa; ahora es un import perezoso (PEP 562).
- BOM UTF-8 al inicio de `README.md` y `CHANGELOG.md`; carácter U+FFFD en
  `data/__init__.py`.
- `.gitignore` no cubría `data/*.sqlite`: correr la demo dejaba el ledger listo para
  commitear por accidente.

### Added

- `AUDIT.md`: auditoría honesta del repo (mapa documentado vs. implementado,
  scorecard antes/después, backlog P0/P1/P2 con esfuerzo y riesgo).
- `SHORT_PITCH.md`: pitches de 15 s y 60 s (ES/EN), bullets para CV y tres preguntas
  de entrevista con respuestas honestas sobre los límites del MVP.
- `scripts/demo_dre.sh`: demo completa en un comando (~2.2 s) — health, camino feliz,
  resume, idempotencia, colisión 409 y volcado de la bitácora con las 9 transiciones.
- `tests/test_dre_invariants.py`: 8 tests de invariantes (bitácora encadenada,
  idempotencia sin fila duplicada, colisión tipada, resume idéntico campo por campo,
  FSM validada como grafo).
- `tests/test_docs_contract.py`: guardas anti-deriva — el ICD debe ser copia literal
  de `dre/contracts/`, los diagramas Mermaid deben poder renderizar, y el entrypoint
  de la API debe importar.
- `tests/test_dre_api.py`: 4 tests de contrato (422 en `run_id` malformado, 422 en
  variante desconocida, 404 en resume inexistente, camino `intervention`).
- `.github/ISSUE_TEMPLATE/` (incluye *"un claim no se sostiene"*) y `CONTRIBUTING.md`.
- `docs/specs/`: specs de diseño restauradas desde `362dff1^` (requisitos con IDs y
  tabúes anti *curve-fitting*; control PI con anti-windup), con mojibake reparado.
- Extra opcional `api` en `pyproject.toml` (FastAPI + uvicorn).

### Changed

- **La wheel ahora incluye el motor `dre/`.** El paquete llamado
  `decision-resilience-engine` entregaba solo los módulos MAT. `pydantic` y `scipy`
  pasan a dependencias base; la API HTTP queda en el extra `[api]`.
- `README.md` y `README.en.md` reescritos: problema y audiencia arriba, tabla
  "hoy vs roadmap", demo de un comando, diagrama de la FSM **implementada**, dos
  quickstarts separados (DRE / MAT), sección "por qué existe este repo". La
  instalación desde PyPI y el nombre legado `sistema-optimizacion-mat` bajan a una
  nota al pie.
- `docs/DRE_IMPLEMENTATION_STATUS.md` reescrito con alcance real por componente
  (sufijo *lite* donde corresponde), tabla de "diseñado pero no implementado" y
  brechas conocidas del MVP.
- `docs/DRE_TECHNICAL_ARCHITECTURE.md`: banner al inicio aclarando que es un
  documento de **diseño**, no de estado.
- `docs/pdr/`: nota de alcance — es un ejercicio de ingeniería de sistemas de una
  sola persona; las tablas de firmas son la plantilla del formato, no aprobaciones.
- `docs/pdr/02_Interface_Contracts_ICD.md`: los snippets ahora son copia literal del
  código, con tabla de diferencias deliberadas respecto del borrador v1.0.
- `docs/README.md` convertido en índice de navegación con columna "leé esto si…".
- `docs/LAUNCH_KIT.md`, `OUTREACH_EXECUTION.md` y `LAUNCH_DAY_CHECKLIST.md` movidos a
  `docs/internal/` (no son documentación del sistema).
- Workflow **Publish to PyPI**: validación automática **tag del release ↔ `project.version`**, `twine check --strict` antes de subir, `concurrency`, checkout por `refs/tags/…` en releases; `workflow_dispatch` por defecto **`main`**; job acotado al repo canónico.
- `docs/PUBLISHING_PYPI.md`: checklist operativo completo (PyPI + GitHub + release), pasos post-publicación y tabla de problemas frecuentes.

## [0.3.0] - 2026-05-06

### Changed

- Proyecto renombrado a **decision-resilience-engine**: repo GitHub, metadatos PyPI (`pip install decision-resilience-engine`), README y docs de outreach alineados.
- Prioridad narrativa: **DRE** como foco principal; **MAT** como puente de medicion secundario.

### Added

- `MANIFEST.in`: sdist sin `tests/`, `dre/` ni `scripts/` (wheel MAT sigue igual).
- CI: paso `python -m build` + `twine check --strict` sobre artefactos.
- Guia `docs/PUBLISHING_PYPI.md` (Trusted Publisher PyPI).

### Fixed

- BOM UTF-8 inicial en `pyproject.toml` que rompia `python -m build` en algunos entornos.

### Migration

- PyPI: el paquete **`sistema-optimizacion-mat`** deja de actualizarse en favor de **`decision-resilience-engine`** (nuevo nombre en el indice PyPI).

## [0.2.0] - 2026-05-06

### Added

- Decision Resilience Engine (DRE) MVP under `dre/`.
- DRE API endpoints: `POST /dre/simulate`, `POST /dre/resume`, `GET /dre/health`.
- SQLite governance checkpoints and `DrePipeline.resume_latest`.
- Redis-compatible context store (`RedisContextStore`) plus fakeredis tests.
- MAT bridge command: `dre/measurement/mat_runner.py`.
- Full PDR package in `docs/pdr/` and technical architecture doc.
- `docs/DRE_IMPLEMENTATION_STATUS.md` mapping spec to code.

### Changed

- README and docs index refreshed for MAT + DRE public presentation.
- Dev dependencies expanded with `scipy`, `fastapi`, `uvicorn`, `httpx`, `redis`, `fakeredis`.

### Removed

- Non-essential OSS/community template files removed earlier in this cycle.

## [0.1.4] - 2026-05-06

### Changed

- PyPI workflow supports `workflow_dispatch` with `git_ref` checkout.

## [0.1.3] - 2026-04-27

### Added

- PyPI release workflow (`publish-pypi.yml`).
- `ruff-format` pre-commit hook.

### Changed

- Repo-wide formatting and stricter Ruff config.

## [0.1.2] - 2026-04-27

### Added

- Ruff config, CI lint step, pre-commit baseline.

## [0.1.1] - 2026-04-27

### Added

- English README and quickstart/publishing docs.

## [0.1.0] - 2026-04-28

### Added

- Initial MAT backtesting engine, tests, CI, and docs.
