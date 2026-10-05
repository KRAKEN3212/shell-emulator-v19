"""Точка входа: python -m src.main [--vfs PATH] [--script PATH]."""

import sys

from src.app import EmulatorApp
from src.config import debug_lines, parse_config
from src.shell import Shell
from src.vfs import Vfs, VfsError, load_vfs


def open_vfs(path):
    """Загружает VFS; при ошибке возвращает пустую VFS и текст ошибки."""
    if not path:
        return Vfs.empty(), None
    try:
        return load_vfs(path), None
    except VfsError as error:
        return Vfs.empty(), str(error)


def main(argv=None):
    """Разбирает параметры, создаёт сеанс эмулятора и открывает окно."""
    config = parse_config(argv)
    for line in debug_lines(config):
        print(line)
    vfs, vfs_error = open_vfs(config.vfs_path)
    app = EmulatorApp(Shell(vfs))
    app.write_lines(debug_lines(config), "debug")
    if vfs_error:
        app.write_lines([f"emulator: {vfs_error}",
                         "emulator: используется пустая VFS"], "error")
    if config.script_path:
        app.schedule_script(config.script_path)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
