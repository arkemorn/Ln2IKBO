"""Тесты DOT-вывода и вызова Graphviz."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.visualization import (
    PNG_SIGNATURE,
    VisualizationError,
    graph_to_dot,
    render_graph,
)


class VisualizationTests(unittest.TestCase):
    """Проверяет DOT-экранирование и PNG-результат."""

    def test_generates_dot_nodes_and_edges(self):
        """Формирует стабильный Graphviz digraph."""
        dot = graph_to_dot({"B": (), "A": ("B",)})
        self.assertIn('"A" -> "B";', dot)
        self.assertIn('"B";', dot)
        self.assertLess(dot.index('"A";'), dot.index('"B";'))

    def test_escapes_quotes_and_backslashes(self):
        """Экранирует специальные символы в именах узлов."""
        dot = graph_to_dot({'A"B': ("C\\D",)})
        self.assertIn(r'"A\"B" -> "C\\D";', dot)

    @patch("src.visualization.subprocess.run")
    @patch("src.visualization.shutil.which", return_value="dot.exe")
    def test_renders_png_and_saves_dot(self, _which_mock, run_mock):
        """Запускает Graphviz, проверяет PNG и сохраняет исходный DOT."""
        with tempfile.TemporaryDirectory() as directory:
            output_file = Path(directory) / "graph.png"

            def write_png(command, **_kwargs):
                """Записывает минимальную сигнатуру PNG как mock Graphviz."""
                index = command.index("-o")
                output_path = Path(command[index + 1])
                output_path.write_bytes(PNG_SIGNATURE + b"data")
                return subprocess.CompletedProcess(command, 0, "", "")

            run_mock.side_effect = write_png
            dot_path = render_graph({"A": ("B",), "B": ()}, output_file)

            self.assertEqual(dot_path, output_file.with_suffix(".dot"))
            self.assertTrue(dot_path.is_file())
            self.assertTrue(output_file.read_bytes().startswith(PNG_SIGNATURE))
            self.assertTrue(run_mock.call_args.kwargs["text"])

    @patch("src.visualization.shutil.which", return_value=None)
    def test_reports_missing_graphviz(self, _which_mock):
        """Сообщает, когда исполняемый файл Graphviz не найден."""
        with tempfile.TemporaryDirectory() as directory:
            output_file = Path(directory) / "graph.png"
            with self.assertRaisesRegex(VisualizationError, "не найден"):
                render_graph({"A": ()}, output_file)
            self.assertTrue(output_file.with_suffix(".dot").is_file())

    @patch("src.visualization.subprocess.run")
    @patch("src.visualization.shutil.which", return_value="dot.exe")
    def test_rejects_invalid_png_signature(self, _which_mock, run_mock):
        """Отклоняет результат Graphviz, не являющийся PNG."""
        with tempfile.TemporaryDirectory() as directory:
            output_file = Path(directory) / "graph.png"

            def write_invalid_file(command, **_kwargs):
                """Записывает неверный результат успешного процесса."""
                index = command.index("-o")
                Path(command[index + 1]).write_bytes(b"bad")
                return subprocess.CompletedProcess(command, 0, "", "")

            run_mock.side_effect = write_invalid_file
            with self.assertRaisesRegex(VisualizationError, "формата"):
                render_graph({"A": ()}, output_file)


if __name__ == "__main__":
    unittest.main()
