@echo off
REM Build installer using Inno Setup (ISCC) or NSIS (makensis)
REM Usage: run from project root after generating dist\FISCSOFT

if not exist dist\FISCSOFT (
  echo Directory dist\FISCSOFT not found. Execute build_exe.bat first to create the app bundle.
  pause
  exit /b 1
)

REM Try Inno Setup first
where ISCC >nul 2>nul
if %ERRORLEVEL%==0 (
  echo Found Inno Setup Compiler (ISCC). Building installer with installer.iss
  ISCC installer.iss
  echo Inno Setup build finished.
  pause
  exit /b 0
)

REM Fallback to NSIS
where makensis >nul 2>nul
if %ERRORLEVEL%==0 (
  echo Found NSIS (makensis). Building installer with installer_nsi.nsi
  makensis installer_nsi.nsi
  echo NSIS build finished.
  pause
  exit /b 0
)

echo Neither ISCC (Inno Setup) nor makensis (NSIS) were found in PATH.
echo Install Inno Setup (https://jrsoftware.org/isinfo.php) or NSIS (https://nsis.sourceforge.io/) and re-run this script.
pause
