import urllib.request
import xml.etree.ElementTree as ET
import os

# ==============================================================================
# CONFIGURACIÓN DE FUENTES Y CANALES
# ==============================================================================

# 1. Lista de fuentes XMLTV públicas (puedes añadir o quitar las que quieras)
FUENTES_XML = {
    "Espana": "https://iptv-org.github.io/epg/guides/es.xml",
    "Mexico": "https://iptv-org.github.io/epg/guides/mx.xml",
    "Argentina": "https://iptv-org.github.io/epg/guides/ar.xml",
    "Colombia": "https://iptv-org.github.io/epg/guides/co.xml"
}

# 2. Tus canales favoritos (deben coincidir con el 'id' exacto de la fuente)
# TIP: Si no sabes el ID, puedes abrir la URL de la fuente en el navegador y buscar el canal.
CANALES_FAVORITOS = [
    # España
    "La1.es",
    "Antena3.es",
    "Cuatro.es",
    "Telecinco.es",
    "LaSexta.es",
    
    # México
    "AztecaUno.mx",
    "LasEstrellas.mx",
    
    # Argentina
    "Telefe.ar",
    "ElTrece.ar",
    
    # Colombia
    "CaracolTV.co",
    "RCNTV.co"
]

# ==============================================================================
# LÓGICA DEL PROCESAMIENTO
# ==============================================================================

def generar_epg_combinado():
    # Creamos el contenedor XML principal para nuestro epg.xml unificado
    root_combinado = ET.Element('tv', generator_info_name="Mi EPG Personalizada Unificada")
    
    # Conjuntos para controlar que no duplicamos datos
    canales_agregados = set()

    for pais, url in FUENTES_XML.items():
        archivo_temp = f"temp_{pais}.xml"
        print(f"--> Descargando fuente de {pais}...")
        
        try:
            # Descargamos el XML del país
            urllib.request.urlretrieve(url, archivo_temp)
            tree = ET.parse(archivo_temp)
            root = tree.getroot()

            # 1. Filtrar y agregar las definiciones de los Canales
            for channel in root.findall('channel'):
                canal_id = channel.get('id')
                if canal_id in CANALES_FAVORITOS and canal_id not in canales_agregados:
                    root_combinado.append(channel)
                    canales_agregados.add(canal_id)

            # 2. Filtrar y agregar los Programas de esos canales
            for programme in root.findall('programme'):
                if programme.get('channel') in CANALES_FAVORITOS:
                    root_combinado.append(programme)

            print(f"    ✔ Procesado {pais} con éxito.")

        except Exception as e:
            print(f"    ❌ Error procesando {pais}: {e}")
        
        finally:
            # Borramos el archivo temporal descargado para mantener todo limpio
            if os.path.exists(archivo_temp):
                os.remove(archivo_temp)

    # Guardamos el archivo epg.xml consolidado
    print("--> Guardando epg.xml final...")
    tree_final = ET.ElementTree(root_combinado)
    ET.indent(tree_final, space="  ", level=0)
    tree_final.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso completado con éxito!")

if __name__ == "__main__":
    generar_epg_combinado()
