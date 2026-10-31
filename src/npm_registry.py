"""Чтение npm package metadata через стандартный HTTP-клиент Python."""

import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin
from urllib.request import Request, urlopen

DEFAULT_TIMEOUT_SECONDS = 15
NPM_ACCEPT = (
    "application/vnd.npm.install-v1+json; q=1.0, "
    "application/json; q=0.8, */*"
)
USER_AGENT = "ikbo-dependency-visualizer/1.0"


class DependencySourceError(RuntimeError):
    """Ошибка получения или разбора метаданных пакета."""


def fetch_direct_dependencies(package_name, repository_url):
    """Возвращает прямые зависимости последней версии npm-пакета."""
    request = _build_metadata_request(package_name, repository_url)
    metadata = _fetch_metadata(request, package_name)
    return _extract_dependency_names(metadata, package_name)


def _build_metadata_request(package_name, repository_url):
    """Создаёт HTTP-запрос к metadata latest для одного пакета."""
    package_path = quote(package_name, safe="")
    endpoint = urljoin(
        repository_url.rstrip("/") + "/",
        f"{package_path}/latest",
    )
    request = Request(
        endpoint,
        headers={"Accept": NPM_ACCEPT, "User-Agent": USER_AGENT},
    )
    return request


def _fetch_metadata(request, package_name):
    """Получает JSON metadata и преобразует ошибки сети в прикладную."""
    try:
        with urlopen(request, timeout=DEFAULT_TIMEOUT_SECONDS) as response:
            metadata = json.load(response)
    except HTTPError as exc:
        raise DependencySourceError(
            f"npm registry вернул HTTP {exc.code} для {package_name}"
        ) from exc
    except (URLError, TimeoutError) as exc:
        raise DependencySourceError(
            f"не удалось получить {package_name}: {exc}"
        ) from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DependencySourceError(
            f"реестр вернул некорректный JSON для {package_name}"
        ) from exc
    if not isinstance(metadata, dict):
        raise DependencySourceError(
            "метаданные пакета должны быть JSON-объектом"
        )
    return metadata


def _extract_dependency_names(metadata, package_name):
    """Проверяет поле dependencies и возвращает отсортированные имена."""
    dependencies = metadata.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise DependencySourceError(
            f"поле dependencies пакета {package_name} имеет неверный формат"
        )
    if any(not isinstance(name, str) for name in dependencies):
        raise DependencySourceError(
            f"поле dependencies пакета {package_name} содержит неверные имена"
        )
    return tuple(sorted(dependencies))
