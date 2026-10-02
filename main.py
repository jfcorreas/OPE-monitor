import time
from modules import opeScrapper
from modules import telegramBot

# ==================== CONFIGURACIÓN ====================
INTERVALO_CHEQUEOS = 3600   # Chequeo cada hora
INTERVALO_ENTRE_CATEGORIAS = 10  # Intervalo entre chequeos de categorías (en segundos)

def monitorear():
    """Bucle principal de ejecución."""
    print(f"Iniciando monitoreo de OPEs SESCAM. Intervalo de chequeo: {INTERVALO_CHEQUEOS} segundos.")
    num_chequeos = 0

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [chequeo: {num_chequeos}] Comprobando sitio web...")
        url_list = opeScrapper.obtener_urls_ope()
        num_alertas = 0
        for categoria, url in url_list.items():
            documentos_actuales = opeScrapper.obtener_documentos_web(url)
            if documentos_actuales:
                actualizados = opeScrapper.buscar_actualizaciones_ope(documentos_actuales,
                                                                    categoria=categoria,
                                                                    ruta=opeScrapper.DOCUMENTOS_OPE)
                
                if len(actualizados) > 0:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] " \
                        f"¡Cambio detectado!: categoría {categoria}. Enviando alerta...")
                    mensaje = f"🚨 *¡Alerta de cambio detectado!*\n\n" \
                            f"*Categoría actualizada*: {categoria}\n\n" \
                            f"*Documentos nuevos*:\n· {'\n· '.join(actualizados)}\n\n" \
                            f"[Visita la página para más detalles]({url})"
                    telegramBot.enviar_telegram(mensaje)
                    num_alertas += 1

                opeScrapper.guardar_documentos_ope(documentos_actuales,
                                                categoria=categoria,
                                                ruta=opeScrapper.DOCUMENTOS_OPE)
                time.sleep(INTERVALO_ENTRE_CATEGORIAS)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] " \
              f"[chequeo: {num_chequeos}] Completado: " \
              f"{len(url_list)} categorías comprobadas / {num_alertas} alertas enviadas.") 
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] " \
            f"Esperando {int(INTERVALO_CHEQUEOS/60)} minutos para el siguiente chequeo...")
        num_chequeos += 1
        time.sleep(INTERVALO_CHEQUEOS)

if __name__ == "__main__":
    monitorear()