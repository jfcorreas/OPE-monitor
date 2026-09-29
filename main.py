import time
import requests
from modules import opeScrapper

# ==================== CONFIGURACIÓN ====================
URL = "https://sanidad.castillalamancha.es/profesionales/atencion-al-profesional/oferta-de-empleo-publico-2023-2024/gestion?field_categoria_profesional_tid=4515&field_sistema_de_acceso_tid=4770"  # Reemplaza con la URL a monitorear
INTERVALO_SEGUNDOS = 300   # Chequeo cada 5 minutos

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = "TU_BOT_TOKEN_AQUI"  # Pega aquí el token de BotFather
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI"     # Pega aquí tu ID numérico de Telegram
# =======================================================

def enviar_telegram(mensaje):
    """Envía un mensaje a través del Bot de Telegram."""
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(telegram_url, data=payload, timeout=10)
        response.raise_for_status()
        print("Notificación enviada a Telegram correctamente.")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] No se pudo enviar el mensaje por Telegram: {e}")


def monitorear():
    """Bucle principal de ejecución."""
    print(f"Iniciando monitoreo de: {URL}")
    hash_previo = opeScrapper.cargar_hash_previo()

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Comprobando sitio web...")
        texto_actual = opeScrapper.obtener_contenido_web(URL)
        
        if texto_actual:
            hash_actual = opeScrapper.calcular_hash(texto_actual)
            
            if hash_previo is None:
                print("Estado inicial guardado.")
                opeScrapper.guardar_hash(hash_actual)
                hash_previo = hash_actual
                #enviar_telegram(f"🤖 *Monitoreo iniciado*\nSe ha registrado el estado inicial de: {URL}")
            elif hash_actual != hash_previo:
                print("¡Cambio detectado! Enviando alerta...")
                mensaje = (
                    f"🚨 *¡Alerta de cambio detectado!*\n\n"
                    f"La página web ha sido actualizada:\n{URL}"
                )
                # enviar_telegram(mensaje)
                opeScrapper.guardar_hash(hash_actual)
                hash_previo = hash_actual
            else:
                print("Sin cambios.")
        
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    monitorear()