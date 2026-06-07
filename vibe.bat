@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
set "VIBE_DIR=%~dp0"
where py >nul 2>nul && (py "%VIBE_DIR%vibe.py" %* & goto :eof)
python "%VIBE_DIR%vibe.py" %*
