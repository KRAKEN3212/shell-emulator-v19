"""Точка входа: python -m src.main [--vfs PATH] [--script PATH]."""

import sys

from src.app import EmulatorApp
from src.config import debug_lines, parse_config
from src.shell import Shell


def main(argv=None):
    """Разбирает параметры, создаёт сеанс эмулятора и открывает окно."""
    config = parse_config(argv)
    for line in debug_lines(config):
        print(line)
    app = EmulatorApp(Shell())
    app.write_lines(debug_lines(config), "debug")
    if config.script_path:
        app.schedule_script(config.script_path)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
