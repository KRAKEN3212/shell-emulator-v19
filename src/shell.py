"""Ядро эмулятора: разбор строки и вызов команд.

Модуль не зависит от GUI, поэтому его удобно тестировать.
"""

import getpass
import socket

from src import commands
from src.parser import ParseError, parse
from src.vfs import Vfs


def get_user_host():
    """Возвращает имя пользователя и имя хоста реальной ОС."""
    try:
        user = getpass.getuser()
    except (KeyError, OSError):
        user = "user"
    return user, socket.gethostname()


def _format_error(name, error):
    """Вывод команды до ошибки и сообщения об ошибках с её именем."""
    lines = [error.output] if error.output else []
    lines.extend(f"{name}: {message}"
                 for message in str(error).splitlines())
    return "\n".join(lines)


class Shell:
    """Состояние сеанса эмулятора и выполнение команд."""

    def __init__(self, vfs=None, env=None):
        """Создаёт сеанс.

        vfs — виртуальная файловая система (по умолчанию пустая),
        env — переменные окружения для парсера (по умолчанию ОС).
        """
        self.vfs = vfs or Vfs.empty()
        self.env = env
        self.user, self.host = get_user_host()
        self.running = True
        self.exit_code = 0
        self.last_failed = False
        self.commands = commands.REGISTRY

    def title(self):
        """Заголовок окна в формате 'Эмулятор - [user@host]'."""
        return f"Эмулятор - [{self.user}@{self.host}]"

    def prompt(self):
        """Строка приглашения к вводу."""
        return f"{self.user}@{self.host}:{self.vfs.cwd.path()}$ "

    def execute(self, line):
        """Выполняет одну строку и возвращает текст вывода.

        Ошибки разбора и выполнения не прерывают работу эмулятора,
        а возвращаются в виде сообщения, как в настоящей оболочке.
        """
        self.last_failed = True
        try:
            words = parse(line, self.env)
        except ParseError as error:
            return f"emulator: syntax error: {error}"
        if not words:
            self.last_failed = False
            return ""
        name, args = words[0], words[1:]
        handler = self.commands.get(name)
        if handler is None:
            return f"{name}: command not found"
        try:
            result = handler(self, args)
        except commands.CommandError as error:
            return _format_error(name, error)
        self.last_failed = False
        return result
