#!/usr/bin/env python3
"""Servidor HTTP de desarrollo para la API DRE.

Ejecutable directamente desde la raíz del repo (`python scripts/run_dre_api.py`).
Python coloca `scripts/` —no la raíz— al frente de `sys.path` cuando se invoca un
script por ruta, así que insertamos la raíz igual que el resto de los wrappers
de `scripts/` para poder importar el paquete `dre` sin instalarlo.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import uvicorn  # noqa: E402

from dre.api.app import create_app  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Decision Resilience Engine — API dev")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/dre_governance.sqlite"),
        help="Ruta SQLite governance (append-only MVP)",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    args.db.parent.mkdir(parents=True, exist_ok=True)
    app = create_app(governance_db_path=args.db)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
