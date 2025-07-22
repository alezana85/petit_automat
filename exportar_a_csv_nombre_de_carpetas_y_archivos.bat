@echo off
setlocal enabledelayedexpansion

rem Nombre del archivo de salida
set "csv=Contenido_directorio.csv"

rem Escribir encabezado
echo Nombre > "%csv%"

rem Listar archivos y carpetas en el directorio actual
for %%F in (*) do echo %%F >> "%csv%"
for /d %%D in (*) do echo %%D >> "%csv%"

echo Listado guardado en %csv%
pause