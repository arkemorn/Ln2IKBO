"""Обход графа зависимостей и построение транзитивного среза."""

from collections import deque
from collections.abc import Callable, Iterable

DependencyLoader = Callable[[str], Iterable[str]]
DependencyGraph = dict[str, tuple[str, ...]]


def build_dependency_graph(root_package, dependency_loader):
    """Строит достижимую часть графа обходом BFS без рекурсии."""
    graph = {}
    visited = set()
    queued = {root_package}
    pending = deque([root_package])

    while pending:
        package_name = pending.popleft()
        if package_name in visited:
            continue
        dependencies = tuple(sorted(set(dependency_loader(package_name))))
        graph[package_name] = dependencies
        visited.add(package_name)
        for dependency in dependencies:
            if dependency not in visited and dependency not in queued:
                pending.append(dependency)
                queued.add(dependency)

    return graph


def get_test_dependencies(repository_graph, package_name):
    """Возвращает прямые рёбра тестового узла или пустой список."""
    return repository_graph.get(package_name, ())


def find_reverse_dependencies(repository_graph, package_name):
    """Ищет BFS-пакеты, ведущие к выбранному узлу по обратным рёбрам."""
    reverse_graph = {}
    for dependent, dependencies in repository_graph.items():
        for dependency in dependencies:
            reverse_graph.setdefault(dependency, set()).add(dependent)

    visited = {package_name}
    pending = deque(reverse_graph.get(package_name, ()))
    while pending:
        dependent = pending.popleft()
        if dependent in visited:
            continue
        visited.add(dependent)
        pending.extend(reverse_graph.get(dependent, ()))

    visited.remove(package_name)
    return tuple(sorted(visited))
