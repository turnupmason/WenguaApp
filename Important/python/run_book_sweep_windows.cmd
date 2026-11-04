@echo off
setlocal
cd /d "%~dp0"
set "BOOK_SWEEP_PY=%CD%\local\qwen_env\Scripts\python.exe"
if not exist "%BOOK_SWEEP_PY%" (
  echo Missing local\qwen_env\Scripts\python.exe. Use the existing Qwen Python environment first.
  exit /b 1
)
"%BOOK_SWEEP_PY%" -X utf8 run_qwen_book_sweep.py run --output local\qwen_book_sweep_v1\run1 --hours 168 --resume
set "BOOK_SWEEP_RESULT=%ERRORLEVEL%"
echo.
echo Report: local\qwen_book_sweep_v1\run1\results.html
if not "%BOOK_SWEEP_RESULT%"=="0" echo Interrupted or failed. Preserve logs and checkpoints; rerun this command to resume.
pause
exit /b %BOOK_SWEEP_RESULT%
