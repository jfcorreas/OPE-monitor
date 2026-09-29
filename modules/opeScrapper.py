import os
import re
import requests
import hashlib
from bs4 import BeautifulSoup

URL_TEST = "https://sanidad.castillalamancha.es/profesionales/atencion-al-profesional/oferta-de-empleo-publico-2023-2024/gestion?field_categoria_profesional_tid=4515&field_sistema_de_acceso_tid=4770"  # Reemplaza con la URL a monitorear

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

def obtener_contenido_web(url):
    """Descarga la página y extrae el texto relevante."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        document_list = []
        for tag in soup.find_all("div", id=re.compile(r"^node-ope-documento")):
            document_list.append(tag.get_text(strip=True))
 
        return document_list
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
  

if __name__ == "__main__":
    print(obtener_contenido_web(url=URL_TEST))