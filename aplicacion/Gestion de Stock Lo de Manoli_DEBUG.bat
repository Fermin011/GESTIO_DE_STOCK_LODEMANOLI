@echo on
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

set "APPDIR=%~dp0"
set "VENV=%APPDIR%venv"
set "PY=%VENV%\Scripts\python.exe"

if not exist "%PY%" (
  echo ERROR: Falta %PY%
  pause
  exit /b 1
)

for /f %%I in ('powershell -NoProfile -Command "(Resolve-Path -LiteralPath \"%APPDIR%..\").Path"') do set "ROOTDIR=%%I"
set "PYTHONPATH=%ROOTDIR%"

echo APPDIR=%APPDIR%
echo ROOTDIR=%ROOTDIR%
echo PYTHONPATH=%PYTHONPATH%

if not exist "%APPDIR%manoli.db" "%PY%" -c "from aplicacion.backend.database.database import crear_tablas; crear_tablas()"

"%PY%" -m aplicacion.main
echo ERRORLEVEL=%ERRORLEVEL%
pause
endlocal
