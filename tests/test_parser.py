"""Тесты парсера командной строки."""

import unittest

from src.parser import ParseError, parse

ENV = {"HOME": "/home/artyom", "USER": "artyom", "EMPTY": ""}


class ParserTest(unittest.TestCase):
    """Разбор слов, кавычек, переменных и комментариев."""

    def test_simple_words(self):
        """Слова разделяются пробелами."""
        self.assertEqual(parse("ls  -a   /home", ENV), ["ls", "-a", "/home"])

    def test_empty_line(self):
        """Пустая строка даёт пустой список."""
        self.assertEqual(parse("   ", ENV), [])

    def test_variable_expansion(self):
        """Раскрываются $VAR и ${VAR}."""
        self.assertEqual(parse("cd $HOME", ENV), ["cd", "/home/artyom"])
        self.assertEqual(parse("ls ${USER}_dir", ENV), ["ls", "artyom_dir"])

    def test_unknown_variable(self):
        """Неизвестная переменная без кавычек пропадает, как в bash."""
        self.assertEqual(parse("ls $NOPE x", ENV), ["ls", "x"])
        self.assertEqual(parse('ls "$NOPE"', ENV), ["ls", ""])

    def test_lone_dollar(self):
        """Одиночный $ остаётся как есть."""
        self.assertEqual(parse("ls $ a$", ENV), ["ls", "$", "a$"])

    def test_quotes(self):
        """Одинарные кавычки не раскрывают переменные, двойные — да."""
        self.assertEqual(parse("ls '$HOME'", ENV), ["ls", "$HOME"])
        self.assertEqual(parse('ls "$HOME/a b"', ENV),
                         ["ls", "/home/artyom/a b"])

    def test_escape(self):
        """Обратная косая черта экранирует символ."""
        self.assertEqual(parse(r"ls a\ b \$HOME", ENV),
                         ["ls", "a b", "$HOME"])

    def test_comment(self):
        """Всё после # в начале слова — комментарий."""
        self.assertEqual(parse("ls a # comment", ENV), ["ls", "a"])
        self.assertEqual(parse("# only comment", ENV), [])
        self.assertEqual(parse("ls a#b", ENV), ["ls", "a#b"])

    def test_errors(self):
        """Незакрытые кавычки и неверная подстановка — ошибки."""
        for line in ("ls 'abc", 'ls "abc', "ls ${HOME", "ls ${}", "ls \\"):
            with self.subTest(line=line):
                with self.assertRaises(ParseError):
                    parse(line, ENV)


if __name__ == "__main__":
    unittest.main()
