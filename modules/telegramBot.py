import requests
import secrets_config as secrets

def enviar_telegram(mensaje):
    """Envía un mensaje a través del Bot de Telegram."""
    telegram_url = f"https://api.telegram.org/bot{secrets.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": secrets.TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(telegram_url, data=payload, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] No se pudo enviar el mensaje por Telegram: {e}")

if __name__ == "__main__":
    """Prueba de envío de mensaje a Telegram."""
    url = "https://www.google.com"
    mensaje_prueba = f"""🚨 *¡Alerta de prueba!*\n\nEste es un mensaje de prueba desde el bot\n {url}"""
    enviar_telegram(mensaje_prueba)