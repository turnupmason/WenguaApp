@echo off
setlocal
cd /d "%~dp0"
set "QWEN8B_PY=%CD%\local\qwen_env\Scripts\python.exe"
if not exist "%QWEN8B_PY%" (
  echo Missing local\qwen_env\Scripts\python.exe. Reuse the existing Qwen environment.
  exit /b 1
)
"%QWEN8B_PY%" -X utf8 run_qwen8b_research.py run --output local\qwen8b_book_v1\run1 --hours 168 --resume
set "QWEN8B_RESULT=%ERRORLEVEL%"
echo.
echo Report: local\qwen8b_book_v1\run1\results.html
if not "%QWEN8B_RESULT%"=="0" echo Stopped. Preserve the output and repeat this command to resume after checking the error.
pause
exit /b %QWEN8B_RESULT%
