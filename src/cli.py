"""Точка входа CLI-приложения."""

from .config import build_parser, configuration_from_args

SUCCESS = 0


def main(argv=None):
    """Разбирает параметры, печатает их и завершает прототип."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = configuration_from_args(args)
    except ValueError as exc:
        parser.error(str(exc))
    from .config import print_configuration

    print_configuration(config)
    print("Конфигурация проверена.")
    return SUCCESS


if __name__ == "__main__":
    raise SystemExit(main())
