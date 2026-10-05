@echo off
rem Запуск эмулятора: run.bat [параметры]
cd /d "%~dp0"
python -m src.main %*
