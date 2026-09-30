import time
from modules import opeScrapper
from modules import telegramBot

# ==================== CONFIGURACIÓN ====================
INTERVALO_SEGUNDOS = 300   # Chequeo cada 5 minutos

def monitorear():
    """Bucle principal de ejecución."""
    print(f"Iniciando monitoreo de OPEs SESCAM. Intervalo de chequeo: {INTERVALO_SEGUNDOS} segundos.")
    num_chequeos = 0

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [chequeo: {num_chequeos}] Comprobando sitio web...")
        num_chequeos += 1
        url_list = opeScrapper.obtener_urls_ope()
        for categoria, url in url_list.items():
            documentos_actuales = opeScrapper.obtener_documentos_web(url)
            
            if documentos_actuales:
                actualizados = opeScrapper.buscar_actualizaciones_ope(documentos_actuales,
                                                                    categoria=categoria,
                                                                    ruta=opeScrapper.DOCUMENTOS_OPE)
                
                if len(actualizados) > 0:
                    print("¡Cambio detectado! Enviando alerta...")
                    mensaje = "🚨 *¡Alerta de cambio detectado!*\n\nCategoría actualizada"
                    telegramBot.enviar_telegram(mensaje)

                opeScrapper.guardar_documentos_ope(documentos_actuales,
                                                categoria=categoria,
                                                ruta=opeScrapper.DOCUMENTOS_OPE)
        
        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    monitorear()