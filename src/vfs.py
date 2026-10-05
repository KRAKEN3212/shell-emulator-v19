"""Виртуальная файловая система (VFS), загружаемая из JSON.

Формат файла VFS — вложенные объекты:

    {"type": "dir", "children": [
        {"name": "a.txt", "type": "file", "content": "текст"},
        {"name": "b.bin", "type": "file", "encoding": "base64",
         "content": "AAEC"},
        {"name": "docs", "type": "dir", "children": []}
    ]}

Корневой объект — каталог «/». Все операции выполняются в памяти,
исходный файл не изменяется.
"""

import base64
import binascii
import json

SEPARATOR = "/"
TYPE_DIR = "dir"
TYPE_FILE = "file"
ENCODINGS = ("text", "base64")
SPECIAL_NAMES = ("", ".", "..")


class VfsError(Exception):
    """Ошибка загрузки VFS или обращения к ней."""


class Node:
    """Файл или каталог VFS."""

    def __init__(self, name, is_dir, parent=None, content=b""):
        """Создаёт узел; для каталога content не используется."""
        self.name = name
        self.is_dir = is_dir
        self.parent = parent
        self.content = content
        self.children = {}

    def path(self):
        """Абсолютный путь узла."""
        parts = []
        node = self
        while node.parent is not None:
            parts.append(node.name)
            node = node.parent
        return SEPARATOR + SEPARATOR.join(reversed(parts))

    def sorted_children(self):
        """Дочерние узлы, упорядоченные по имени."""
        return [self.children[name] for name in sorted(self.children)]

    def walk(self):
        """Обходит поддерево в глубину, начиная с самого узла."""
        yield self
        for child in self.sorted_children():
            yield from child.walk()


class Vfs:
    """Дерево VFS и текущий каталог."""

    def __init__(self, root, source=None):
        """Создаёт VFS с корнем root; source — путь к JSON-файлу."""
        self.root = root
        self.cwd = root
        self.previous = root
        self.source = source

    @classmethod
    def empty(cls):
        """VFS из одного пустого корневого каталога."""
        return cls(Node("", True))

    def resolve(self, path):
        """Находит узел по абсолютному или относительному пути."""
        node = self.root if path.startswith(SEPARATOR) else self.cwd
        for part in path.split(SEPARATOR):
            if part in ("", "."):
                continue
            if not node.is_dir:
                raise VfsError("Not a directory")
            if part == "..":
                node = node.parent or node
            elif part in node.children:
                node = node.children[part]
            else:
                raise VfsError("No such file or directory")
        return node

    def stats(self):
        """Число каталогов, файлов и суммарный размер файлов."""
        nodes = list(self.root.walk())
        files = [node for node in nodes if not node.is_dir]
        size = sum(len(node.content) for node in files)
        return len(nodes) - len(files), len(files), size


def load_vfs(path):
    """Загружает VFS из JSON-файла path.

    Возбуждает VfsError, если файл не найден, не является JSON
    или имеет неверную структуру.
    """
    try:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        raise VfsError(f"{path}: файл VFS не найден") from error
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise VfsError(f"{path}: неверный формат JSON ({error})") from error
    except OSError as error:
        raise VfsError(f"{path}: {error.strerror}") from error
    if not isinstance(data, dict) or data.get("type") != TYPE_DIR:
        raise VfsError(f"{path}: корень VFS должен быть объектом-каталогом")
    root = Node("", True)
    try:
        _add_children(root, data, SEPARATOR)
    except VfsError as error:
        raise VfsError(f"{path}: неверная структура VFS: {error}") from error
    return Vfs(root, path)


def _add_children(parent, data, where):
    """Строит дочерние узлы каталога parent по описанию data."""
    children = data.get("children", [])
    if not isinstance(children, list):
        raise VfsError(f"{where}: поле children должно быть списком")
    for item in children:
        node = _make_node(item, parent, where)
        if node.name in parent.children:
            raise VfsError(f"{where}: повторяющееся имя '{node.name}'")
        parent.children[node.name] = node


def _make_node(item, parent, where):
    """Создаёт узел по описанию item (объекту JSON)."""
    if not isinstance(item, dict):
        raise VfsError(f"{where}: элемент каталога должен быть объектом")
    name = item.get("name")
    if not isinstance(name, str) or name in SPECIAL_NAMES \
            or SEPARATOR in name:
        raise VfsError(f"{where}: недопустимое имя {name!r}")
    kind = item.get("type")
    if kind == TYPE_DIR:
        node = Node(name, True, parent)
        _add_children(node, item, _join(where, name))
        return node
    if kind == TYPE_FILE:
        return Node(name, False, parent, _decode_content(item, name))
    raise VfsError(f"{_join(where, name)}: неизвестный тип {kind!r}")


def _join(where, name):
    """Путь к элементу name внутри каталога where (для сообщений)."""
    return where.rstrip(SEPARATOR) + SEPARATOR + name


def _decode_content(item, name):
    """Возвращает содержимое файла в виде байтов."""
    content = item.get("content", "")
    encoding = item.get("encoding", "text")
    if not isinstance(content, str) or encoding not in ENCODINGS:
        raise VfsError(f"{name}: неверное содержимое или кодировка")
    if encoding == "text":
        return content.encode("utf-8")
    try:
        return base64.b64decode(content, validate=True)
    except (binascii.Error, ValueError) as error:
        raise VfsError(f"{name}: неверные данные base64") from error
