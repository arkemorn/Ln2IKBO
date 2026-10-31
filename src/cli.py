"""Точка входа CLI-приложения."""

import sys
from functools import partial

from .config import (
    REGISTRY_MODE,
    TEST_MODE,
    build_parser,
    configuration_from_args,
    print_configuration,
)
from .graph import (
    build_dependency_graph,
    find_reverse_dependencies,
    get_test_dependencies,
)
from .graph_repository import TestRepositoryError, load_test_graph
from .npm_registry import DependencySourceError, fetch_direct_dependencies

SUCCESS = 0
FAILURE = 1


def main(argv=None):
    """Разбирает параметры и выводит прямые зависимости пакета."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = configuration_from_args(args)
    except ValueError as exc:
        parser.error(str(exc))
    print_configuration(config)
    if config.reverse:
        return _run_reverse_mode(config)
    try:
        graph = _load_dependency_graph(config)
    except (DependencySourceError, TestRepositoryError) as exc:
        print(f"ошибка: {exc}", file=sys.stderr)
        return FAILURE

    print(f"Прямые зависимости {config.package_name}:")
    for dependency in graph[config.package_name]:
        print(f"  {dependency}")
    print("Граф зависимостей:")
    for package_name, dependencies in graph.items():
        value = ", ".join(dependencies) or "(нет)"
        print(f"{package_name}: {value}")
    return SUCCESS


def _run_reverse_mode(config):
    """Печатает обратные зависимости из полного тестового графа."""
    try:
        repository_graph = load_test_graph(config.repository)
    except TestRepositoryError as exc:
        print(f"ошибка: {exc}", file=sys.stderr)
        return FAILURE
    if config.package_name not in repository_graph:
        print(
            f"ошибка: пакет {config.package_name} отсутствует в тестовом графе",
            file=sys.stderr,
        )
        return FAILURE

    dependencies = find_reverse_dependencies(
        repository_graph, config.package_name
    )
    print(f"Обратные зависимости {config.package_name}:")
    for dependency in dependencies:
        print(f"  {dependency}")
    return SUCCESS


def _load_dependency_graph(config):
    """Выбирает источник данных и строит граф для корневого пакета."""
    if config.mode == TEST_MODE:
        repository_graph = load_test_graph(config.repository)
        if config.package_name not in repository_graph:
            raise TestRepositoryError(
                f"пакет {config.package_name} отсутствует в тестовом графе"
            )
        dependency_loader = partial(
            get_test_dependencies, repository_graph
        )
    elif config.mode == REGISTRY_MODE:
        dependency_loader = partial(
            fetch_direct_dependencies, repository_url=config.repository
        )
    else:
        raise ValueError(f"неподдерживаемый режим: {config.mode}")
    return build_dependency_graph(config.package_name, dependency_loader)


if __name__ == "__main__":
    raise SystemExit(main())
