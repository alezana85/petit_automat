@echo off
setlocal enabledelayedexpansion

echo Convirtiendo nombres de archivos a mayusculas...
echo.

 Recorrer todos los archivos en el directorio actual y subdirectorios
for r %%f in () do (
    set archivo=%%~nxf
    set ruta=%%~dpf
    
     Convertir a mayúsculas
    for %%A in (a b c d e f g h i j k l m n o p q r s t u v w x y z) do (
        set archivo=!archivo%%A=%%A!
    )
    
     Reemplazar minúsculas por mayúsculas
    set archivo=!archivoa=A!
    set archivo=!archivob=B!
    set archivo=!archivoc=C!
    set archivo=!archivod=D!
    set archivo=!archivoe=E!
    set archivo=!archivof=F!
    set archivo=!archivog=G!
    set archivo=!archivoh=H!
    set archivo=!archivoi=I!
    set archivo=!archivoj=J!
    set archivo=!archivok=K!
    set archivo=!archivol=L!
    set archivo=!archivom=M!
    set archivo=!archivon=N!
    set archivo=!archivoo=O!
    set archivo=!archivop=P!
    set archivo=!archivoq=Q!
    set archivo=!archivor=R!
    set archivo=!archivos=S!
    set archivo=!archivot=T!
    set archivo=!archivou=U!
    set archivo=!archivov=V!
    set archivo=!archivow=W!
    set archivo=!archivox=X!
    set archivo=!archivoy=Y!
    set archivo=!archivoz=Z!
    
     Solo renombrar si el nombre es diferente
    if not %%~nxf==!archivo! (
        echo Renombrando %%~nxf a !archivo!
        ren %%f !archivo! 2nul
        if errorlevel 1 (
            echo Error al renombrar %%f
        )
    )
)

echo.
echo Proceso completado.
pause