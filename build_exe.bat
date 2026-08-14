@echo off
REM Build FISCSOFT executable using PyInstaller (Windows)
REM Usage:
REM   1. Activate your virtualenv: .venv\Scripts\activate
REM   2. Install build deps: pip install -r requirements-exe.txt
REM   3. Run this script from the project root: build_exe.bat

set NAME=FISCSOFT
set ICONPATH=assets\imagens\logo_fiscsoft.ico

echo Installing PyInstaller (if missing)...
pip install -r requirements-exe.txt

echo Running PyInstaller (one-folder build)...
if exist "%ICONPATH%" (
  echo Using icon %ICONPATH%
  pyinstaller --noconfirm --onedir --windowed --name %NAME% --icon "%ICONPATH%" \
    --add-data "data;data" \
    --add-data "assets;assets" \
    --add-data "config;config" \
    --add-data "database;database" \
    --add-data "screens;screens" \
    main.py
) else (
  pyinstaller --noconfirm --onedir --windowed --name %NAME% \
    --add-data "data;data" \
    --add-data "assets;assets" \
    --add-data "config;config" \
    --add-data "database;database" \
    --add-data "screens;screens" \
    main.py
)

echo Build finished. See the "dist\%NAME%" folder for the executable.

if exist "%ICONPATH%" (
  if exist "dist\%NAME%" (
    copy "%ICONPATH%" "dist\%NAME%\logo_fiscsoft.ico" >nul
    echo Copied icon to dist\%NAME%\logo_fiscsoft.ico
  )
)

pause
