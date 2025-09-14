@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM === Pararse en manoli\aplicacion ===
cd /d "%~dp0"

REM Rutas base
set "APPDIR=%~dp0"          REM ...\manoli\aplicacion\
set "ROOTDIR=%APPDIR%.."    REM ...\manoli\
set "VENV=%ROOTDIR%\venv"   REM venv en manoli\venv
set "PY=%VENV%\Scripts\python.exe"

REM Logs
set "LOG_DIR=%LocalAppData%\LoDeManoli\logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
for /f %%I in ('powershell -NoProfile -Command "(Get-Date).ToString('yyyyMMdd')"') do set DATESTR=%%I
set "APP_LOG=%LOG_DIR%\app-%DATESTR%.log"
set "LAUNCH_LOG=%LOG_DIR%\launcher.log"

REM Verificar venv
if not exist "%PY%" (
  echo [%date% %time%] ERROR: No se encontro el venv en "%VENV%" >> "%LAUNCH_LOG%"
  echo No se encontro el venv en "%VENV%".
  echo Crealo con:
  echo   py -3.13 -m venv "%VENV%" --copies
  echo   "%VENV%\Scripts\python" -m pip install --upgrade pip wheel setuptools
  echo   "%VENV%\Scripts\pip" install -r "%APPDIR%requirements.txt"
  pause
  exit /b 1
)

REM Hacer visible el paquete 'aplicacion' y forzar UTF-8 para evitar UnicodeEncodeError
set "PYTHONPATH=%ROOTDIR%"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

REM Crear DB si falta (con UTF-8 habilitado)
if not exist "%APPDIR%manoli.db" (
  "%PY%" -X utf8 -c "from aplicacion.backend.database.database import crear_tablas; crear_tablas()" 1>> "%LAUNCH_LOG%" 2>&1
)

REM Ejecutar la app como módulo, en UTF-8, y loguear salida
echo [INFO] Ejecutando: "%PY%" -X utf8 -m aplicacion.main >> "%LAUNCH_LOG%"
"%PY%" -X utf8 -m aplicacion.main 1>> "%APP_LOG%" 2>&1
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo [ERROR] La app salio con codigo %EXITCODE%. >> "%LAUNCH_LOG%"
  start notepad "%APP_LOG%"
  start notepad "%LAUNCH_LOG%"
  pause
  exit /b %EXITCODE%
)

endlocal

