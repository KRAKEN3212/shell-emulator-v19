@echo off
rem Этап 2: проверка всех параметров командной строки эмулятора.
rem Каждый запуск открывает окно; закройте его, чтобы перейти к следующему.
cd /d "%~dp0\.."

echo == 1. без параметров
python -m src.main
echo == 2. только путь к VFS
python -m src.main --vfs examples\vfs\minimal.json
echo == 3. только стартовый скрипт
python -m src.main --script examples\scripts\stage2_config.txt
echo == 4. оба параметра
python -m src.main --vfs examples\vfs\deep.json --script examples\scripts\stage1_repl.txt
echo == 5. несуществующий скрипт (ошибка в окне)
python -m src.main --script examples\scripts\no_such_script.txt
echo == 6. неизвестный параметр (ошибка argparse)
python -m src.main --unknown
echo == 7. справка
python -m src.main --help
pause
