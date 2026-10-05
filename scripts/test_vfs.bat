@echo off
rem Этап 3: запуск эмулятора с разными вариантами VFS.
rem Каждый запуск открывает окно; закройте его, чтобы перейти к следующему.
cd /d "%~dp0\.."
set SCRIPT=examples\scripts\stage3_vfs.txt

for %%v in (minimal files deep) do (
    echo == VFS: %%v
    python -m src.main --vfs examples\vfs\%%v.json --script %SCRIPT%
)
for %%v in (no_such_file broken bad_structure bad_base64) do (
    echo == VFS с ошибкой: %%v
    python -m src.main --vfs examples\vfs\%%v.json --script %SCRIPT%
)
pause
