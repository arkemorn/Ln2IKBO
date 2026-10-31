"""Показывает обработку ошибочных параметров командной строки."""

from src.cli import main as run_visualizer

SUCCESS = 0
ERROR_CASES = (
    (
        "package",
        ("--package", "bad name", "--repository", "https://registry.npmjs.org"),
    ),
    (
        "repository URL",
        ("--package", "debug", "--repository", "registry.npmjs.org"),
    ),
    (
        "mode",
        (
            "--package",
            "debug",
            "--repository",
            "https://registry.npmjs.org",
            "--mode",
            "unknown",
        ),
    ),
    (
        "output file",
        (
            "--package",
            "debug",
            "--repository",
            "https://registry.npmjs.org",
            "--output",
            "graph.svg",
        ),
    ),
    (
        "test repository path",
        (
            "--mode",
            "test",
            "--package",
            "A",
            "--repository",
            "missing.json",
        ),
    ),
)


def main():
    """Запускает CLI по очереди со всеми неверными параметрами."""
    for label, arguments in ERROR_CASES:
        print(f"\nОшибка параметра {label}:")
        try:
            run_visualizer(list(arguments))
        except SystemExit:
            continue
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
