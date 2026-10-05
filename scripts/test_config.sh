#!/bin/sh
# Этап 2: проверка всех параметров командной строки эмулятора.
# Каждый запуск открывает окно; закройте его, чтобы перейти к следующему.
cd "$(dirname "$0")/.." || exit 1
PY=${PYTHON:-python3}

echo "== 1. без параметров"
$PY -m src.main
echo "== 2. только путь к VFS"
$PY -m src.main --vfs examples/vfs/minimal.json
echo "== 3. только стартовый скрипт"
$PY -m src.main --script examples/scripts/stage2_config.txt
echo "== 4. оба параметра"
$PY -m src.main --vfs examples/vfs/deep.json \
    --script examples/scripts/stage1_repl.txt
echo "== 5. несуществующий скрипт (ошибка в окне)"
$PY -m src.main --script examples/scripts/no_such_script.txt
echo "== 6. неизвестный параметр (ошибка argparse)"
$PY -m src.main --unknown 2>&1
echo "== 7. справка"
$PY -m src.main --help
