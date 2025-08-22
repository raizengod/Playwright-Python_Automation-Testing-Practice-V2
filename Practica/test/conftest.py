# nombra el archivo: Ve a la ubicación de tu archivo y colcoar el nombre a conftest.py
# La convención de conftest.py le indica a Pytest que este archivo contiene fixtures que deben estar disponibles 
# para los tests en ese directorio y sus subdirectorios.
import pytest
import time
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from datetime import datetime
import os
from typing import Generator
from Practica.utils import config
from Practica.pages.base_page import Funciones_Globales
from Practica.locator.locator_barraMenu import MenuLocatorsPage
from Practica.locator.locator_getByRole import RoleLocatorsPage
from Practica.locator.locator_getByText import TextLocatorsPage

# Función para generar IDs legibles
def generar_ids_browser(param):
    """
    Genera un ID descriptivo para cada combinación de navegador y dispositivo.
    """
    browser = param['browser']
    device = param['device']
    resolution = param['resolution']

    if device:
        return f"{browser}-{device}"
    else:
        return f"{browser}-{resolution['width']}x{resolution['height']}"

@pytest.fixture(
    scope="function",
    params=[
            # Resoluciones de escritorio
            {"browser": "chromium", "resolution": {"width": 1920, "height": 1080}, "device": None},
            {"browser": "firefox", "resolution": {"width": 1920, "height": 1080}, "device": None},
            {"browser": "webkit", "resolution": {"width": 1920, "height": 1080}, "device": None},
            # Emulación de dispositivos móviles
            #{"browser": "chromium", "device": "iPhone 12", "resolution": None},
            {"browser": "webkit", "device": "Pixel 5", "resolution": None},
            {"browser": "webkit", "device": "iPhone 12", "resolution": None}
    ],
    ids=generar_ids_browser # <--- Usar la función para generar IDs
)
def playwright_page(playwright: Playwright, request) -> Generator[Page, None, None]:
    """
    Fixture base para configurar el navegador, contexto y página de Playwright con configuraciones comunes.
    Maneja el lanzamiento del navegador, la creación del contexto (con grabación de video y emulación de dispositivos),
    el rastreo (tracing) y la navegación de la página a una URL específica. También renombra el archivo de video al finalizar.
    """
    param = request.param
    browser_type = param["browser"]
    resolution = param["resolution"]
    device_name = param["device"]

    browser_instance = None
    context = None
    page = None

    try:
        if browser_type == "chromium":
            browser_instance = playwright.chromium.launch(headless=True, slow_mo=500)
        elif browser_type == "firefox":
            browser_instance = playwright.firefox.launch(headless=True, slow_mo=500)
        elif browser_type == "webkit":
            browser_instance = playwright.webkit.launch(headless=True, slow_mo=500)
        else:
            raise ValueError(f"\nEl tipo de navegador '{browser_type}' no es compatible.")

        context_options = {
            "record_video_dir": config.VIDEO_DIR,
            "record_video_size": {"width": 1920, "height": 1080}
        }

        if device_name:
            device = playwright.devices[device_name]
            context = browser_instance.new_context(**device, **context_options)
        elif resolution:
            context = browser_instance.new_context(viewport=resolution, **context_options)
        else:
            context = browser_instance.new_context(**context_options)

        page = context.new_page()

        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        trace_name_suffix = ""
        if device_name:
            trace_name_suffix = device_name.replace(" ", "_").replace("(", "").replace(")", "")
        elif resolution:
            trace_name_suffix = f"{resolution['width']}x{resolution['height']}"

        trace_file_name = f"traceview_{current_time}_{browser_type}_{trace_name_suffix}.zip"
        trace_path = os.path.join(config.TRACEVIEW_DIR, trace_file_name)

        context.tracing.start(screenshots=True, snapshots=True, sources=True)

        yield page

    finally:
        if context:
            context.tracing.stop(path=trace_path)
            context.close()
            
        if browser_instance:
            browser_instance.close()
            
        if page and page.video:
            video_path = page.video.path()
            new_video_name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".webm"
            new_video_path = os.path.join(config.VIDEO_DIR, new_video_name)
            try:
                os.rename(video_path, new_video_path)
                print(f"\nVideo guardado como: {new_video_path}")
            except Exception as e:
                print(f"\nError al renombrar el video: {e}")

@pytest.fixture(scope="function")
def set_up_ir_a(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que comienzan desde la página principal.

    Navega a la URL base y configura el timeout por defecto para la página.
    """
    # Navega a la URL base definida en 'config.BASE_URL'
    # 'wait_until="domcontentloaded"' espera a que el DOM se cargue completamente antes de continuar
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    
    # Establece un timeout por defecto de 10 segundos (10000 ms) para las operaciones de Playwright
    playwright_page.set_default_timeout(10000)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_by_role(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que utilizan localizadores 'byRole'.
    
    Navega a la página de inicio, hace clic en el enlace 'PlaywrightPractice',
    y valida la URL y el título antes de ceder el control a la prueba.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # 1. Valida que la URL actual sea la de la página de inicio
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
       
    fg.esperar_fijo(1) # Espera fija para asegurar la estabilidad
    
    # 2. Hace clic en el enlace que lleva a la página de práctica de Playwright
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    
    # 3. Valida que la nueva URL sea la de la página de práctica
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    
    # 4. Valida que el título de la página sea el correcto
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_byText(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que usan localizadores 'byText'.
    
    Configura el entorno de la página de práctica de Playwright y se desplaza
    hacia abajo para asegurar la visibilidad de los elementos 'byText'.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, hace clic en el enlace y valida la nueva URL y el título de la página
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 500 píxeles para exponer los elementos relevantes
    fg.scroll_pagina(0, 500)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_byLabel(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que usan localizadores 'byLabel'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con etiquetas (labels) de formulario.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, hace clic en el enlace y valida la nueva URL y el título de la página
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 1200 píxeles
    fg.scroll_pagina(0, 1200)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_byPlaceholder(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que usan localizadores 'byPlaceholder'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los campos de entrada con texto de marcador de posición.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1) # Espera fija para asegurar la estabilidad
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 1800 píxeles
    fg.scroll_pagina(0, 1800)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_byAtlText(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que usan localizadores 'byAltText'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de las imágenes con texto alternativo.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 2100 píxeles
    fg.scroll_pagina(0, 2100)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_byTitle(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que usan localizadores 'byTitle'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con texto de título.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 2550 píxeles
    fg.scroll_pagina(0, 2550)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page

@pytest.fixture(scope="function")
def set_up_byTestId(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas que usan localizadores 'byTestId'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con atributos 'data-testid'.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 3000 píxeles
    fg.scroll_pagina(0, 3000)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page
    
@pytest.fixture(scope="function")
def set_up_cargarArchivo(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas de 'cargarArchivos'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con atributos 'data-testid'.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 3800 píxeles
    fg.scroll_pagina(0, 3800)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page
    
@pytest.fixture(scope="function")
def set_up_manejodDeTabla(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas de 'manejodDeTabla'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con atributos 'data-testid'.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 3800 píxeles
    fg.scroll_pagina(0, 4400)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page
    
@pytest.fixture(scope="function")
def set_up_checkBoxLista(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas de 'checkBoxLista'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con atributos 'data-testid'.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 3800 píxeles
    fg.scroll_pagina(0, 5000)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page
    
@pytest.fixture(scope="function")
def set_up_AlertsAndPopups(playwright_page: Page) -> Generator[Page, None, None]:
    """
    Fixture de configuración para pruebas de 'checkBoxLista'.
    
    Configura el entorno y se desplaza hacia abajo para asegurar la visibilidad
    de los elementos con atributos 'data-testid'.
    """
    # Navega a la URL base y configura el timeout por defecto
    playwright_page.goto(config.BASE_URL, wait_until="domcontentloaded")
    playwright_page.set_default_timeout(10000)
    
    # Inicializa las clases de funciones globales y localizadores del menú
    fg = Funciones_Globales(playwright_page)
    ml = MenuLocatorsPage(playwright_page)
    
    # PRE-CONDICIONES:
    # Valida URL, espera un segundo, hace clic, y valida la nueva URL y el título
    fg.validar_url_actual("https://testautomationpractice.blogspot.com")
    fg.esperar_fijo(1)
    fg.hacer_click_en_elemento(ml.irAPlaywright, "Clic_PlaywrightPractice", config.SCREENSHOT_DIR, "PlaywrightPractice")
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    
    # 5. Se desplaza verticalmente 3800 píxeles
    fg.scroll_pagina(0, 400)
    
    # El 'yield' devuelve el objeto 'page' a la prueba para su uso
    yield playwright_page