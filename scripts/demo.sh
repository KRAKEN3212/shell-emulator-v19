#!/bin/sh
# Этапы 4-5: запуск стартовых скриптов с командами над VFS.
# Каждый запуск открывает окно; закройте его, чтобы перейти к следующему.
cd "$(dirname "$0")/.." || exit 1
PY=${PYTHON:-python3}

for script in stage4_commands stage5_rmdir full_demo; do
    echo "== $script"
    $PY -m src.main --vfs examples/vfs/deep.json \
        --script "examples/scripts/$script.txt"
done
