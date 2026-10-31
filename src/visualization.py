"""Формирование DOT-текста и PNG через Graphviz dot."""

import shutil
import subprocess
from pathlib import Path

DOT_COMMAND = "dot"
DOT_SUFFIX = ".dot"
PNG_FORMAT = "png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
RENDER_TIMEOUT_SECONDS = 60
SUCCESS = 0


class VisualizationError(RuntimeError):
    """Ошибка подготовки DOT-файла или изображения PNG."""


def graph_to_dot(graph):
    """Преобразует отображение смежности в язык диаграмм Graphviz."""
    lines = [
        "digraph dependencies {",
        '  graph [rankdir="LR"];',
        '  node [shape="box"];',
    ]
    for package_name in sorted(graph):
        lines.append(f"  {_quote(package_name)};")
        for dependency in sorted(graph[package_name]):
            edge = f"  {_quote(package_name)} -> {_quote(dependency)};"
            lines.append(edge)
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_graph(graph, output_file):
    """Сохраняет DOT рядом с PNG и запускает Graphviz без shell."""
    output_path = Path(output_file)
    dot_path = output_path.with_suffix(DOT_SUFFIX)
    dot_text = graph_to_dot(graph)
    try:
        dot_path.write_text(dot_text, encoding="utf-8")
    except OSError as exc:
        raise VisualizationError(
            f"не удалось записать DOT-файл: {dot_path}"
        ) from exc

    executable = shutil.which(DOT_COMMAND)
    if executable is None:
        raise VisualizationError(
            "Graphviz dot не найден; установите Graphviz и добавьте его в PATH"
        )

    command = [executable, f"-T{PNG_FORMAT}", "-o", str(output_path)]
    try:
        result = subprocess.run(
            command,
            input=dot_text,
            text=True,
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=RENDER_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise VisualizationError(
            f"не удалось запустить Graphviz: {exc}"
        ) from exc
    if result.returncode != SUCCESS:
        detail = result.stderr.strip() or "неизвестная ошибка Graphviz"
        raise VisualizationError(f"Graphviz завершился с ошибкой: {detail}")

    _validate_png(output_path)
    return dot_path


def _quote(value):
    """Экранирует строковое имя узла для DOT-идентификатора."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _validate_png(output_path):
    """Проверяет, что Graphviz создал файл с сигнатурой PNG."""
    try:
        with output_path.open("rb") as stream:
            signature = stream.read(len(PNG_SIGNATURE))
    except OSError as exc:
        raise VisualizationError(
            f"Graphviz не создал PNG-файл: {output_path}"
        ) from exc
    if signature != PNG_SIGNATURE:
        raise VisualizationError(
            f"Graphviz создал файл неверного формата: {output_path}"
        )
