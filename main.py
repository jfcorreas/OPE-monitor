import time
from modules import opeScrapper
from modules import telegramBot

# ==================== CONFIGURACIÓN ====================
URL = "https://sanidad.castillalamancha.es/profesionales/atencion-al-profesional/oferta-de-empleo-publico-2023-2024/gestion?field_categoria_profesional_tid=4515&field_sistema_de_acceso_tid=4770"  # Reemplaza con la URL a monitorear
INTERVALO_SEGUNDOS = 300   # Chequeo cada 5 minutos

def monitorear():
    """Bucle principal de ejecución."""
    print(f"Iniciando monitoreo de: {URL}")
    num_chequeos = 0

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Comprobando sitio web...")
        documentos_actuales = opeScrapper.obtener_documentos_web(URL)
        
        if documentos_actuales:
            num_chequeos += 1
            actualizados = opeScrapper.buscar_actualizaciones_ope(documentos_actuales,
                                                                  categoria="OPE",
                                                                  ruta=opeScrapper.DOCUMENTOS_OPE)
            
            if len(actualizados) > 0:
                print("¡Cambio detectado! Enviando alerta...")
                mensaje = (
                    f"🚨 *¡Alerta de cambio detectado!*\n\n"
                    f"La página web ha sido actualizada: {len(actualizados)} documentos nuevos\n{URL}")
                telegramBot.enviar_telegram(mensaje)

            opeScrapper.guardar_documentos_ope(documentos_actuales,
                                               categoria="OPE",
                                               ruta=opeScrapper.DOCUMENTOS_OPE)
        
        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    monitorear()