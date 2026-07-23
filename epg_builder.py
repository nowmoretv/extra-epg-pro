import urllib.request
import xml.etree.ElementTree as ET
import os
import gzip
from datetime import datetime, timedelta, timezone

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

DIAS_FUTURO = 3

FUENTES_XML = {
    "Espana": "https://iptv-org.github.io/epg/guides/es.xml",
    "Mexico": "https://iptv-org.github.io/epg/guides/mx.xml",
    "Argentina": "https://iptv-org.github.io/epg/guides/ar.xml",
    "Colombia": "https://iptv-org.github.io/epg/guides/co.xml"
}

# MAPEO DE CANALES: "ID_ORIGINAL_EN_FUENTE": "ID_NUEVO_DESEADO"
MAPEO_CANALES = {
    "La 1 HD": "La 1",
    "Antena3.es": "Antena 3",
    "Cuatro.es": "Cuatro",
    "Telecinco.es": "Telecinco",
    "LaSexta.es": "La Sexta",
    "AztecaUno.mx": "Azteca Uno",
    "LasEstrellas.mx": "Las Estrellas",
    "Telefe.ar": "Telefe",
    "ElTrece.ar": "El Trece",
    "CaracolTV.co": "Caracol TV",
    "RCNTV.co": "RCN TV"
}

# ==============================================================================
# LÓGICA DE PROCESAMIENTO Y MAPEADO
# ==============================================================================

def es_programa_valido(fecha_inicio_str, fecha_limite_inicio, fecha_limite_fin):
    try:
        fecha_clean = fecha_inicio_str.split()[0][:14]
        fecha_dt = datetime.strptime(fecha_clean, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        return fecha_limite_inicio <= fecha_dt <= fecha_limite_fin
    except Exception:
        return True

def obtener_arbol_xml(url, archivo_temp):
    urllib.request.urlretrieve(url, archivo_temp)
    if url.endswith('.gz'):
        with gzip.open(archivo_temp, 'rb') as f_in:
            tree = ET.parse(f_in)
    else:
        tree = ET.parse(archivo_temp)
    return tree

def generar_epg_combinado():
    root_combinado = ET.Element('tv', generator_info_name="Mi EPG Personalizada y Mapeada")
    canales_agregados = set()

    ahora_utc = datetime.now(timezone.utc)
    fecha_limite_inicio = ahora_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    fecha_limite_fin = fecha_limite_inicio + timedelta(days=DIAS_FUTURO + 1)

    print(f"--> Filtrando programación desde {fecha_limite_inicio.strftime('%Y-%m-%d')} hasta {fecha_limite_fin.strftime('%Y-%m-%d')}...")

    for pais, url in FUENTES_XML.items():
        ext = ".xml.gz" if url.endswith('.gz') else ".xml"
        archivo_temp = f"temp_{pais}{ext}"
        print(f"--> Descargando fuente de {pais}...")
        
        try:
            tree = obtener_arbol_xml(url, archivo_temp)
            root = tree.getroot()

            # 1. Procesar y renombrar CANALES
            for channel in root.findall('channel'):
                id_original = channel.get('id')
                
                if id_original in MAPEO_CANALES:
                    id_nuevo = MAPEO_CANALES[id_original]
                    
                    if id_nuevo not in canales_agregados:
                        # Cambiamos el id original por el nuevo id
                        channel.set('id', id_nuevo)
                        
                        # Cambiamos el nombre visible <display-name>
                        display_name = channel.find('display-name')
                        if display_name is not None:
                            display_name.text = id_nuevo
                            
                        root_combinado.append(channel)
                        canales_agregados.add(id_nuevo)

            # 2. Procesar, filtrar y renombrar PROGRAMAS
            for programme in root.findall('programme'):
                canal_original = programme.get('channel')
                start_time = programme.get('start')

                if canal_original in MAPEO_CANALES and start_time:
                    if es_programa_valido(start_time, fecha_limite_inicio, fecha_limite_fin):
                        id_nuevo = MAPEO_CANALES[canal_original]
                        programme.set('channel', id_nuevo)
                        root_combinado.append(programme)

            print(f"    ✔ Procesado {pais} con éxito.")

        except Exception as e:
            print(f"    ❌ Error procesando {pais}: {e}")
        
        finally:
            if os.path.exists(archivo_temp):
                os.remove(archivo_temp)

    print("--> Guardando epg.xml final con nombres personalizados...")
    tree_final = ET.ElementTree(root_combinado)
    ET.indent(tree_final, space="  ", level=0)
    tree_final.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso completado!")

if __name__ == "__main__":
    generar_epg_combinado()
