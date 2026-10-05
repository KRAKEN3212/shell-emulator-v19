"""Точка входа: python -m src.main."""

import sys

from src.app import EmulatorApp
from src.shell import Shell


def main():
    """Создаёт сеанс эмулятора и открывает окно."""
    app = EmulatorApp(Shell())
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
