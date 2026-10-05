#!/bin/sh
# Запуск эмулятора: ./run.sh [параметры]
cd "$(dirname "$0")" || exit 1
exec python3 -m src.main "$@"
