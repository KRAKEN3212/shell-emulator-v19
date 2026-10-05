"""Тесты команд-заглушек этапа 1."""

import unittest

from src.shell import Shell


class StubTest(unittest.TestCase):
    """ls и cd выводят своё имя и аргументы."""

    def test_ls_stub(self):
        """ls выводит имя и раскрытые аргументы."""
        shell = Shell(env={"HOME": "/h"})
        self.assertEqual(shell.execute("ls -a $HOME"),
                         "[stub] ls '-a' '/h'")

    def test_cd_stub(self):
        """cd без аргументов выводит только имя."""
        self.assertEqual(Shell(env={}).execute("cd"), "[stub] cd")


if __name__ == "__main__":
    unittest.main()
