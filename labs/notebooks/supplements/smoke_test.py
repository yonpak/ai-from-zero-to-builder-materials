"""Run the self-contained optional PyTorch notebooks on CPU (not canonical Lab count)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NOTEBOOKS = ("p05-pytorch-reading.ipynb", "p07-transformer-shapes.ipynb")

def main():
    for name in NOTEBOOKS:
        path = ROOT / name
        notebook = json.loads(path.read_text(encoding="utf-8"))
        scope = {"__name__": "__main__"}
        assert notebook["nbformat"] == 4
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] == "code":
                exec(compile("".join(cell["source"]), f"{name}#cell-{index}", "exec"), scope, scope)
        print("PASS", name)

if __name__ == "__main__":
    main()
