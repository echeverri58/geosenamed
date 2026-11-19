@echo off
rem ===========================================================================
rem  PUBLICAR EN GITHUB - Datos Sensibles Georreferenciados - SENA
rem  Creado por el instructor John Alexander Echeverry Ocampo
rem
rem  Este archivo solo llama a publicar_github.py de forma comoda.
rem  Se puede ejecutar con doble clic o desde la consola:
rem      "PUBLICAR EN GITHUB.bat" --watch
rem      "PUBLICAR EN GITHUB.bat" --repo mi-repositorio --pages
rem  Para automatizar sin pausa final: definir la variable SIN_PAUSA=1
rem ===========================================================================
setlocal EnableExtensions
chcp 65001 >nul 2>nul
cd /d "%~dp0"

title Publicar en GitHub - Datos Sensibles Georreferenciados (SENA)

rem --- Comprobar que el script de Python esta al lado -----------------------
if not exist "%~dp0publicar_github.py" goto error_archivo

rem --- Buscar Python (py -3, python o python3) ------------------------------
set "PY="
py -3 -c "import sys" >nul 2>nul
if not errorlevel 1 set "PY=py -3"
if not defined PY (
  python -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PY=python"
)
if not defined PY (
  python3 -c "import sys" >nul 2>nul
  if not errorlevel 1 set "PY=python3"
)
if not defined PY goto error_python

rem --- Si vienen argumentos, se pasan directo al script ---------------------
if not "%~1"=="" (
  set "ARGS=%*"
  goto ejecutar
)

rem --- Menu -----------------------------------------------------------------
:menu
cls
echo ============================================================
echo   PUBLICAR EN GITHUB
echo   Datos Sensibles Georreferenciados - SENA
echo   Instructor John Alexander Echeverry Ocampo
echo ============================================================
echo.
echo   Que quieres hacer?
echo.
echo     [1] Subir todo a GitHub              (usa la sesion guardada, sin token)
echo     [2] Subir con un token               (si la sesion no funciona)
echo     [3] Subir y vigilar cambios          (con token, resube si algo cambia)
echo     [4] Solo preparar el repositorio local (sin subir)
echo     [5] Ver opciones avanzadas
echo     [0] Salir
echo.
echo   Archivos y carpetas de esta publicacion:
call :contar
echo.
set "OPCION="
set /p "OPCION=  Opcion [1]: "
if not defined OPCION set "OPCION=1"
if "%OPCION%"=="1" goto opcion_1
if "%OPCION%"=="2" goto opcion_2
if "%OPCION%"=="3" goto opcion_3
if "%OPCION%"=="4" goto opcion_4
if "%OPCION%"=="5" goto ayuda
if "%OPCION%"=="0" goto salir_menu
echo.
echo   Opcion no valida. Intenta de nuevo.
timeout /t 2 >nul 2>nul
goto menu

:opcion_1
set "ARGS=--sin-token"
goto ejecutar

:opcion_2
set "ARGS="
goto ejecutar

:opcion_3
set "ARGS=--watch"
goto ejecutar

:opcion_4
set "ARGS=--local"
goto ejecutar

:salir_menu
set "CODIGO=0"
goto fin

rem --- Ayuda ----------------------------------------------------------------
:ayuda
cls
echo ============================================================
echo   OPCIONES AVANZADAS
echo ============================================================
echo.
echo   Se pueden combinar, por ejemplo:
echo      "PUBLICAR EN GITHUB.bat" --sin-token
echo      "PUBLICAR EN GITHUB.bat" --repo mi-app --private --pages
echo.
echo   --sin-token       sube con la sesion de GitHub guardada en Windows
echo                     (no pide token; el repositorio debe existir)
echo   --repo NOMBRE     nombre del repositorio o URL completa
echo   --private         repositorio privado (por defecto publico)
echo   --watch           queda vigilando y resube al detectar cambios
echo   --interval N      segundos entre revisiones en --watch (5)
echo   --pages           activa GitHub Pages para ver la app en linea
echo   --branch RAMA     rama a publicar (main)
echo   --local           solo repositorio local y commit, sin subir
echo   --dry-run         muestra que subiria, sin tocar nada
echo   --force           fuerza la subida si el remoto tiene otra historia
echo   --diagnostico     revisa el token y los permisos sin subir nada
echo.
echo   Token de GitHub: https://github.com/settings/tokens  (permiso "repo")
echo   Los archivos de mas de 50 MB no se suben (por ejemplo el .pbf).
echo.
pause
goto menu

rem --- Ejecucion ------------------------------------------------------------
:ejecutar
cls
echo ============================================================
echo   Publicando en GitHub...
echo ============================================================
echo.
%PY% "%~dp0publicar_github.py" %ARGS%
set "CODIGO=%ERRORLEVEL%"
echo.
if "%CODIGO%"=="0" (
  echo [OK] Proceso terminado correctamente.
) else (
  echo [AVISO] El proceso termino con codigo %CODIGO%.
  echo         Revisa los mensajes de arriba.
)
goto fin

rem --- Errores --------------------------------------------------------------
:error_archivo
echo.
echo [ERROR] No se encontro publicar_github.py en esta carpeta:
echo         %~dp0
echo.
echo Copia este .bat junto al archivo publicar_github.py.
set "CODIGO=1"
goto fin

:error_python
echo.
echo [ERROR] No se encontro Python en este equipo.
echo.
echo   1. Descargalo de https://www.python.org/downloads/windows/
echo   2. Al instalar, marca la casilla "Add python.exe to PATH".
echo   3. Vuelve a ejecutar este archivo.
set "CODIGO=1"
goto fin

rem --- Contador de archivos (solo informativo en el menu) -------------------
:contar
for /f %%A in ('dir /b /a-d ^| find /c /v ""') do echo     %%A archivo(s) en esta carpeta
for /f %%A in ('dir /b /ad ^| find /c /v ""') do echo     %%A subcarpeta(s)
exit /b 0

rem --- Salida ---------------------------------------------------------------
:fin
echo.
if not defined SIN_PAUSA pause
endlocal & exit /b %CODIGO%
