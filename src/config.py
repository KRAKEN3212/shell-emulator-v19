"""Параметры командной строки эмулятора."""

import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Config:
    """Настройки запуска эмулятора."""

    vfs_path: Optional[str] = None
    script_path: Optional[str] = None


def build_arg_parser():
    """Создаёт парсер параметров командной строки."""
    parser = argparse.ArgumentParser(
        prog="emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС")
    parser.add_argument(
        "--vfs", dest="vfs_path", metavar="PATH",
        help="путь к физическому расположению VFS (JSON-файл)")
    parser.add_argument(
        "--script", dest="script_path", metavar="PATH",
        help="путь к стартовому скрипту эмулятора")
    return parser


def parse_config(argv=None):
    """Разбирает параметры argv и возвращает Config."""
    namespace = build_arg_parser().parse_args(argv)
    return Config(namespace.vfs_path, namespace.script_path)


def debug_lines(config):
    """Строки отладочного вывода всех заданных параметров."""
    return [
        "[debug] параметры запуска:",
        f"[debug]   vfs    = {config.vfs_path or '<не задан>'}",
        f"[debug]   script = {config.script_path or '<не задан>'}",
    ]
