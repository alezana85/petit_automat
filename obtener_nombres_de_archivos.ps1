$folder = Get-Location
$contenido = Get-ChildItem $folder | Select-Object Name

# Guardar el contenido en un archivo CSV en la carpeta actual
$csvPath = Join-Path $folder "Contenido_directorio.csv"
$contenido | Export-Csv -NoTypeInformation -Encoding UTF8 $csvPath

Write-Host "Listado guardado en $csvPath"