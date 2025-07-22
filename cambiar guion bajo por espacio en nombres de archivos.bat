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

rem Procesar archivos en la carpeta actual y subcarpetas
for /R %%f in (*) do (
    rem Ignorar el propio archivo batch
    if not "%%~nxf" == "%~nx0" (
        set "rutacompleta=%%f"
        set "carpeta=%%~dpf"
        set "filename=%%~nxf"
        set "newname=!filename:_= !"
        
        if not "!filename!" == "!newname!" (
            pushd "!carpeta!"
            ren "!filename!" "!newname!"
            popd
            echo Renombrado: "!carpeta!!filename!" a "!carpeta!!newname!"
            set /a procesados+=1
        ) else (
            set /a sinCambios+=1
        )
    )
)

echo.
echo Proceso completado.
echo %procesados% archivos renombrados.
echo %sinCambios% archivos sin cambios.
echo.
pause