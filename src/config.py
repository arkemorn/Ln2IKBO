"""Разбор и проверка настроек приложения."""

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

PNG_SUFFIX = ".png"
TEST_MODE = "test"
REGISTRY_MODE = "registry"
TEST_PACKAGE_PATTERN = re.compile(r"[A-Z]+")
NPM_PACKAGE_PATTERN = re.compile(
    r"(?:@[a-z0-9._-]+/)?[a-z0-9._-]+"
)
VALID_MODES = (REGISTRY_MODE, TEST_MODE)


class ConfigurationError(ValueError):
    """Ошибка значения параметра командной строки."""


@dataclass(frozen=True)
class AppConfig:
    """Параметры одного запуска визуализатора."""

    package_name: str
    repository: str
    mode: str
    output_file: Path
    reverse: bool = False


def build_parser():
    """Создаёт парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        description="Построить граф зависимостей npm-пакета"
    )
    parser.add_argument("--package", required=True, help="имя пакета")
    parser.add_argument(
        "--repository",
        required=True,
        help="URL npm-реестра или путь к JSON-графу",
    )
    parser.add_argument(
        "--mode",
        choices=VALID_MODES,
        default=REGISTRY_MODE,
        help="режим работы: registry или test",
    )
    parser.add_argument(
        "--output",
        default="dependency-graph.png",
        help="путь к PNG-файлу",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="вывести обратные зависимости тестового пакета",
    )
    return parser


def configuration_from_args(args):
    """Создаёт проверенную конфигурацию из параметров argparse."""
    config = AppConfig(
        package_name=args.package,
        repository=args.repository,
        mode=args.mode,
        output_file=Path(args.output),
        reverse=args.reverse,
    )
    validate_configuration(config)
    return config


def validate_configuration(config):
    """Проверяет имя пакета, источник данных и путь результата."""
    _validate_package(config.package_name, config.mode)
    _validate_repository(config.repository, config.mode)
    _validate_output(config.output_file)
    if config.reverse and config.mode != TEST_MODE:
        raise ConfigurationError(
            "обратные зависимости требуют полного тестового графа"
        )


def _validate_package(package_name, mode):
    """Проверяет имя npm-пакета или тестового узла."""
    pattern = (
        TEST_PACKAGE_PATTERN if mode == TEST_MODE else NPM_PACKAGE_PATTERN
    )
    if not pattern.fullmatch(package_name):
        if mode == TEST_MODE:
            detail = "тестовые имена должны состоять из A-Z"
        else:
            detail = "ожидается допустимое имя npm-пакета"
        raise ConfigurationError(f"недопустимое имя пакета: {detail}")


def _validate_repository(repository, mode):
    """Проверяет путь тестового графа или URL npm-реестра."""
    if mode == TEST_MODE:
        if not Path(repository).is_file():
            raise ConfigurationError(
                f"файл тестового графа не найден: {repository}"
            )
        return

    parsed = urlparse(repository)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ConfigurationError(
            "repository должен быть URL с протоколом http или https"
        )


def _validate_output(output_file):
    """Проверяет расширение PNG и доступность каталога вывода."""
    if output_file.suffix.lower() != PNG_SUFFIX:
        raise ConfigurationError("путь output должен иметь расширение .png")
    if output_file.exists() and output_file.is_dir():
        raise ConfigurationError("путь output указывает на каталог")
    if not output_file.parent.is_dir():
        raise ConfigurationError(
            f"каталог для output не найден: {output_file.parent}"
        )


def print_configuration(config):
    """Печатает пользовательские параметры в формате ключ=значение."""
    print(f"package={config.package_name}")
    print(f"repository={config.repository}")
    print(f"mode={config.mode}")
    print(f"output={config.output_file}")
    print(f"reverse={str(config.reverse).lower()}")
