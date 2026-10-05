"""Тесты загрузки VFS и разрешения путей."""

import os
import unittest

from src.shell import Shell
from src.vfs import VfsError, load_vfs

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples", "vfs")


def example(name):
    """Путь к примеру VFS из каталога examples/vfs."""
    return os.path.join(EXAMPLES, name + ".json")


class LoadTest(unittest.TestCase):
    """Загрузка разных вариантов VFS."""

    def test_minimal(self):
        """Минимальная VFS — только корень."""
        self.assertEqual(load_vfs(example("minimal")).stats(), (1, 0, 0))

    def test_files(self):
        """Несколько файлов, включая base64."""
        vfs = load_vfs(example("files"))
        logo = vfs.resolve("/logo.bin")
        self.assertTrue(logo.content.startswith(b"\x89PNG"))

    def test_deep(self):
        """Не менее трёх уровней вложенности."""
        vfs = load_vfs(example("deep"))
        node = vfs.resolve("/home/artyom/projects/shell/main.py")
        self.assertEqual(node.content, b"print('hi')\n")

    def test_errors(self):
        """Отсутствующий файл, битый JSON, неверная структура."""
        for name in ("no_such_file", "broken", "bad_structure",
                     "bad_base64"):
            with self.subTest(name=name):
                with self.assertRaises(VfsError):
                    load_vfs(example(name))


class ResolveTest(unittest.TestCase):
    """Разрешение абсолютных и относительных путей."""

    def setUp(self):
        """VFS с глубокой структурой."""
        self.vfs = load_vfs(example("deep"))

    def test_paths(self):
        """., .. и повторные разделители."""
        self.vfs.cwd = self.vfs.resolve("/home/artyom")
        node = self.vfs.resolve("./projects/../hello.txt")
        self.assertEqual(node.path(), "/home/artyom/hello.txt")
        self.assertEqual(self.vfs.resolve("//etc///").path(), "/etc")
        self.assertIs(self.vfs.resolve("/.."), self.vfs.root)

    def test_missing(self):
        """Несуществующий путь и путь через файл."""
        with self.assertRaises(VfsError):
            self.vfs.resolve("/nope")
        with self.assertRaises(VfsError):
            self.vfs.resolve("/etc/motd/x")

    def test_vfs_info(self):
        """Служебная команда vfs-info."""
        output = Shell(self.vfs, env={}).execute("vfs-info")
        self.assertIn("files:  7", output)


if __name__ == "__main__":
    unittest.main()
