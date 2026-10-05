#!/bin/sh
# Этап 3: запуск эмулятора с разными вариантами VFS.
# Каждый запуск открывает окно; закройте его, чтобы перейти к следующему.
cd "$(dirname "$0")/.." || exit 1
PY=${PYTHON:-python3}
SCRIPT=examples/scripts/stage3_vfs.txt

for vfs in minimal files deep; do
    echo "== VFS: $vfs"
    $PY -m src.main --vfs "examples/vfs/$vfs.json" --script "$SCRIPT"
done
for vfs in no_such_file broken bad_structure bad_base64; do
    echo "== VFS с ошибкой: $vfs"
    $PY -m src.main --vfs "examples/vfs/$vfs.json" --script "$SCRIPT"
done
