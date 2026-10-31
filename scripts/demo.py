"""Создаёт PNG-примеры для трёх узлов тестового графа."""

from pathlib import Path

from src.cli import main as run_visualizer

ROOT_DIRECTORY = Path(__file__).resolve().parents[1]
GRAPH_FILE = ROOT_DIRECTORY / "testdata" / "graphs" / "multiple.json"
OUTPUT_DIRECTORY = ROOT_DIRECTORY / "output"
DEMO_PACKAGES = ("A", "B", "F")
SUCCESS = 0


def main():
    """Строит PNG и DOT-файлы для демонстрационных узлов."""
    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    for package_name in DEMO_PACKAGES:
        output_file = OUTPUT_DIRECTORY / f"{package_name}.png"
        result = run_visualizer(
            [
                "--mode",
                "test",
                "--package",
                package_name,
                "--repository",
                str(GRAPH_FILE),
                "--output",
                str(output_file),
            ]
        )
        if result != SUCCESS:
            return result
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
