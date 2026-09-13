"""Decision Resilience Engine (MVP).

`DrePipeline` es el núcleo y solo depende de pydantic/scipy/numpy. `create_app`
vive detrás de un import perezoso (PEP 562) porque arrastra FastAPI, que es un
extra opcional (`pip install "decision-resilience-engine[api]"`): importar el
motor no debería exigir un servidor HTTP.
"""

from typing import TYPE_CHECKING, Any

from dre.orchestrator import DrePipeline

if TYPE_CHECKING:  # pragma: no cover - solo para type checkers
    from dre.api import create_app

__all__ = ["DrePipeline", "create_app"]


def __getattr__(name: str) -> Any:
    if name == "create_app":
        from dre.api import create_app as _create_app

        return _create_app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
