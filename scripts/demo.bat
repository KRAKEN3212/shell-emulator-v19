@echo off
rem Этапы 4-5: запуск стартовых скриптов с командами над VFS.
rem Каждый запуск открывает окно; закройте его, чтобы перейти к следующему.
cd /d "%~dp0\.."

for %%s in (stage4_commands stage5_rmdir full_demo) do (
    echo == %%s
    python -m src.main --vfs examples\vfs\deep.json --script examples\scripts\%%s.txt
)
pause
