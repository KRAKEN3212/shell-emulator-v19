"""Чтение стартового скрипта эмулятора."""

COMMENT_PREFIX = "#"


class ScriptError(Exception):
    """Ошибка загрузки стартового скрипта."""


def is_command(line):
    """True, если строка не пустая и не является комментарием."""
    text = line.strip()
    return bool(text) and not text.startswith(COMMENT_PREFIX)


def read_script(path):
    """Читает скрипт и возвращает список строк-команд.

    Пустые строки и строки-комментарии (начинающиеся с #)
    пропускаются. Комментарии в конце строки отбрасывает парсер.
    """
    try:
        with open(path, encoding="utf-8") as file:
            lines = file.read().splitlines()
    except FileNotFoundError as error:
        raise ScriptError(f"{path}: скрипт не найден") from error
    except UnicodeDecodeError as error:
        raise ScriptError(f"{path}: скрипт не в кодировке UTF-8") from error
    except OSError as error:
        raise ScriptError(f"{path}: {error.strerror}") from error
    return [line for line in lines if is_command(line)]
