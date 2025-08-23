import re
import time
import random
import pytest
from playwright.sync_api import Page, expect, Playwright, sync_playwright
from Practica.pages.base_page import Funciones_Globales
from Practica.locator.locator_AlertsAndPopups import AlertsPopupsLocatorsPage
from Practica.utils import config
from Practica.utils.logger import setup_logger

def test_ver_simple_alert(set_up_AlertsAndPopups):
    page= set_up_AlertsAndPopups
    
    #IMPORTANTE: Creamos un objeto de tipo función 'Funciones_Globales'
    fg= Funciones_Globales(page) #Este page va ser enviado a la función __init__ en el archivo FuncionesPOM
    #IMPORTANTE: Creamos un objeto de tipo función 'AlertsPopupsLocatorsPage'
    apl= AlertsPopupsLocatorsPage(page)
    
    #fg.verificar_alerta_visible("verificar_alerta_visible_simple_alert", config.SCREENSHOT_DIR, "I am an alert box!")
    fg.verificar_alerta_simple_con_on(apl.botonSimpleAlert, "I am an alert box!", "verificar_alerta_simple_boton_simple_alert", config.SCREENSHOT_DIR)
    
def test_ver_confirmation_alert(set_up_AlertsAndPopups):
    page= set_up_AlertsAndPopups
    
    #IMPORTANTE: Creamos un objeto de tipo función 'Funciones_Globales'
    fg= Funciones_Globales(page) #Este page va ser enviado a la función __init__ en el archivo FuncionesPOM
    #IMPORTANTE: Creamos un objeto de tipo función 'AlertsPopupsLocatorsPage'
    apl= AlertsPopupsLocatorsPage(page)
    
    fg.validar_elemento_no_visible(apl.mensajeConfirmacionDeAccion, "validar_elemento_no_visible_mensaje_Confirmación_De_Accion", config.SCREENSHOT_DIR)
    fg.validar_elemento_no_visible(apl.mensajeConfirmacionDeAccion, "validar_elemento_no_visible_mensaje_Confirmación_De_Accion", config.SCREENSHOT_DIR)
    fg.verificar_confirmacion_on_dialog(apl.botonConfirmationAlert, "Press a button!", "accept", "verificar_confirmación_on_dialog_boton_Confirmation_Alert", config.SCREENSHOT_DIR)
    fg.verificar_texto_contenido(apl.mensajeConfirmacionDeAccion, "You pressed OK!", "verificar_texto_contenido_mensaje_Confirmacion_De_Accion", config.SCREENSHOT_DIR)
    fg.verificar_confirmacion_on_dialog(apl.botonConfirmationAlert, "Press a button!", "dismiss", "verificar_confirmación_dismiss_on_dialog_boton_Confirmation_Alert", config.SCREENSHOT_DIR)
    fg.verificar_texto_contenido(apl.mensajeConfirmacionDeAccion, "You pressed Cancel!", "verificar_texto_contenido_mensaje_Confirmacion_De_Accion", config.SCREENSHOT_DIR)
    
def test_ver_prompt_alert_con_on(set_up_AlertsAndPopups):
    page= set_up_AlertsAndPopups
    
    #IMPORTANTE: Creamos un objeto de tipo función 'Funciones_Globales'
    fg= Funciones_Globales(page) #Este page va ser enviado a la función __init__ en el archivo FuncionesPOM
    #IMPORTANTE: Creamos un objeto de tipo función 'AlertsPopupsLocatorsPage'
    apl= AlertsPopupsLocatorsPage(page)
    
    texto_a_ingresar = "Playwright User On"
    resultado_mensaje_esperado = f"Hello {texto_a_ingresar}! How are you today?"
    
    fg.verificar_prompt_on_dialog(apl.botonPromptAlert, "Please enter your name:", texto_a_ingresar, "accept", "verificar_prompt_on_dialog_botón_Prompt_Alert", config.SCREENSHOT_DIR)
    fg.validar_elemento_visible(apl.mensajeConfirmacionDeAccion, "validar_elemento_visible_mensaje_Confirmación_DeAccion", config.SCREENSHOT_DIR)
    fg.verificar_texto_contenido(apl.mensajeConfirmacionDeAccion, resultado_mensaje_esperado, "verificar_texto_contenido_mensaje_Confirmacion_De_Accion", config.SCREENSHOT_DIR)
    
    fg.verificar_prompt_on_dialog(apl.botonPromptAlert, "Please enter your name:", texto_a_ingresar, "dismiss", "verificar_prompt_on_dialog_botón_Prompt_Alert", config.SCREENSHOT_DIR)
    fg.validar_elemento_visible(apl.mensajeConfirmacionDeAccion, "validar_elemento_visible_mensaje_Confirmación_DeAccion", config.SCREENSHOT_DIR)
    fg.verificar_texto_contenido(apl.mensajeConfirmacionDeAccion, "User cancelled the prompt.", "verificar_texto_contenido_mensaje_Confirmacion_De_Accion", config.SCREENSHOT_DIR)
    
def test_ver_nuevo_tab(set_up_AlertsAndPopups):
    page_original = set_up_AlertsAndPopups # Guardamos la referencia a la página ORIGINAL

    fg = Funciones_Globales(page_original) # fg se inicializa con la página original
    apl = AlertsPopupsLocatorsPage(page_original) # Esta instancia 'apl' también se inicializa con la página original

    # 1. Realizar la acción que abre la nueva pestaña y cambiar el foco
    # Ahora, 'abrir_y_cambiar_a_nueva_pestana' manejará tanto el clic como la espera y el cambio de foco.
    nueva_pestana_page = fg.abrir_y_cambiar_a_nueva_pestana(apl.botonNewTab, "abrir_nueva_pestana", config.SCREENSHOT_DIR)

    # 2. VERIFICAR QUE SE HAYA CAMBIADO A LA NUEVA PESTAÑA
    if nueva_pestana_page:
        # IMPORTANTE: Re-instanciar AlertsPopupsLocatorsPage con la *nueva* página
        # Esto asegura que los locators dentro de apl_nueva_pestana apunten a la nueva pestaña
        apl_nueva_pestana = AlertsPopupsLocatorsPage(nueva_pestana_page)

        # Ahora puedes realizar validaciones en la nueva pestaña
        # fg.page ya apunta a la nueva pestaña gracias a 'abrir_y_cambiar_a_nueva_pestana'
        fg.validar_url_actual("https://www.pavantestingtools.com")
        fg.validar_titulo_de_web("SDET-QA Blog", "validar_titulo_de_web", config.SCREENSHOT_DIR)

        # Usa la nueva instancia de locators para verificar el texto en la nueva pestaña
        fg.verificar_texto_contenido(apl_nueva_pestana.tituloEncabezadoNuevatab1, "SDET-QA Blog", "verificar_texto_contenido_titulo_Encabezado_Nuevatab_1", config.SCREENSHOT_DIR)
        fg.scroll_pagina(0, 200)
        
        # 3. Cerrar la nueva pestaña después de todas las validaciones
        fg.cerrar_pestana_actual("cerrar_pestana_nueva", config.SCREENSHOT_DIR)

        # Opcional: Si necesitas volver a interactuar con la página original específica después de cerrar la nueva pestaña,
        # y cerrar_pestana_actual no te devolvió automáticamente a ella, puedes reasignar fg.page
        fg.page = page_original # Esto podría ser necesario si cerrar_pestana_actual no cambia al foco deseado
        print(f"\n🔄 Foco vuelto a la página original: URL = {fg.page.url}")

    else:
        pytest.fail("No se pudo abrir o cambiar a la nueva pestaña. La prueba falló.")
        
    fg.validar_url_actual(".*/p/playwrightpractice.html")
    fg.validar_titulo_de_web("Automation Testing Practice: PlaywrightPractice", "validar_titulo_de_web", config.SCREENSHOT_DIR)
    fg.esperar_fijo(2)

@pytest.mark.skip(reason="A veces falla cuando se ejecutan todos los archivos de pruebas, pero funciona si se ejecuta unicamente test_alertsAndPopups.py")    
def test_ver_nueva_ventana(set_up_AlertsAndPopups):
    page_original = set_up_AlertsAndPopups # Guardamos la referencia a la página ORIGINAL

    fg = Funciones_Globales(page_original) # fg se inicializa con la página original
    apl_original = AlertsPopupsLocatorsPage(page_original) # Instancia para la página original

    # Definir nombre_base_test y directorio_capturas antes de usarlos
    nombre_base_test = "TestNuevaVentana"

    # --- Inicia el bloque principal de try-except ---
    try:
        # Paso 1: Realizar la acción que abre la(s) nueva(s) ventana(s)
        print("\n--- Ejecutando acción para abrir nueva(s) ventana(s) ---")
        todas_las_nuevas_ventanas = fg.hacer_clic_y_abrir_nueva_ventana(
            apl_original.botonNuevaVentana,
            nombre_base_test,
            config.SCREENSHOT_DIR,
            nombre_paso="Clic en 'Popup Windows'",
            # Aumentar el tiempo de espera para evitar el "race condition"
            tiempo_espera_max_total=10.0 # Ajustado a 10 segundos
        )

        # Paso 2: Si se abrieron ventanas, procesarlas
        print(f"✅ Se detectaron y cargaron {len(todas_las_nuevas_ventanas)} nueva(s) ventana(s).")
        assert len(todas_las_nuevas_ventanas) == 2, f"Se esperaban 2 ventanas, pero se encontraron {len(todas_las_nuevas_ventanas)}."

        # Paso 3: Validar el contenido de cada ventana
        # Se utilizan variables para facilitar el acceso a cada página
        selenium_page = [p for p in todas_las_nuevas_ventanas if "selenium.dev" in p.url]
        playwright_page = [p for p in todas_las_nuevas_ventanas if "playwright.dev" in p.url]

        assert selenium_page, "No se encontró la ventana de Selenium."
        assert playwright_page, "No se encontró la ventana de Playwright."
        
        # Validar la página de Selenium
        print("\n--- Validando contenido de la ventana de Selenium ---")
        fg.verificar_texto_contenido(
            locator=selenium_page[0].locator("h1.text-gray-900"),
            texto_esperado="Selenium automates browsers. That's it!",
            nombre_base=f"{nombre_base_test}_selenium",
            directorio=config.SCREENSHOT_DIR,
            nombre_paso="Verificar texto en ventana de Selenium"
        )
        print("✅ Aserciones en la ventana de Selenium pasadas exitosamente.")

        # Validar la página de Playwright
        print("\n--- Validando contenido de la ventana de Playwright ---")
        fg.verificar_texto_contenido(
            locator=playwright_page[0].locator("h1.docTitle_p06K"),
            texto_esperado="Playwright enables reliable end-to-end testing for modern web apps.",
            nombre_base=f"{nombre_base_test}_playwright",
            directorio=config.SCREENSHOT_DIR,
            nombre_paso="Verificar texto en ventana de Playwright"
        )
        print("✅ Aserciones en la ventana de Playwright pasadas exitosamente.")

        # Paso 4: Cerrar las ventanas que no sean la original
        print("\n--- Cerrando todas las ventanas nuevas ---")
        for page_obj in todas_las_nuevas_ventanas:
            fg.cerrar_pestana_especifica(page_obj, "cerrar_pestana_especifica", config.SCREENSHOT_DIR, f"Ventana: {page_obj.title()}")
        
        # Paso 5: Validar que el foco ha regresado a la página original
        # No se necesita una espera, Playwright lo maneja automáticamente
        print("\n--- Verificando que el foco haya regresado a la página original ---")
        assert len(page_original.context.pages) == 1, "No se regresó a la página original, o hay ventanas extras abiertas."
        assert page_original.is_visible(), "La página original no está visible después de cerrar las ventanas."
        assert "playwrightpractice.html" in page_original.url, "La URL no corresponde a la página original."
        print("✅ Foco regresado exitosamente a la página original.")

        print("\n---------- Fin del escenario de prueba 'test_ver_nueva_ventana' ----------")

    except AssertionError as e:
        print(f"\n❌ El test falló en una aserción: {e}")
        fg.tomar_captura(f"{nombre_base_test}_FALLO", config.SCREENSHOT_DIR)
        raise e
    except Exception as e:
        print(f"\n❌ El test falló debido a un error inesperado: {e}", exc_info=True)
        fg.tomar_captura(f"{nombre_base_test}_FALLO_FINAL", config.SCREENSHOT_DIR)
        raise e
