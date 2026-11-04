@echo off
setlocal
cd /d "%~dp0"
set "BOOK_LOOP_PY=%CD%\local\qwen_env\Scripts\python.exe"
if not exist "%BOOK_LOOP_PY%" (
  echo Missing local\qwen_env\Scripts\python.exe. Use the existing Qwen Python environment first.
  exit /b 1
)
"%BOOK_LOOP_PY%" -X utf8 run_qwen_book_loop.py run --output local\qwen_book_loop_v3\run1 --cycles 6 --hours 48 --resume
set "BOOK_LOOP_RESULT=%ERRORLEVEL%"
echo.
echo Report: local\qwen_book_loop_v3\run1\results.html
if not "%BOOK_LOOP_RESULT%"=="0" echo Run paused or failed. Preserve logs and checkpoints before changing the job.
pause
exit /b %BOOK_LOOP_RESULT%
