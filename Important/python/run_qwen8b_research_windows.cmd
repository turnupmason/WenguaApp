@echo off
setlocal
cd /d "%~dp0"
set "QWEN8B_PY=%CD%\local\qwen_env\Scripts\python.exe"
if not exist "%QWEN8B_PY%" (
  echo Missing local\qwen_env\Scripts\python.exe. Reuse the existing Qwen environment.
  exit /b 1
)
"%QWEN8B_PY%" -X utf8 run_qwen8b_diagnostic.py run --output local\qwen8b_book_v1\run3_attention_fix --hours 168 --resume
set "QWEN8B_RESULT=%ERRORLEVEL%"
echo.
echo Report: local\qwen8b_book_v1\run3_attention_fix\results.html
if "%QWEN8B_RESULT%"=="3" echo Course quality review: training paused. Preserve all models and checkpoints. See docs\QWEN_BOOK_COURSE_REVIEW_20261105.md.
if not "%QWEN8B_RESULT%"=="0" if not "%QWEN8B_RESULT%"=="3" echo Stopped. Preserve the output and check the error before retrying.
pause
exit /b %QWEN8B_RESULT%
