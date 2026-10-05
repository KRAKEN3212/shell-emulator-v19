"""Тесты параметров командной строки и загрузки скрипта."""

import os
import tempfile
import unittest
import unittest.mock

from src.config import Config, debug_lines, parse_config
from src.script import ScriptError, read_script


class ConfigTest(unittest.TestCase):
    """Разбор параметров --vfs и --script."""

    def test_defaults(self):
        """Без параметров оба пути не заданы."""
        self.assertEqual(parse_config([]), Config(None, None))

    def test_all_params(self):
        """Оба параметра разбираются."""
        config = parse_config(["--vfs", "a.json", "--script", "s.txt"])
        self.assertEqual(config, Config("a.json", "s.txt"))

    def test_debug_output(self):
        """Отладочный вывод содержит все параметры."""
        text = "\n".join(debug_lines(Config("a.json", None)))
        self.assertIn("vfs    = a.json", text)
        self.assertIn("script = <не задан>", text)

    def test_unknown_param(self):
        """Неизвестный параметр — ошибка argparse."""
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            with unittest.mock.patch("sys.stderr", devnull):
                with self.assertRaises(SystemExit):
                    parse_config(["--bad"])


class ScriptTest(unittest.TestCase):
    """Чтение стартового скрипта."""

    def test_skip_comments(self):
        """Комментарии и пустые строки пропускаются."""
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "s.txt")
            with open(path, "w", encoding="utf-8") as file:
                file.write("# c\n\nls\n  # c2\ncd / # tail\n")
            self.assertEqual(read_script(path), ["ls", "cd / # tail"])

    def test_missing_script(self):
        """Отсутствующий скрипт — ScriptError."""
        with self.assertRaises(ScriptError):
            read_script("no/such/file.txt")


if __name__ == "__main__":
    unittest.main()
