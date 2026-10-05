"""Команды эмулятора.

Каждая команда — функция вида handler(shell, args) -> str.
При ошибке команда возбуждает CommandError с текстом сообщения.
"""

MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды."""


def _stub(name, args):
    """Формирует вывод команды-заглушки: имя и аргументы."""
    shown = " ".join(repr(arg) for arg in args)
    return f"[stub] {name} {shown}".rstrip()


def cmd_ls(shell, args):
    """ls [путь...] — заглушка: выводит имя команды и аргументы."""
    return _stub("ls", args)


def cmd_cd(shell, args):
    """cd [путь] — заглушка: выводит имя команды и аргументы."""
    return _stub("cd", args)


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
    "vfs-info": cmd_vfs_info,
    "exit": cmd_exit,
}
