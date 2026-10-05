# Эмулятор командной оболочки ОС (вариант 19)

Графический эмулятор командной строки UNIX-подобной ОС на Python + Tkinter.
Работает с виртуальной файловой системой (VFS), загружаемой из JSON-файла;
все изменения VFS выполняются только в памяти.

## 1. Общее описание

- окно с заголовком `Эмулятор - [username@hostname]` — имя пользователя
  и хоста берутся из реальной ОС;
- приглашение `user@host:/текущий/каталог$`, история команд (стрелки ↑/↓);
- парсер командной строки: кавычки `'...'` и `"..."`, экранирование `\`,
  комментарии `#`, раскрытие переменных окружения ОС `$VAR` и `${VAR}`;
- стартовый скрипт: команды выполняются по очереди, на экране видны и
  ввод, и вывод; ошибка в одной команде не останавливает скрипт;
- ошибки выводятся красным в формате `команда: сообщение`.

Структура репозитория:

```
src/            исходный код
  main.py       точка входа, загрузка VFS, запуск окна
  app.py        GUI (Tkinter)
  shell.py      ядро: разбор строки и вызов команд (без GUI)
  parser.py     парсер командной строки
  commands.py   команды эмулятора
  vfs.py        виртуальная файловая система
  config.py     параметры командной строки
  script.py     чтение стартового скрипта
tests/          модульные тесты (unittest)
examples/vfs/   примеры VFS
examples/scripts/  стартовые скрипты эмулятора для этапов
scripts/        скрипты ОС для запуска эмулятора с разными параметрами
```

## 2. Функции и настройки

### Параметры командной строки

| Параметр        | Описание                                           |
|-----------------|----------------------------------------------------|
| `--vfs PATH`    | путь к JSON-файлу VFS (по умолчанию — пустая VFS)  |
| `--script PATH` | путь к стартовому скрипту эмулятора                |
| `--help`        | справка                                            |

При запуске выводятся отладочные значения всех параметров.

### Команды

| Команда | Описание |
|---------|----------|
| `ls [-l] [путь...]` | содержимое каталогов; `-l` — тип (`d`/`-`) и размер |
| `cd [путь \| -]` | смена каталога; без аргументов — корень, `-` — предыдущий |
| `find [путь...] [-name ШАБЛОН] [-type f\|d]` | рекурсивный поиск |
| `rev ФАЙЛ...` | строки файлов с символами в обратном порядке |
| `rmdir [-p] КАТАЛОГ...` | удаление пустых каталогов; `-p` — вместе с родителями |
| `vfs-info` | служебная: источник VFS, число каталогов и файлов |
| `exit [код]` | выход из эмулятора |

### Формат VFS

```json
{"type": "dir", "children": [
  {"name": "a.txt", "type": "file", "content": "текст"},
  {"name": "b.bin", "type": "file", "encoding": "base64", "content": "AAEC"},
  {"name": "docs",  "type": "dir",  "children": []}
]}
```

Двоичные данные хранятся в base64. Если файл VFS не найден, содержит
неверный JSON или неверную структуру (повтор имени, неизвестный тип,
битый base64), эмулятор сообщает об ошибке и работает с пустой VFS.

### Стартовый скрипт

Обычный текстовый файл, одна команда на строку. Строки, начинающиеся
с `#`, и пустые строки пропускаются; `#` в начале слова начинает
комментарий до конца строки.

## 3. Сборка и запуск

Нужен Python 3.8+ с Tkinter (в Windows входит в стандартный установщик,
в Ubuntu: `sudo apt install python3-tk`). Сторонних зависимостей нет.

```sh
./run.sh [--vfs PATH] [--script PATH]     # Linux / macOS
run.bat  [--vfs PATH] [--script PATH]     # Windows
```

Запуск тестов:

```sh
python -m unittest discover -s tests -t . -v
```

Скрипты ОС для проверки этапов (каждый открывает несколько окон подряд —
закрывайте окно, чтобы перейти к следующему запуску):

| Скрипт | Что проверяет |
|--------|---------------|
| `scripts/test_config.sh` / `.bat` | все параметры командной строки (этап 2) |
| `scripts/test_vfs.sh` / `.bat` | разные VFS и ошибки загрузки (этап 3) |
| `scripts/demo.sh` / `.bat` | команды над VFS (этапы 4–5) |

## 4. Примеры использования

```sh
./run.sh --vfs examples/vfs/deep.json --script examples/scripts/full_demo.txt
```

```
user@host:/$ ls -l
d        2 etc
d        2 home
d        1 tmp
d        1 var
user@host:/$ cd home/artyom
user@host:/home/artyom$ find . -type f
./hello.txt
./photo.png
./projects/shell/README.md
./projects/shell/main.py
user@host:/home/artyom$ rev hello.txt
dlrow olleh
stressed desserts
user@host:/home/artyom$ rmdir projects
rmdir: failed to remove 'projects': Directory not empty
user@host:/home/artyom$ cd $HOME
cd: /home/user: No such file or directory
user@host:/home/artyom$ ls "unclosed
emulator: syntax error: unexpected EOF while looking for matching `"'
```

Примечание для Windows: переменной `HOME` там обычно нет, используйте
`$USERPROFILE`, `$USERNAME`, `$COMPUTERNAME`.

Стартовые скрипты этапов: `examples/scripts/stage1_repl.txt`,
`stage2_config.txt`, `stage3_vfs.txt`, `stage4_commands.txt`,
`stage5_rmdir.txt`, `full_demo.txt`.
