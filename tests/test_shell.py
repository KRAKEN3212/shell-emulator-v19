"""Тесты ядра эмулятора (без GUI)."""

import unittest

from src.shell import Shell

ENV = {"HOME": "/home/artyom"}


class ShellTest(unittest.TestCase):
    """Выполнение строк, ошибки, команда exit."""

    def setUp(self):
        """Новый сеанс для каждого теста."""
        self.shell = Shell(env=ENV)

    def test_title(self):
        """Заголовок содержит пользователя и хост ОС."""
        expected = f"Эмулятор - [{self.shell.user}@{self.shell.host}]"
        self.assertEqual(self.shell.title(), expected)

    def test_unknown_command(self):
        """Неизвестная команда — сообщение об ошибке."""
        self.assertEqual(self.shell.execute("foo 1"),
                         "foo: command not found")
        self.assertTrue(self.shell.last_failed)

    def test_syntax_error(self):
        """Синтаксическая ошибка не роняет эмулятор."""
        self.assertIn("syntax error", self.shell.execute("ls 'x"))
        self.assertTrue(self.shell.running)

    def test_exit(self):
        """exit завершает сеанс с кодом."""
        self.shell.execute("exit 3")
        self.assertFalse(self.shell.running)
        self.assertEqual(self.shell.exit_code, 3)

    def test_exit_errors(self):
        """exit с неверными аргументами не завершает сеанс."""
        self.assertIn("numeric argument required",
                      self.shell.execute("exit abc"))
        self.assertIn("too many arguments", self.shell.execute("exit 1 2"))
        self.assertTrue(self.shell.running)


if __name__ == "__main__":
    unittest.main()
