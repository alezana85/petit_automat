@echo off
setlocal enabledelayedexpansion
echo Iniciando reemplazo de guiones bajos por espacios en todas las carpetas y subcarpetas...
echo.

rem Trabajar en la carpeta donde está este script
cd /d "%~dp0"
echo Trabajando en: %CD% y todas sus subcarpetas
echo.

set "procesados=0"
set "sinCambios=0"

rem Procesar solo carpetas en la carpeta actual y subcarpetas (orden inverso para evitar problemas de rutas)
for /f "delims=" %%d in ('dir /ad /b /s ^| sort /R') do (
    set "carpeta=%%~nd"
    set "ruta=%%~dpd"
    set "nombreNuevo=!carpeta:_= !"
    if not "!carpeta!"=="!nombreNuevo!" (
        pushd "%%~dpd"
        ren "%%~nd" "!nombreNuevo!"
        popd
        echo Renombrado: "%%d" a "!ruta!!nombreNuevo!"
        set /a procesados+=1
    ) else (
        set /a sinCambios+=1
    )
)

echo.
echo Proceso completado.
echo %procesados% carpetas renombradas.
echo %sinCambios% carpetas sin cambios.
echo.
pause