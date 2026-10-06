"""Команды эмулятора.

Каждая команда — функция вида handler(shell, args) -> str.
При ошибке команда возбуждает CommandError. Если команда успела
что-то вывести до ошибки, этот вывод передаётся в CommandError.output.
"""

import fnmatch

from src.vfs import SEPARATOR, VfsError

MAX_EXIT_ARGS = 1
MAX_CD_ARGS = 1
MAX_PLAIN_LS_OPERANDS = 1
FIND_TYPES = {"f": False, "d": True}
END_OF_OPTIONS = "--"


class CommandError(Exception):
    """Ошибка выполнения команды (сообщения — по одному на строку)."""

    def __init__(self, message, output=""):
        """message — текст ошибки, output — вывод до ошибки."""
        super().__init__(message)
        self.output = output


class Report:
    """Накопитель вывода и ошибок команды."""

    def __init__(self):
        """Пустой отчёт."""
        self.lines = []
        self.errors = []

    def finish(self):
        """Возвращает вывод или возбуждает CommandError при ошибках."""
        output = "\n".join(self.lines)
        if self.errors:
            raise CommandError("\n".join(self.errors), output)
        return output


def split_options(args, allowed):
    """Отделяет короткие опции (-l, -la) от операндов.

    Возвращает множество опций и список операндов. Неизвестная
    опция вызывает CommandError.
    """
    options, operands = set(), []
    for index, arg in enumerate(args):
        if arg == END_OF_OPTIONS:
            return options, operands + args[index + 1:]
        if not arg.startswith("-") or arg == "-":
            operands.append(arg)
            continue
        for letter in arg[1:]:
            if letter not in allowed:
                raise CommandError(f"invalid option -- '{letter}'")
            options.add(letter)
    return options, operands


def _format_entry(node, long_format, shown=None):
    """Строка вывода ls для узла; shown — отображаемое имя."""
    name = shown or node.name
    if not long_format:
        return name
    kind = "d" if node.is_dir else "-"
    size = len(node.children) if node.is_dir else len(node.content)
    return f"{kind} {size:>8} {name}"


def _resolve_all(vfs, paths, report):
    """Находит узлы для путей; ошибки добавляет в report."""
    targets = []
    for path in paths:
        try:
            targets.append((path, vfs.resolve(path)))
        except VfsError as error:
            report.errors.append(f"cannot access '{path}': {error}")
    return targets


def cmd_ls(shell, args):
    """ls [-l] [путь...] — список содержимого каталогов VFS.

    Как в UNIX, сначала выводятся файлы-операнды, затем содержимое
    каталогов; при нескольких операндах у каталогов есть заголовки.
    """
    options, paths = split_options(args, "l")
    long_format = "l" in options
    report = Report()
    targets = _resolve_all(shell.vfs, paths or ["."], report)
    for path, node in targets:
        if not node.is_dir:
            report.lines.append(_format_entry(node, long_format, path))
    show_headers = len(paths) > MAX_PLAIN_LS_OPERANDS
    for path, node in targets:
        if not node.is_dir:
            continue
        if report.lines:
            report.lines.append("")
        if show_headers:
            report.lines.append(f"{path}:")
        report.lines.extend(_format_entry(child, long_format)
                            for child in node.sorted_children())
    return report.finish()


def cmd_cd(shell, args):
    """cd [путь | -] — смена текущего каталога VFS.

    Без аргументов переходит в корень VFS, «cd -» — в предыдущий
    каталог.
    """
    if len(args) > MAX_CD_ARGS:
        raise CommandError("too many arguments")
    vfs = shell.vfs
    path = args[0] if args else SEPARATOR
    if path == "-":
        vfs.cwd, vfs.previous = vfs.previous, vfs.cwd
        return vfs.cwd.path()
    try:
        node = vfs.resolve(path)
    except VfsError as error:
        raise CommandError(f"{path}: {error}") from error
    if not node.is_dir:
        raise CommandError(f"{path}: Not a directory")
    vfs.previous, vfs.cwd = vfs.cwd, node
    return ""


def _parse_find_args(args):
    """Разбирает аргументы find: пути, шаблон -name и тип -type."""
    first_option = next((index for index, arg in enumerate(args)
                         if arg.startswith("-")), len(args))
    paths = args[:first_option]
    rest = args[first_option:]
    filters = {"name": None, "type": None}
    while rest:
        key, rest = rest[0], rest[1:]
        if key not in ("-name", "-type"):
            raise CommandError(f"unknown predicate `{key}'")
        if not rest:
            raise CommandError(f"missing argument to `{key}'")
        value, rest = rest[0], rest[1:]
        if key == "-type" and value not in FIND_TYPES:
            raise CommandError(f"Unknown argument to -type: {value}")
        filters[key[1:]] = value
    return paths or ["."], filters


def _find_matches(node, filters):
    """Проверяет узел на соответствие фильтрам find."""
    if filters["type"] and node.is_dir != FIND_TYPES[filters["type"]]:
        return False
    pattern = filters["name"]
    return pattern is None or fnmatch.fnmatchcase(node.name, pattern)


def _find_walk(node, shown, filters, lines):
    """Рекурсивно обходит каталог, собирая подходящие пути."""
    if _find_matches(node, filters):
        lines.append(shown)
    prefix = shown.rstrip(SEPARATOR) + SEPARATOR
    for child in node.sorted_children():
        _find_walk(child, prefix + child.name, filters, lines)


def cmd_find(shell, args):
    """find [путь...] [-name ШАБЛОН] [-type f|d] — поиск в VFS."""
    paths, filters = _parse_find_args(args)
    report = Report()
    for path in paths:
        try:
            node = shell.vfs.resolve(path)
        except VfsError as error:
            report.errors.append(f"'{path}': {error}")
            continue
        _find_walk(node, path, filters, report.lines)
    return report.finish()


def cmd_rev(shell, args):
    """rev ФАЙЛ... — выводит строки файлов с символами в обратном порядке."""
    _, paths = split_options(args, "")
    if not paths:
        raise CommandError("missing file operand")
    report = Report()
    for path in paths:
        try:
            node = shell.vfs.resolve(path)
        except VfsError as error:
            report.errors.append(f"cannot open {path}: {error}")
            continue
        if node.is_dir:
            report.errors.append(f"{path}: Is a directory")
            continue
        text = node.content.decode("utf-8", errors="replace")
        report.lines.extend(line[::-1] for line in text.splitlines())
    return report.finish()


def _is_busy(vfs, node):
    """True для корня и для каталогов на пути к текущему каталогу."""
    current = vfs.cwd
    while current is not None:
        if current is node:
            return True
        current = current.parent
    return False


def _remove_dir(vfs, path):
    """Удаляет пустой каталог path из VFS (только в памяти)."""
    last = path.rstrip(SEPARATOR).rsplit(SEPARATOR, 1)[-1]
    if last in (".", ".."):
        raise VfsError("Invalid argument")
    node = vfs.resolve(path)
    if not node.is_dir:
        raise VfsError("Not a directory")
    if _is_busy(vfs, node):
        raise VfsError("Device or resource busy")
    if node.children:
        raise VfsError("Directory not empty")
    del node.parent.children[node.name]


def _parent_paths(path):
    """Путь и все его родители по записи: a/b/c -> a/b/c, a/b, a."""
    parts = [part for part in path.split(SEPARATOR) if part]
    prefix = SEPARATOR if path.startswith(SEPARATOR) else ""
    return [prefix + SEPARATOR.join(parts[:end])
            for end in range(len(parts), 0, -1)]


def cmd_rmdir(shell, args):
    """rmdir [-p] КАТАЛОГ... — удаляет пустые каталоги VFS.

    С опцией -p удаляются и родительские каталоги из пути.
    Изменения выполняются только в памяти.
    """
    options, paths = split_options(args, "p")
    if not paths:
        raise CommandError("missing operand")
    report = Report()
    for path in paths:
        chain = _parent_paths(path) if "p" in options else [path]
        for target in chain or [path]:
            try:
                _remove_dir(shell.vfs, target)
            except VfsError as error:
                report.errors.append(
                    f"failed to remove '{target}': {error}")
                break
    return report.finish()


def cmd_vfs_info(shell, args):
    """vfs-info — служебная команда: сведения о загруженной VFS."""
    if args:
        raise CommandError("too many arguments")
    dirs, files, size = shell.vfs.stats()
    source = shell.vfs.source or "<пустая VFS по умолчанию>"
    return "\n".join([
        f"source: {source}",
        f"dirs:   {dirs}",
        f"files:  {files}",
        f"bytes:  {size}",
    ])


def cmd_exit(shell, args):
    """exit [код] — завершает работу эмулятора."""
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("too many arguments")
    code = 0
    if args:
        try:
            code = int(args[0])
        except ValueError as error:
            raise CommandError(
                f"{args[0]}: numeric argument required") from error
    shell.running = False
    shell.exit_code = code
    return ""


REGISTRY = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "find": cmd_find,
    "rev": cmd_rev,
    "rmdir": cmd_rmdir,
    "vfs-info": cmd_vfs_info,
    "exit": cmd_exit,
}
