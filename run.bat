@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHONPATH=%cd%
start pythonw jarvis\app_ultimate.py
exit
