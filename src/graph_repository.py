"""Загрузка полного графа из JSON тестового репозитория."""

import json
import re
from pathlib import Path

TEST_PACKAGE_PATTERN = re.compile(r"[A-Z]+")


class TestRepositoryError(ValueError):
    """Ошибка формата или содержимого тестового репозитория."""


def load_test_graph(repository_path):
    """Загружает JSON-словарь пакетов и проверяет имена узлов."""
    path = Path(repository_path)
    try:
        with path.open(encoding="utf-8") as stream:
            raw_graph = json.load(stream)
    except OSError as exc:
        raise TestRepositoryError(
            f"не удалось прочитать тестовый граф: {repository_path}"
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TestRepositoryError(
            f"тестовый граф не является корректным JSON: {repository_path}"
        ) from exc

    if not isinstance(raw_graph, dict):
        raise TestRepositoryError("корнем тестового JSON должен быть объект")

    graph = {}
    for package_name, dependencies in raw_graph.items():
        _validate_name(package_name)
        if not isinstance(dependencies, list):
            raise TestRepositoryError(
                f"зависимости пакета {package_name} должны быть списком"
            )
        for dependency in dependencies:
            _validate_name(dependency)
        graph[package_name] = tuple(sorted(set(dependencies)))
    return graph


def _validate_name(package_name):
    """Проверяет, что имя тестового пакета состоит из заглавных букв."""
    if not isinstance(package_name, str):
        raise TestRepositoryError("имя тестового пакета должно быть строкой")
    if not TEST_PACKAGE_PATTERN.fullmatch(package_name):
        raise TestRepositoryError(
            f"имя тестового пакета должно содержать только A-Z: {package_name}"
        )
