import hashlib
import os
import time
import requests
from bs4 import BeautifulSoup

# ==================== CONFIGURACIÓN ====================
URL = "https://sanidad.castillalamancha.es/profesionales/atencion-al-profesional/oferta-de-empleo-publico-2023-2024/gestion?field_categoria_profesional_tid=4515&field_sistema_de_acceso_tid=4770"  # Reemplaza con la URL a monitorear
INTERVALO_SEGUNDOS = 300   # Chequeo cada 5 minutos

# Configuración de Telegram
TELEGRAM_BOT_TOKEN = "TU_BOT_TOKEN_AQUI"  # Pega aquí el token de BotFather
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI"     # Pega aquí tu ID numérico de Telegram

# Archivo persistente para no perder el estado al reiniciar el script
ARCHIVO_HASH = "ultimo_hash.txt"

# Cabecera para evitar bloqueos por peticiones automáticas
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
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


def obtener_contenido_web(url):
    """Descarga la página y extrae el texto relevante."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # OPCIÓN A: Monitorear el cuerpo del sitio
        contenido = soup.find("body")
        
        # OPCIÓN B: Descomentar si deseas monitorear solo un elemento específico
        contenido = soup.find("div", id="block-system-main") 
        
        if contenido:
            return contenido.get_text(strip=True)
        return ""
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al acceder a {url}: {e}")
        return None


def calcular_hash(texto):
    """Genera un hash MD5 a partir del contenido de texto."""
    return hashlib.md5(texto.encode("utf-8")).hexdigest()


def cargar_hash_previo():
    """Carga el último hash guardado desde el archivo."""
    if os.path.exists(ARCHIVO_HASH):
        with open(ARCHIVO_HASH, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def guardar_hash(nuevo_hash):
    """Guarda el nuevo hash en el archivo."""
    with open(ARCHIVO_HASH, "w", encoding="utf-8") as f:
        f.write(nuevo_hash)


def monitorear():
    """Bucle principal de ejecución."""
    print(f"Iniciando monitoreo de: {URL}")
    hash_previo = cargar_hash_previo()

    while True:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Comprobando sitio web...")
        texto_actual = obtener_contenido_web(URL)
        
        if texto_actual:
            hash_actual = calcular_hash(texto_actual)
            
            if hash_previo is None:
                print("Estado inicial guardado.")
                guardar_hash(hash_actual)
                hash_previo = hash_actual
                #enviar_telegram(f"🤖 *Monitoreo iniciado*\nSe ha registrado el estado inicial de: {URL}")
            elif hash_actual != hash_previo:
                print("¡Cambio detectado! Enviando alerta...")
                mensaje = (
                    f"🚨 *¡Alerta de cambio detectado!*\n\n"
                    f"La página web ha sido actualizada:\n{URL}"
                )
                # enviar_telegram(mensaje)
                guardar_hash(hash_actual)
                hash_previo = hash_actual
            else:
                print("Sin cambios.")
        
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    monitorear()