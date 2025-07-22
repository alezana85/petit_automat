@echo off
setlocal

rem Lista de nombres de carpetas a crear
set "meses=01_Enero|02_Febrero|03_Marzo|04_Abril|05_Mayo|06_Junio|07_Julio|08_Agosto|09_Septiembre|10_Octubre|11_Noviembre|12_Diciembre"

rem Recorre solo las subcarpetas de primer nivel
for /d %%D in (*) do (
    if exist "%%D\" (
        for %%M in (%meses:|= %) do (
            md "%%D\%%M" 2>nul
        )
    )
)

echo Carpetas de meses creadas en subcarpetas de primer nivel.
pause