"""Парсер командной строки эмулятора.

Разбивает строку на слова с учётом кавычек и экранирования,
раскрывает переменные окружения реальной ОС ($VAR и ${VAR})
и отбрасывает комментарии, начинающиеся с символа #.
"""

import os
import string

NAME_CHARS = string.ascii_letters + string.digits + "_"
DOUBLE_QUOTE_ESCAPABLE = '"\\$'
NOT_FOUND = -1


class ParseError(Exception):
    """Синтаксическая ошибка в командной строке."""


class Lexer:
    """Посимвольный разбор одной строки."""

    def __init__(self, line, env):
        """Запоминает строку и словарь переменных окружения."""
        self.line = line
        self.env = env
        self.pos = 0
        self.words = []
        self.word = []
        self.in_word = False

    def run(self):
        """Выполняет разбор и возвращает список слов."""
        while self.pos < len(self.line):
            char = self.line[self.pos]
            if char.isspace():
                self._finish_word()
                self.pos += 1
            elif char == "#" and not self.in_word:
                break
            else:
                self._read_part(char)
        self._finish_word()
        return self.words

    def _read_part(self, char):
        """Разбирает фрагмент слова, начинающийся с символа char."""
        if char == "$":
            self._variable()
            self.in_word = self.in_word or any(self.word)
            return
        self.in_word = True
        if char == "'":
            self._single_quoted()
        elif char == '"':
            self._double_quoted()
        elif char == "\\":
            self._escaped()
        else:
            self.word.append(char)
            self.pos += 1

    def _finish_word(self):
        """Завершает текущее слово и добавляет его в результат."""
        if self.in_word:
            self.words.append("".join(self.word))
        self.word = []
        self.in_word = False

    def _single_quoted(self):
        """Строка в одинарных кавычках: всё берётся буквально."""
        end = self.line.find("'", self.pos + 1)
        if end == NOT_FOUND:
            raise ParseError("unexpected EOF while looking for matching `''")
        self.word.append(self.line[self.pos + 1:end])
        self.pos = end + 1

    def _double_quoted(self):
        """Строка в двойных кавычках: раскрываются переменные."""
        self.pos += 1
        while self.pos < len(self.line):
            char = self.line[self.pos]
            if char == '"':
                self.pos += 1
                return
            if char == "$":
                self._variable()
            elif char == "\\" and self._next_in(DOUBLE_QUOTE_ESCAPABLE):
                self.word.append(self.line[self.pos + 1])
                self.pos += 2
            else:
                self.word.append(char)
                self.pos += 1
        raise ParseError('unexpected EOF while looking for matching `"\'')

    def _escaped(self):
        """Символ после обратной косой черты берётся буквально."""
        if self.pos + 1 >= len(self.line):
            raise ParseError("unexpected end of line after `\\'")
        self.word.append(self.line[self.pos + 1])
        self.pos += 2

    def _next_in(self, chars):
        """Проверяет, что следующий символ входит в набор chars."""
        nxt = self.pos + 1
        return nxt < len(self.line) and self.line[nxt] in chars

    def _variable(self):
        """Раскрывает переменную окружения $NAME или ${NAME}."""
        if self._next_in("{"):
            end = self.line.find("}", self.pos + 2)
            name = self.line[self.pos + 2:end] if end != NOT_FOUND else ""
            if end == NOT_FOUND or not _is_name(name):
                raise ParseError("bad substitution")
            self.pos = end + 1
        else:
            end = self.pos + 1
            while end < len(self.line) and self.line[end] in NAME_CHARS:
                end += 1
            name = self.line[self.pos + 1:end]
            self.pos = end
            if not name:
                self.word.append("$")
                return
        self.word.append(self.env.get(name, ""))


def _is_name(name):
    """Проверяет, что name — допустимое имя переменной."""
    return bool(name) and all(char in NAME_CHARS for char in name)


def parse(line, env=None):
    """Разбирает строку line в список слов (имя команды и аргументы).

    Неизвестные переменные раскрываются в пустую строку, как в bash.
    При синтаксической ошибке возбуждается ParseError.
    """
    return Lexer(line, os.environ if env is None else env).run()
