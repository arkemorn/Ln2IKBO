"""Тесты прямого чтения npm metadata без доступа к сети."""

import io
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from src.npm_registry import (
    DependencySourceError,
    NPM_ACCEPT,
    fetch_direct_dependencies,
)


class NpmRegistryTests(unittest.TestCase):
    """Проверяет запросы и обработку npm registry ответов."""

    @patch("src.npm_registry.urlopen")
    def test_returns_sorted_direct_dependencies(self, urlopen_mock):
        """Извлекает только прямые зависимости из metadata."""
        response = io.BytesIO(
            b'{"dependencies":{"zebra":"^1","alpha":"~2"}}'
        )
        urlopen_mock.return_value = response

        result = fetch_direct_dependencies(
            "left-pad", "https://registry.npmjs.org"
        )

        self.assertEqual(result, ("alpha", "zebra"))
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://registry.npmjs.org/left-pad/latest",
        )
        self.assertEqual(request.get_header("Accept"), NPM_ACCEPT)

    @patch("src.npm_registry.urlopen")
    def test_encodes_scoped_package_name(self, urlopen_mock):
        """URL-кодирует slash в имени scoped-пакета."""
        urlopen_mock.return_value = io.BytesIO(b'{"dependencies":{}}')

        result = fetch_direct_dependencies(
            "@types/node", "https://registry.npmjs.org/"
        )

        self.assertEqual(result, ())
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "https://registry.npmjs.org/%40types%2Fnode/latest",
        )

    @patch("src.npm_registry.urlopen")
    def test_reports_http_errors(self, urlopen_mock):
        """Преобразует HTTP-ошибку в сообщение источника."""
        urlopen_mock.side_effect = HTTPError(
            "https://registry.npmjs.org/missing/latest",
            404,
            "Not Found",
            None,
            io.BytesIO(b""),
        )

        with self.assertRaisesRegex(DependencySourceError, "HTTP 404"):
            fetch_direct_dependencies(
                "missing", "https://registry.npmjs.org"
            )

    @patch("src.npm_registry.urlopen")
    def test_reports_connection_errors(self, urlopen_mock):
        """Преобразует ошибку соединения в понятную ошибку источника."""
        urlopen_mock.side_effect = URLError("offline")

        with self.assertRaisesRegex(DependencySourceError, "не удалось"):
            fetch_direct_dependencies(
                "left-pad", "https://registry.npmjs.org"
            )

    @patch("src.npm_registry.urlopen")
    def test_rejects_invalid_json(self, urlopen_mock):
        """Отклоняет тело ответа, которое нельзя разобрать как JSON."""
        urlopen_mock.return_value = io.BytesIO(b"not-json")

        with self.assertRaisesRegex(DependencySourceError, "JSON"):
            fetch_direct_dependencies(
                "left-pad", "https://registry.npmjs.org"
            )

    @patch("src.npm_registry.urlopen")
    def test_rejects_invalid_dependencies_field(self, urlopen_mock):
        """Отклоняет поле dependencies неверного типа."""
        urlopen_mock.return_value = io.BytesIO(
            b'{"dependencies":["alpha"]}'
        )

        with self.assertRaisesRegex(DependencySourceError, "неверный формат"):
            fetch_direct_dependencies(
                "left-pad", "https://registry.npmjs.org"
            )


if __name__ == "__main__":
    unittest.main()
