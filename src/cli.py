"""Точка входа CLI-приложения."""

import sys

from .config import (
    REGISTRY_MODE,
    build_parser,
    configuration_from_args,
    print_configuration,
)
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
    from .config import print_configuration

    print_configuration(config)
    if config.mode != REGISTRY_MODE:
        parser.error("режим test будет добавлен на этапе 3")
    try:
        dependencies = fetch_direct_dependencies(
            config.package_name, config.repository
        )
    except DependencySourceError as exc:
        print(f"ошибка: {exc}", file=sys.stderr)
        return FAILURE

    print(f"Прямые зависимости {config.package_name}:")
    for dependency in dependencies:
        print(f"  {dependency}")
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
