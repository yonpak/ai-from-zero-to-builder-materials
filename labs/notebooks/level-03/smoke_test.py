from __future__ import annotations
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

def run_notebook(path: pathlib.Path) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(notebook.get("cells"), list):
        raise AssertionError(f"{path}: cells missing")
    namespace = {"__name__": f"smoke_{path.stem}"}
    for index, cell in enumerate(notebook["cells"]):
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell.get("source", []))
        exec(compile(source, f"{path}#cell-{index}", "exec"), namespace, namespace)

def main() -> None:
    notebooks = sorted(ROOT.glob("l03-*.ipynb"))
    if len(notebooks) != 4:
        raise AssertionError(f"expected 4 Level 3 notebooks, found {len(notebooks)}")
    for path in notebooks:
        run_notebook(path)
        print(f"PASS {path.name}")

if __name__ == "__main__":
    main()
