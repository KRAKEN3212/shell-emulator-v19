"""Тесты команд ls, cd, find, rev."""

import os
import unittest

from src.shell import Shell
from src.vfs import load_vfs

DEEP = os.path.join(os.path.dirname(__file__), "..", "examples", "vfs",
                    "deep.json")


class CommandTestCase(unittest.TestCase):
    """Общая подготовка: сеанс с глубокой VFS."""

    def setUp(self):
        """Новый сеанс для каждого теста."""
        self.shell = Shell(load_vfs(DEEP), env={"HOME": "/home/artyom"})

    def run_ok(self, line):
        """Выполняет строку и проверяет, что ошибки нет."""
        output = self.shell.execute(line)
        self.assertFalse(self.shell.last_failed, output)
        return output

    def run_fail(self, line):
        """Выполняет строку и проверяет, что была ошибка."""
        output = self.shell.execute(line)
        self.assertTrue(self.shell.last_failed, output)
        return output


class LsTest(CommandTestCase):
    """Команда ls."""

    def test_root(self):
        """ls без аргументов — текущий каталог."""
        self.assertEqual(self.run_ok("ls"), "etc\nhome\ntmp\nvar")

    def test_long(self):
        """ls -l показывает тип и размер."""
        self.assertEqual(self.run_ok("ls -l /etc"),
                         "-        9 hostname\n-       40 motd")

    def test_file_and_dirs(self):
        """Файл-операнд и заголовки каталогов."""
        output = self.run_ok("ls /etc/motd /home /tmp")
        self.assertEqual(output,
                         "/etc/motd\n\n/home:\nartyom\nguest\n\n/tmp:\na")

    def test_errors(self):
        """Ошибка по одному операнду не мешает остальным."""
        output = self.run_fail("ls /nope /tmp")
        self.assertEqual(output, "/tmp:\na\n"
                         "ls: cannot access '/nope': "
                         "No such file or directory")
        self.assertIn("invalid option", self.run_fail("ls -z"))


class CdTest(CommandTestCase):
    """Команда cd."""

    def test_cd_and_prompt(self):
        """cd меняет каталог и приглашение."""
        self.run_ok("cd $HOME/projects")
        self.assertTrue(self.shell.prompt().endswith(
            ":/home/artyom/projects$ "))
        self.run_ok("cd ../..")
        self.assertEqual(self.shell.vfs.cwd.path(), "/home")

    def test_cd_home_and_back(self):
        """cd без аргументов — в корень, cd - — обратно."""
        self.run_ok("cd /var/log")
        self.run_ok("cd")
        self.assertEqual(self.run_ok("cd -"), "/var/log")

    def test_errors(self):
        """Ошибки cd."""
        self.assertIn("No such file", self.run_fail("cd /nope"))
        self.assertIn("Not a directory", self.run_fail("cd /etc/motd"))
        self.assertIn("too many", self.run_fail("cd a b"))
        self.assertEqual(self.shell.vfs.cwd.path(), "/")


class FindTest(CommandTestCase):
    """Команда find."""

    def test_all(self):
        """find без аргументов обходит текущий каталог."""
        self.run_ok("cd /tmp")
        self.assertEqual(self.run_ok("find"), ".\n./a\n./a/b\n./a/b/c")

    def test_filters(self):
        """Фильтры -name и -type."""
        self.assertEqual(self.run_ok("find / -name '*.txt'"),
                         "/home/artyom/hello.txt")
        self.assertEqual(self.run_ok("find /home -type d -name 'g*'"),
                         "/home/guest")
        self.assertEqual(self.run_ok("find /var -type f"),
                         "/var/log/system.log")

    def test_errors(self):
        """Ошибки find."""
        self.assertIn("unknown predicate", self.run_fail("find -size 1"))
        self.assertIn("missing argument", self.run_fail("find -name"))
        self.assertIn("Unknown argument", self.run_fail("find -type x"))
        self.assertIn("No such file", self.run_fail("find /nope"))


class RevTest(CommandTestCase):
    """Команда rev."""

    def test_rev(self):
        """Строки файла переворачиваются."""
        self.assertEqual(self.run_ok("rev /etc/motd"),
                         "rotalume eht ot emocleW\nyad ecin a evaH")
        self.assertEqual(self.run_ok("rev /home/artyom/hello.txt"),
                         "dlrow olleh\nstressed desserts")

    def test_errors(self):
        """Ошибки rev."""
        self.assertIn("missing file operand", self.run_fail("rev"))
        self.assertIn("Is a directory", self.run_fail("rev /etc"))
        self.assertIn("cannot open", self.run_fail("rev /nope"))


if __name__ == "__main__":
    unittest.main()
