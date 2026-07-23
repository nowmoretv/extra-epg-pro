import urllib.request
import xml.etree.ElementTree as ET

# 1. URL de la fuente pública de EPG (por ejemplo, España en iptv-org)
URL_FUENTE = "https://iptv-org.github.io/epg/guides/es.xml"

# 2. Tu lista de IDs de canales preferidos (deben coincidir con el ID de la fuente)
MIS_CANALES_FAVORITOS = [
    "La1.es",
    "Antena3.es",
    "Cuatro.es",
    "Telecinco.es",
    "LaSexta.es"
]

def filtrar_epg():
    print("Descargando EPG de la fuente...")
    urllib.request.urlretrieve(URL_FUENTE, "fuente_temporal.xml")
    
    print("Filtrando programación...")
    tree = ET.parse("fuente_temporal.xml")
    root = tree.getroot()
    
    # Creamos un nuevo árbol XML solo con lo necesario
    nuevo_tv = ET.Element('tv', generator_info_name="Mi EPG Filtrada")
    
    # Guardar solo la información de los canales seleccionados
    for channel in root.findall('channel'):
        if channel.get('id') in MIS_CANALES_FAVORITOS:
            nuevo_tv.append(channel)
            
    # Guardar solo los programas de los canales seleccionados
    for programme in root.findall('programme'):
        if programme.get('channel') in MIS_CANALES_FAVORITOS:
            nuevo_tv.append(programme)
            
    # Guardar el resultado final
    nuevo_tree = ET.ElementTree(nuevo_tv)
    ET.indent(nuevo_tree, space="  ", level=0)
    nuevo_tree.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("¡epg.xml generado con éxito!")

if __name__ == "__main__":
    filtrar_epg()
