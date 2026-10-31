"""Тесты параметров запуска и обработки их ошибок."""

import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path

from src.config import (
    AppConfig,
    ConfigurationError,
    TEST_MODE,
    build_parser,
    validate_configuration,
)


class ConfigurationTests(unittest.TestCase):
    """Проверяет валидные и ошибочные значения конфигурации."""

    def test_accepts_registry_configuration(self):
        """Разрешает корректный npm-пакет и URL реестра."""
        config = AppConfig(
            "left-pad",
            "https://registry.npmjs.org",
            "registry",
            Path("graph.png"),
        )
        validate_configuration(config)

    def test_accepts_test_configuration(self):
        """Разрешает верхнеуровневый узел тестового графа."""
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory) / "graph.json"
            graph.write_text("{}", encoding="utf-8")
            config = AppConfig("A", str(graph), TEST_MODE, Path("g.png"))
            validate_configuration(config)

    def test_rejects_invalid_registry_package(self):
        """Отклоняет имя, которое не соответствует формату npm."""
        config = AppConfig(
            "bad name", "https://registry.npmjs.org", "registry",
            Path("graph.png"),
        )
        with self.assertRaisesRegex(ConfigurationError, "имя пакета"):
            validate_configuration(config)

    def test_rejects_dot_as_registry_package(self):
        """Не принимает относительный путь за имя npm-пакета."""
        config = AppConfig(
            "..", "https://registry.npmjs.org", "registry", Path("g.png")
        )
        with self.assertRaisesRegex(ConfigurationError, "имя пакета"):
            validate_configuration(config)

    def test_rejects_invalid_test_package(self):
        """Отклоняет тестовые имена вне диапазона A-Z."""
        with tempfile.TemporaryDirectory() as directory:
            graph = Path(directory) / "graph.json"
            graph.write_text("{}", encoding="utf-8")
            config = AppConfig("a", str(graph), TEST_MODE, Path("g.png"))
            with self.assertRaisesRegex(ConfigurationError, "A-Z"):
                validate_configuration(config)

    def test_rejects_invalid_repository_url(self):
        """Отклоняет URL без схемы или домена."""
        config = AppConfig("left-pad", "registry.npmjs.org", "registry",
                           Path("graph.png"))
        with self.assertRaisesRegex(ConfigurationError, "URL"):
            validate_configuration(config)

    def test_rejects_missing_test_repository(self):
        """Отклоняет путь, не указывающий на существующий файл."""
        config = AppConfig("A", "missing.json", TEST_MODE, Path("g.png"))
        with self.assertRaisesRegex(ConfigurationError, "не найден"):
            validate_configuration(config)

    def test_rejects_non_png_output(self):
        """Отклоняет путь результата с другим расширением."""
        config = AppConfig(
            "left-pad", "https://registry.npmjs.org", "registry",
            Path("graph.svg"),
        )
        with self.assertRaisesRegex(ConfigurationError, "расширение .png"):
            validate_configuration(config)

    def test_rejects_missing_output_directory(self):
        """Отклоняет несуществующий каталог вывода."""
        config = AppConfig(
            "left-pad", "https://registry.npmjs.org", "registry",
            Path("missing/graph.png"),
        )
        with self.assertRaisesRegex(ConfigurationError, "каталог"):
            validate_configuration(config)

    def test_rejects_registry_reverse_mode(self):
        """Не обещает reverse-зависимости вне полного тестового графа."""
        config = AppConfig(
            "left-pad",
            "https://registry.npmjs.org",
            "registry",
            Path("graph.png"),
            reverse=True,
        )
        with self.assertRaisesRegex(ConfigurationError, "полного тестового"):
            validate_configuration(config)

    def test_parser_rejects_unknown_mode(self):
        """Показывает ошибку, если режим не входит в допустимые значения."""
        parser = build_parser()
        arguments = [
            "--package",
            "debug",
            "--repository",
            "https://registry.npmjs.org",
            "--mode",
            "unknown",
        ]
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(arguments)


if __name__ == "__main__":
    unittest.main()
