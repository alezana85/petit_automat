import asyncio
from playwright.async_api import async_playwright, Playwright
import os
import time
from datetime import datetime
import csv
from pathlib import Path

async def monitor_and_close_modal(page, stop_monitoring):
    """Monitorea y cierra el modal de advertencia cuando aparece"""
    while not stop_monitoring.is_set():
        try:
            modal_button = await page.query_selector('xpath=//*[@id="myModal"]/div/div/div[3]/button')
            if modal_button:
                await modal_button.click()
                print("Modal de advertencia cerrado automáticamente")
                await asyncio.sleep(1)
        except Exception:
            pass
        await asyncio.sleep(0.5)  # Verificar cada 500ms

DOWNLOAD_DIR = r"F:\\01 TRABAJO\\WALMART\\02 IMSS\\02 EMISIONES"
CSV_PATH = 'templates/rp_con_emision.csv'
WORKERS = 4  # número de "navegadores" en paralelo
HEADLESS = os.getenv("HEADLESS", "1") == "1"


async def procesar_registro(page, registro: str) -> tuple[str, str]:
    """Procesa un registro patronal y devuelve (registro, estatus)."""
    estatus = ""
    archivos_descargados = 0
    try:
        await page.goto("http://idse.imss.gob.mx/imss/")
        await page.wait_for_load_state("networkidle")

        # Iniciar monitoreo del modal de advertencia
        stop_monitoring = asyncio.Event()
        modal_task = asyncio.create_task(monitor_and_close_modal(page, stop_monitoring))

        await page.set_input_files('xpath=//*[@id="certificado"]', 'F:/01 TRABAJO/WALMART/01 ACCESOS/FIEL RL/ALFONSO BRISEÑO/BIAA9001171B1.cer')
        await page.set_input_files('xpath=//*[@id="llave"]', 'F:/01 TRABAJO/WALMART/01 ACCESOS/FIEL RL/ALFONSO BRISEÑO/Claveprivada_FIEL_BIAA9001171B1_20230808_171424.key')
        await page.fill('xpath=//*[@id="idUsuario"]', "BIAA9001171B1")
        await page.fill('xpath=//*[@id="password"]', "IVANNA06")

        # Detener monitoreo antes del click en botonFirma
        stop_monitoring.set()
        modal_task.cancel()
        try:
            await modal_task
        except asyncio.CancelledError:
            pass

        await page.click('xpath=//*[@id="botonFirma"]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)
        await page.click('xpath=/html/body/main/div[1]/section[1]/div[3]/div[2]/h3/a')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)
        await page.click('xpath=/html/body/main/div/form/div[3]/div[1]/div[1]/div/button')
        await page.fill('xpath=/html/body/main/div/form/div[3]/div[1]/div[1]/div/div/div[1]/input', registro)
        await page.keyboard.press("Enter")
        await page.click('xpath=/html/body/main/div/form/div[9]/div/button')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)
        await page.click('xpath=//*[@id="EnviaParam"]/div[9]/div/button[2]')
        await page.wait_for_load_state("networkidle")
        await asyncio.sleep(5)

        iniciar_buttons = await page.query_selector_all('button:has-text("Iniciar descarga")')
        if iniciar_buttons:
            for btn in iniciar_buttons:
                await btn.click()
                await asyncio.sleep(2)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            print(f"Se procesaron {len(iniciar_buttons)} botones 'Iniciar descarga' para el registro {registro}")
        else:
            print(f"No se encontraron botones de 'Iniciar descarga' para el registro {registro}, buscando enlaces de descarga directamente")

        # Siempre buscar enlaces "Descargar archivo"
        download_buttons = await page.query_selector_all('//a[contains(text(), "Descargar archivo")] | //button[contains(text(), "Descargar archivo")]')

        if download_buttons:
            print(f"Se encontraron {len(download_buttons)} enlaces/botones 'Descargar archivo' para el registro {registro}")
            for btn in download_buttons:
                async with page.expect_download() as download_info:
                    await btn.click()
                download = await download_info.value
                suggested_name = download.suggested_filename
                filename = suggested_name  # Usar el nombre sugerido por defecto
                save_path = str(Path(DOWNLOAD_DIR) / filename)

                await download.save_as(save_path)
                timeout = 30
                start_time = time.time()
                while not os.path.exists(save_path):
                    await asyncio.sleep(0.5)
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"El archivo {save_path} no se descargó en el tiempo esperado.")
                print(f"Archivo descargado: {filename}")
                archivos_descargados += 1
                await asyncio.sleep(1)
        else:
            print(f"No se encontraron enlaces/botones 'Descargar archivo' para el registro {registro}")

        if archivos_descargados > 0:
            estatus = f"{archivos_descargados} Archivos Descargados"
        else:
            estatus = "Sin archivos para descargar"
    except Exception as e:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_path = str(Path(DOWNLOAD_DIR) / f"ERROR_{registro}_{timestamp}.png")
        try:
            await page.screenshot(path=error_path)
            print(f"Error en registro {registro}: {e}. Captura de pantalla guardada en {error_path}")
        except Exception as screenshot_error:
            print(f"No se pudo guardar la captura de pantalla de error: {screenshot_error}")
        estatus = "Error al Descargar Archivos"
    return registro, estatus


async def worker(browser, queue: asyncio.Queue, resultados: list):
    # Cada worker usa su propio context/página (navegador independiente)
    context = await browser.new_context(ignore_https_errors=True, accept_downloads=True)
    page = await context.new_page()
    try:
        while True:
            try:
                registro = queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            reg, est = await procesar_registro(page, registro)
            resultados.append({"Registro Patronal": reg, "Estatus": est})
    finally:
        await context.close()


async def run(playwright: Playwright):
    chromium = playwright.chromium
    browser = await chromium.launch(
        headless=HEADLESS,
        args=["--force-device-scale-factor=0.5", "--window-size=1920,1080"],
    )

    # Leer registros patronales desde el CSV
    registros: list[str] = []
    with open(CSV_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            registro = row.get("Registro Patronal")
            if registro:
                registros.append(registro.strip())

    # Cola con registros para repartir entre workers
    queue: asyncio.Queue = asyncio.Queue()
    for r in registros:
        queue.put_nowait(r)

    resultados: list[dict] = []

    # Lanzar workers
    tasks = [asyncio.create_task(worker(browser, queue, resultados)) for _ in range(WORKERS)]
    await asyncio.gather(*tasks)

    await browser.close()

    # Escribir resultados en un nuevo CSV con columna Estatus
    output_path = str(Path(DOWNLOAD_DIR) / 'estatus_descargas.csv')
    with open(CSV_PATH, newline='', encoding='utf-8') as infile, open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Estatus"] if reader.fieldnames and "Estatus" not in reader.fieldnames else reader.fieldnames
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

if __name__ == "__main__":
    asyncio.run(main())
