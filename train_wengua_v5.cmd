@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "PYTHONUNBUFFERED=1"
if not exist "local\qwen_env\Scripts\python.exe" (
  echo Missing local\qwen_env. Install requirements-qwen.txt in the existing Python 3.12 environment.
  pause
  exit /b 2
)
local\qwen_env\Scripts\python.exe -X utf8 run_course_v5.py run --resume %*
set "QIMEN_EXIT=%ERRORLEVEL%"
echo Report: local\course_v5\run1\results.html
if not "%QIMEN_EXIT%"=="0" echo Stopped. Outputs preserved. Review the error before repeating this command to resume.
pause
exit /b %QIMEN_EXIT%
