import re
import requests
import hashlib
import json
from bs4 import BeautifulSoup

URL_TEST = "https://sanidad.castillalamancha.es/profesionales/atencion-al-profesional/oferta-de-empleo-publico-2023-2024/gestion?field_categoria_profesional_tid=4515&field_sistema_de_acceso_tid=4770"  # Reemplaza con la URL a monitorear

DOCUMENTS_ID_TAG = "node-ope-documento"  # ID de los div que contienen los documentos relevantes
DOCUMENTOS_OPE = "data/documentos_ope.json"  # Archivo persistente para no perder el estado al reiniciar el script

# Cabecera para evitar bloqueos por peticiones automáticas
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def obtener_documentos_web(url):
    """Descarga la página y extrae el texto relevante."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        document_list = []
        for tag in soup.find_all("div", id=re.compile(r"^" + DOCUMENTS_ID_TAG)):
            document_list.append(tag.get_text(strip=True))
 
        return document_list
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al acceder a {url}: {e}")
        return None


def calcular_hash(texto):
    """Genera un hash MD5 a partir del contenido de texto."""
    return hashlib.md5(texto.encode("utf-8")).hexdigest()


# def cargar_hash_previo():
#     """Carga el último hash guardado desde el archivo."""
#     if os.path.exists(ARCHIVO_HASH):
#         with open(ARCHIVO_HASH, "r", encoding="utf-8") as f:
#             return f.read().strip()
#     return None


# def guardar_hash(nuevo_hash):
#     """Guarda el nuevo hash en el archivo."""
#     with open(ARCHIVO_HASH, "w", encoding="utf-8") as f:
#         f.write(nuevo_hash)


def guardar_documentos_ope(lista, categoria, ruta):
    """Guarda la lista bajo la clave correspondiente a la categoría en un fichero JSON."""
    with open(ruta, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = {}

    data[categoria] = lista
        
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def buscar_actualizaciones_ope(nueva_lista, categoria, ruta):
    """Compara la nueva lista con la guardada y devuelve los elementos nuevos."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
            lista_guardada = set(data.get(categoria, []))
    except (FileNotFoundError, json.JSONDecodeError):
        lista_guardada = set()

    actualizaciones = [doc for doc in nueva_lista if doc not in lista_guardada]

    return actualizaciones

if __name__ == "__main__":
    documentos = obtener_documentos_web(url=URL_TEST)
    print(f"Longitud de la lista de documentos: {len(documentos)}")

    actualizados = buscar_actualizaciones_ope(documentos, categoria="TEST", ruta=DOCUMENTOS_OPE)
    print(f"Documentos actualizados: {len(actualizados)}\n{chr(10).join(actualizados)}")

    guardar_documentos_ope(documentos, categoria="TEST", ruta=DOCUMENTOS_OPE)