"""Тесты BFS, циклов и тестового файла графа."""

import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from src.graph import build_dependency_graph, find_reverse_dependencies
from src.graph_repository import TestRepositoryError, load_test_graph


class DependencyGraphTests(unittest.TestCase):
    """Проверяет построение транзитивного графа без рекурсии."""

    def test_builds_breadth_first_graph_with_a_cycle(self):
        """Обходит цикл и возвращает каждую вершину один раз."""
        source = {
            "A": ("B", "C"),
            "B": ("D",),
            "C": ("D",),
            "D": ("A",),
        }
        calls = Counter()

        def load(package_name):
            calls[package_name] += 1
            return source.get(package_name, ())

        graph = build_dependency_graph("A", load)

        self.assertEqual(list(graph), ["A", "B", "C", "D"])
        self.assertEqual(calls, Counter({"A": 1, "B": 1, "C": 1, "D": 1}))

    def test_handles_package_without_dependencies(self):
        """Создаёт граф с единственным листовым пакетом."""
        graph = build_dependency_graph("A", lambda _name: ())
        self.assertEqual(graph, {"A": ()})

    def test_deduplicates_edges(self):
        """Удаляет дубликаты зависимостей, не дублируя обход."""
        def load(package_name):
            return ("B", "B") if package_name == "A" else ()

        graph = build_dependency_graph("A", load)
        self.assertEqual(graph, {"A": ("B",), "B": ()})

    def test_finds_transitive_reverse_dependencies_with_a_cycle(self):
        """Обходит входящие рёбра и останавливается на цикле."""
        graph = {
            "A": ("B", "C"),
            "B": ("D",),
            "C": ("D",),
            "D": ("A",),
            "E": ("D",),
        }
        self.assertEqual(
            find_reverse_dependencies(graph, "D"),
            ("A", "B", "C", "E"),
        )

    def test_returns_no_reverse_dependencies_for_root(self):
        """Возвращает пустой список для узла без входящих рёбер."""
        self.assertEqual(find_reverse_dependencies({"A": ()}, "A"), ())


class TestRepositoryTests(unittest.TestCase):
    """Проверяет формат JSON-репозитория с именами A-Z."""

    def _write_graph(self, directory, value):
        """Записывает JSON во временный файл для одного теста."""
        path = Path(directory) / "graph.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def test_loads_graph_with_uppercase_names(self):
        """Читает и сортирует зависимости тестовых узлов."""
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_graph(directory, {"A": ["C", "B"]})
            self.assertEqual(load_test_graph(path), {"A": ("B", "C")})

    def test_rejects_lowercase_package_name(self):
        """Отклоняет тестовый узел с именем вне A-Z."""
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_graph(directory, {"a": []})
            with self.assertRaisesRegex(TestRepositoryError, "A-Z"):
                load_test_graph(path)

    def test_rejects_invalid_dependency_type(self):
        """Отклоняет зависимость, которая не является строкой A-Z."""
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_graph(directory, {"A": ["lower"]})
            with self.assertRaisesRegex(TestRepositoryError, "A-Z"):
                load_test_graph(path)

    def test_rejects_non_list_dependencies(self):
        """Отклоняет поле зависимостей, которое не является списком."""
        with tempfile.TemporaryDirectory() as directory:
            path = self._write_graph(directory, {"A": "B"})
            with self.assertRaisesRegex(TestRepositoryError, "списком"):
                load_test_graph(path)

    def test_rejects_invalid_json(self):
        """Сообщает об ошибке синтаксиса JSON-файла."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "graph.json"
            path.write_text("{invalid", encoding="utf-8")
            with self.assertRaisesRegex(TestRepositoryError, "JSON"):
                load_test_graph(path)


if __name__ == "__main__":
    unittest.main()
