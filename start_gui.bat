@echo off
setlocal

set "PYTHON=%~dp0runtime\python.exe"
if not exist "%PYTHON%" set "PYTHON=python"

"%PYTHON%" -c "import PIL" >nul 2>nul
if errorlevel 1 (
    echo Startup failed: Python or Pillow is not available.
    echo.
    echo Install Python 3, then run:
    echo python -m pip install Pillow
    echo.
    pause
    exit /b 1
)

start "IMGtoPDF" "%PYTHON%" "%~dp0main.py"
