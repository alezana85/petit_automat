import asyncio
from playwright.async_api import async_playwright, Playwright
import os
import time
from datetime import datetime
import csv

async def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(
        headless=False,
        args=[
            "--force-device-scale-factor=0.5",
            "--window-size=1920,1080"
        ]
    )
    context = await browser.new_context(ignore_https_errors=True)
    page = await context.new_page()

    # Leer registros patronales desde el CSV
    registros = []
    resultados = []
    csv_path = 'C:/Users/a0l0uxs/Documents/03 AUTOMATIZACION/Descarga de Emisiones (webscrap)/rp_con_emision.csv'
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            registro = row.get("Registro Patronal")
            if registro:
                registros.append(registro.strip())

    for registro in registros:
        estatus = ""
        archivos_descargados = 0
        try:
            await page.goto("http://idse.imss.gob.mx/imss/")
            await page.wait_for_load_state("networkidle")
            # Si aparece el modal, cerrarlo antes de continuar (puede aparecer en cualquier momento antes del login)
            try:
                await page.click('xpath=//*[@id="myModal"]/div/div/div[3]/button', timeout=2000)
                await asyncio.sleep(1)
            except Exception:
                pass  # Si no aparece el modal, continuar normalmente
            await page.set_input_files('xpath=//*[@id="certificado"]', 'C:/Users/a0l0uxs/Downloads/FIEL_BIAA9001171B1_20230808171424/FIEL_BIAA9001171B1_20230808171424/biaa9001171b1.cer')
            await asyncio.sleep(2)
            await page.set_input_files('xpath=//*[@id="llave"]', 'C:/Users/a0l0uxs/Downloads/FIEL_BIAA9001171B1_20230808171424/FIEL_BIAA9001171B1_20230808171424/Claveprivada_FIEL_BIAA9001171B1_20230808_171424.key')
            await page.fill('xpath=//*[@id="idUsuario"]', "BIAA9001171B1")
            await page.fill('xpath=//*[@id="password"]', "IVANNA06")
            await page.click('xpath=//*[@id="botonFirma"]')
            await page.wait_for_load_state("networkidle")
            await page.click('xpath=/html/body/main/div[1]/section[1]/div[3]/div[2]/h3/a')
            await page.click('xpath=/html/body/main/div/form/div[3]/div[1]/div[1]/div/button')
            await page.fill('xpath=/html/body/main/div/form/div[3]/div[1]/div[1]/div/div/div[1]/input', registro)
            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")
            # Comprobar si el registro patronal existe en la web
            # Por ejemplo, si no aparece el botón de búsqueda o algún elemento clave
            try:
                await page.click('xpath=/html/body/main/div/form/div[9]/div/button', timeout=5000)
            except Exception:
                estatus = "Registro Patronal no encontrado"
                resultados.append({"Registro Patronal": registro, "Estatus": estatus})
                continue
            await page.wait_for_load_state("networkidle")
            await page.click('xpath=//*[@id="EnviaParam"]/div[9]/div/button[2]')
            
            iniciar_buttons = await page.query_selector_all('button:has-text("Iniciar descarga")')
            if iniciar_buttons:
                for btn in iniciar_buttons:
                    await btn.click()
                    await asyncio.sleep(2)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(3)

            # Siempre buscar y descargar archivos después de "Iniciar descarga"
            download_buttons = await page.query_selector_all('//button[contains(text(), "Descargar archivo")]')
            for btn in download_buttons:
                async with page.expect_download() as download_info:
                    await btn.click()
                download = await download_info.value
                suggested_name = download.suggested_filename
                save_path = f"C:/Users/a0l0uxs/Downloads/01 EMIOSNES DIRECTAS DE IDSE/{suggested_name}"
                await download.save_as(save_path)
                timeout = 30
                start_time = time.time()
                while not os.path.exists(save_path):
                    await asyncio.sleep(0.5)
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"El archivo {save_path} no se descargó en el tiempo esperado.")
                print(f"Archivo descargado: {suggested_name}")
                archivos_descargados += 1
                await asyncio.sleep(1)
            
            # Buscar también los enlaces de descarga, independientemente de si se encontraron botones
            download_links = await page.query_selector_all('//a[contains(text(), "Descargar archivo")]')
            for link in download_links:
                async with page.expect_download() as download_info:
                    await link.click()
                download = await download_info.value
                suggested_name = download.suggested_filename
                save_path = f"C:/Users/a0l0uxs/Downloads/Temp/Nueva carpeta/{suggested_name}"
                await download.save_as(save_path)
                timeout = 30
                start_time = time.time()
                while not os.path.exists(save_path):
                    await asyncio.sleep(0.5)
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"El archivo {save_path} no se descargó en el tiempo esperado.")
                print(f"Archivo descargado: {suggested_name}")
                archivos_descargados += 1
                await asyncio.sleep(1)

            if archivos_descargados > 0:
                estatus = f"{archivos_descargados} Archivos Descargados"
            else:
                estatus = "Sin archivos para descargar"
        except Exception as e:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_path = f"C:/Users/a0l0uxs/Downloads/Temp/ERROR_{registro}_{timestamp}.png"
            try:
                await page.screenshot(path=error_path)
                print(f"Error en registro {registro}: {e}. Captura de pantalla guardada en {error_path}")
            except Exception as screenshot_error:
                print(f"No se pudo guardar la captura de pantalla de error: {screenshot_error}")
            estatus = "Error al Descargar Archivos"
        resultados.append({"Registro Patronal": registro, "Estatus": estatus})

    await browser.close()

    # Escribir resultados en un nuevo CSV con columna Estatus
    output_path = 'C:/Users/a0l0uxs/Documents/03 AUTOMATIZACION/Descarga de Emisiones (webscrap)/rp_con_emision_resultado.csv'
    with open(csv_path, newline='', encoding='utf-8') as infile, open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Estatus"] if "Estatus" not in reader.fieldnames else reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            registro = row.get("Registro Patronal", "").strip()
            estatus_row = next((r["Estatus"] for r in resultados if r["Registro Patronal"] == registro), "")
            row["Estatus"] = estatus_row
            writer.writerow(row)

async def main():
    async with async_playwright() as playwright:
        await run(playwright)
asyncio.run(main())