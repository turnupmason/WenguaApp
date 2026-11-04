@echo off
setlocal
cd /d "%~dp0"
set "BOOK_RESEARCH_PY=%CD%\local\qwen_env\Scripts\python.exe"
if not exist "%BOOK_RESEARCH_PY%" (
  echo Missing local\qwen_env\Scripts\python.exe. Use the existing Qwen environment first.
  exit /b 1
)
"%BOOK_RESEARCH_PY%" -X utf8 run_qwen_book_sweep_v2.py run --output local\qwen_book_sweep_v2\run1 --hours 168 --resume
set "BOOK_RESEARCH_RESULT=%ERRORLEVEL%"
echo.
echo Report: local\qwen_book_sweep_v2\run1\results.html
if not "%BOOK_RESEARCH_RESULT%"=="0" echo Interrupted or failed. Preserve the output and repeat this command to resume.
pause
exit /b %BOOK_RESEARCH_RESULT%
