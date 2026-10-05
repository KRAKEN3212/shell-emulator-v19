"""Тесты команды rmdir (этап 5)."""

import unittest

from src.vfs import load_vfs
from tests.test_commands import DEEP, CommandTestCase


class RmdirTest(CommandTestCase):
    """Удаление пустых каталогов в памяти."""

    def test_remove_empty(self):
        """Пустой каталог удаляется."""
        self.run_ok("rmdir /home/guest")
        self.assertEqual(self.run_ok("ls /home"), "artyom")

    def test_remove_parents(self):
        """-p удаляет всю цепочку пустых каталогов."""
        self.run_ok("rmdir -p /tmp/a/b/c")
        self.assertEqual(self.run_ok("ls"), "etc\nhome\nvar")

    def test_parents_stop_at_non_empty(self):
        """-p останавливается на непустом каталоге с ошибкой."""
        output = self.run_fail("rmdir -p home/artyom/projects/old")
        self.assertIn("'home/artyom/projects': Directory not empty", output)
        self.assertEqual(self.run_ok("ls /home/artyom/projects"), "shell")

    def test_errors(self):
        """Ошибки rmdir."""
        cases = {
            "rmdir": "missing operand",
            "rmdir /nope": "No such file or directory",
            "rmdir /etc/motd": "Not a directory",
            "rmdir /etc": "Directory not empty",
            "rmdir /": "busy",
            "rmdir /tmp/.": "Invalid argument",
            "rmdir -x a": "invalid option",
        }
        for line, message in cases.items():
            with self.subTest(line=line):
                self.assertIn(message, self.run_fail(line))

    def test_busy_cwd(self):
        """Нельзя удалить текущий каталог и его предков."""
        self.run_ok("cd /tmp/a/b/c")
        self.assertIn("busy", self.run_fail("rmdir /tmp/a/b/c"))

    def test_source_file_untouched(self):
        """Файл VFS на диске не изменяется."""
        self.run_ok("rmdir /home/guest")
        self.assertIn("guest", load_vfs(DEEP).resolve("/home").children)


if __name__ == "__main__":
    unittest.main()
