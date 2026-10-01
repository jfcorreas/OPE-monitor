import re
import requests
import json
from bs4 import BeautifulSoup

URL_TEST = "https://sanidad.castillalamancha.es/profesionales/atencion-al-profesional/oferta-de-empleo-publico-2023-2024/gestion?field_categoria_profesional_tid=4515&field_sistema_de_acceso_tid=4770"  # Reemplaza con la URL a monitorear

DOCUMENTS_ID_TAG = "node-ope-documento"  # ID de los div que contienen los documentos relevantes
DOCUMENTOS_OPE = "data/documentos_ope.json" 
OPE_ACTUAL = "ope23-24"
BBDD_PAGINAS_OPE = "data/paginas_ope.json" 
TEXTO_PARENTESIS_REGEX =  r"\(.*\)"

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
            documento = re.sub(TEXTO_PARENTESIS_REGEX, "", tag.get_text(strip=True))
            documento = documento[:11] + " - " + documento[11:]  
            document_list.append(documento.strip())
 
        return document_list
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error al acceder a {url}: {e}")
        return None

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

def obtener_urls_ope():
    """Obtiene las URLs de las páginas de la OPE_ACTUAL desde el archivo JSON."""
    try:
        with open(BBDD_PAGINAS_OPE, "r", encoding="utf-8") as f:
            data = json.load(f)
            ope_actual = data[OPE_ACTUAL]   
            url_base_ope = ope_actual["URL_base"]
            categorias = ope_actual["categorias"]
            dict_urls = {}
            for categoria in categorias:
                dict_urls[categoria["abreviatura"]] = url_base_ope + categoria["url"]
            return dict_urls
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

if __name__ == "__main__":
    """ Prueba de las funciones del módulo opeScrapper.py con la primera categoría de la OPE_ACTUAL """
    urls = obtener_urls_ope()

    categoria, url_categoria = list(urls.items())[0]  # Obtiene la primera categoría y su URL
    print(f"Categoría: {categoria}, URL: {url_categoria}")

    documentos = obtener_documentos_web(url=url_categoria)
    print(f"Longitud de la lista de documentos: {len(documentos)}")

    actualizados = buscar_actualizaciones_ope(documentos, categoria=categoria, ruta=DOCUMENTOS_OPE)
    print(f"Documentos actualizados: {len(actualizados)}\n{chr(10).join(actualizados)}")

    guardar_documentos_ope(documentos, categoria=categoria, ruta=DOCUMENTOS_OPE)