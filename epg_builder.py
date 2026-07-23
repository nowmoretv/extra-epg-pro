import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def generar_xmltv():
    # Creación de la estructura base XMLTV
    tv = ET.Element('tv', generator_info_name="Mi EPG Autogenerada")

    # 1. Lista de Canales Favoritos (id y nombre visible)
    canales = [
        {"id": "TVE1.es", "nombre": "La 1"},
        {"id": "Antena3.es", "nombre": "Antena 3"},
        {"id": "Telecinco.es", "nombre": "Telecinco"}
    ]

    for c in canales:
        canal_elem = ET.SubElement(tv, 'channel', id=c["id"])
        display_name = ET.SubElement(canal_elem, 'display-name')
        display_name.text = c["nombre"]

    # 2. Ejemplo de generación de programas (Aquí integrarías tus fuentes/scraping)
    ahora = datetime.utcnow()
    
    for c in canales:
        # Generamos 24h de programación de prueba paso a paso
        hora_inicio = ahora
        for i in range(12):
            hora_fin = hora_inicio + timedelta(hours=2)
            
            # Formato XMLTV requerido: YYYYMMDDHHMMSS +0000
            start_str = hora_inicio.strftime('%Y%m%d%H%M%S +0000')
            stop_str = hora_fin.strftime('%Y%m%d%H%M%S +0000')

            prog = ET.SubElement(tv, 'programme', {
                'start': start_str,
                'stop': stop_str,
                'channel': c["id"]
            })
            
            title = ET.SubElement(prog, 'title', lang="es")
            title.text = f"Programa de prueba {i+1} en {c['nombre']}"
            
            desc = ET.SubElement(prog, 'desc', lang="es")
            desc.text = "Descripción del evento de televisión emitido."

            hora_inicio = hora_fin

    # Guardar en archivo
    tree = ET.ElementTree(tv)
    ET.indent(tree, space="  ", level=0)
    tree.write("epg.xml", encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    generar_xmltv()
