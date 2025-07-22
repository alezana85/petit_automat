Get-ChildItem -Filter *.SUA | ForEach-Object {
    $original = $_.FullName
    $txt = $_.BaseName + ".txt"
    Rename-Item $original $txt
    $contenido = Get-Content $txt -Raw -Encoding Default
    if ($contenido.Length -lt 39) {
        Write-Host "Archivo $txt demasiado corto para renombrar correctamente."
        Rename-Item $txt $_.Name
        return
    }
    $parte1 = $contenido.Substring(14,12)
    $parte2 = $contenido.Substring(2,11)
    $parte3 = $contenido.Substring(30,2)
    $parte4 = $contenido.Substring(26,4)
    $parte5 = $contenido.Substring(32,6)
    $nuevo = "$parte1 $parte2 $parte3-$parte4 FOLIO $parte5.SUA"
    $nuevo = $nuevo -replace "`r|`n",''
    Rename-Item $txt $nuevo
    Write-Host "Renombrado: $($_.Name) -> $nuevo"
}