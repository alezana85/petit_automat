@echo off
setlocal enabledelayedexpansion

:: Obtener la ruta de la carpeta donde está el archivo .bat
set "carpeta_actual=%~dp0"

:: Itera sobre todos los archivos .zip en la carpeta actual
for %%F in ("%carpeta_actual%*.zip") do (
    :: Obtiene el nombre del archivo .zip sin la extensión
    set "nombre_archivo=%%~nF"
    
    :: Crear una carpeta temporal para descomprimir el archivo
    set "temp_folder=%carpeta_actual%temp_%%~nF"
    if not exist "!temp_folder!" mkdir "!temp_folder!"
    
    :: Descomprimir el archivo .zip en la carpeta temporal
    echo Descomprimiendo %%F...
    "C:\Program Files\7-Zip\7z.exe" x "%%F" -o"!temp_folder!" -y
    
    :: Buscar el archivo .xls en la carpeta temporal
    for %%A in ("!temp_folder!\*.xls") do (
        if exist "%%A" (
            :: Mover y renombrar el archivo .xls a la carpeta principal
            move /Y "%%A" "%carpeta_actual%!nombre_archivo!.xls"
        )
    )
    
    :: Eliminar la carpeta temporal después de procesar
    rd /S /Q "!temp_folder!"
)

echo Proceso completado.
pause