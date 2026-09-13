"""La documentación también es un contrato: si miente, el build falla.

Tres cosas que se rompieron en este repo sin que nadie se enterara hasta que un
lector abrió la página:

  D1. Dos de los tres diagramas Mermaid del doc de arquitectura no parseaban
      (paréntesis sin comillas dentro de `[...]`, `\\n` literal en las etiquetas):
      GitHub mostraba "Unable to render rich display" en lugar del diagrama.
  D2. Los snippets del ICD habían divergido del código que dicen espejar.
  D3. `python scripts/run_dre_api.py` fallaba con `ModuleNotFoundError: dre`,
      es decir el quickstart del README no arrancaba.

Estos tests son baratos y atrapan exactamente esas tres regresiones.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_MERMAID_BLOCK = re.compile(r"```mermaid\n(.*?)```", re.S)
# Etiquetas de nodo tipo A[...], A[(...)], A{{...}} en diagramas flowchart.
_NODE_LABEL = re.compile(r"\[\(?(?P<label>[^\]\[]*?)\)?\]")


def _mermaid_blocks() -> list[tuple[Path, int, str]]:
    out: list[tuple[Path, int, str]] = []
    for md in sorted(ROOT.rglob("*.md")):
        if ".git" in md.parts or "node_modules" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for m in _MERMAID_BLOCK.finditer(text):
            line = text[: m.start()].count("\n") + 1
            out.append((md.relative_to(ROOT), line, m.group(1)))
    return out


class TestMermaidRenders(unittest.TestCase):
    def test_d1_no_unquoted_parens_in_node_labels(self) -> None:
        """`A[Texto (x)]` es un error de sintaxis en Mermaid; hay que citarlo."""
        offenders: list[str] = []
        for path, line, code in _mermaid_blocks():
            if not code.lstrip().startswith(("flowchart", "graph")):
                continue
            for match in _NODE_LABEL.finditer(code):
                label = match.group("label")
                if label.startswith('"') or label.endswith('"'):
                    continue
                if "(" in label or ")" in label:
                    offenders.append(f"{path}:{line} -> {match.group(0)}")
        self.assertEqual(offenders, [], "etiquetas Mermaid con paréntesis sin comillas")

    def test_d1b_no_literal_backslash_n_in_labels(self) -> None:
        """Mermaid moderno no interpreta `\\n`; hay que usar `<br/>`."""
        offenders = [f"{path}:{line}" for path, line, code in _mermaid_blocks() if "\\n" in code]
        self.assertEqual(offenders, [], "usar <br/> en lugar de \\n en etiquetas Mermaid")

    def test_d1c_at_least_one_diagram_exists(self) -> None:
        self.assertGreater(len(_mermaid_blocks()), 0)


class TestIcdMirrorsCode(unittest.TestCase):
    """El ICD dice espejar `dre/contracts/`. Se verifica, no se confía."""

    ICD = ROOT / "docs" / "pdr" / "02_Interface_Contracts_ICD.md"

    def test_d2_contract_snippets_are_verbatim(self) -> None:
        icd = self.ICD.read_text(encoding="utf-8")
        for rel in ("dre/contracts/stress_feedback.py", "dre/contracts/orchestrator_context.py"):
            code = (ROOT / rel).read_text(encoding="utf-8").strip()
            self.assertIn(
                code,
                icd,
                f"{rel} cambió y {self.ICD.name} quedó desactualizado: "
                f"pegá el archivo actual en el snippet correspondiente.",
            )


class TestQuickstartRuns(unittest.TestCase):
    def test_d3_api_entrypoint_imports_standalone(self) -> None:
        """Ejecutar el script por ruta debe importar `dre` sin instalar el paquete.

        Se invoca con `--help` para no levantar el servidor: alcanza para probar
        que los imports de módulo resuelven, que es lo que estaba roto.
        """
        proc = subprocess.run(
            [sys.executable, "scripts/run_dre_api.py", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("--db", proc.stdout)

    def test_d3b_demo_script_is_executable_and_valid_bash(self) -> None:
        demo = ROOT / "scripts" / "demo_dre.sh"
        self.assertTrue(demo.exists(), "falta scripts/demo_dre.sh")
        proc = subprocess.run(["bash", "-n", str(demo)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
