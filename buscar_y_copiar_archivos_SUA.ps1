# Obtener la ruta del script actual
$origen = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

# Obtener ruta del escritorio del usuario actual
$escritorio = [Environment]::GetFolderPath("Desktop")

# Definir carpeta de destino
$destino = Join-Path $escritorio "Archivos renombrados"

# Crear la carpeta de destino si no existe
if (-not (Test-Path -Path $destino)) {
    New-Item -ItemType Directory -Path $destino | Out-Null
}

# Buscar todos los archivos con extensión .SUA en subcarpetas
$archivos = Get-ChildItem -Path $origen -Filter *.SUA -Recurse

# Contador para renombrar
$contador = 1

foreach ($archivo in $archivos) {
    $nuevoNombre = "Archivo_$contador.sua"
    $rutaDestino = Join-Path $destino $nuevoNombre

    Copy-Item -Path $archivo.FullName -Destination $rutaDestino
    $contador++
}

Write-Output "Se copiaron y renombraron $($contador - 1) archivos a '$destino'."