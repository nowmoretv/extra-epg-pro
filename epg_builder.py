import urllib.request
import xml.etree.ElementTree as ET
import os
import gzip
from datetime import datetime, timedelta, timezone

# ==============================================================================
# CONFIGURACIÓN DE FUENTES Y CANALES
# ==============================================================================

# ¿Cuántos días hacia el futuro quieres conservar? (1 es hoy y mañana, 3 es los próximos tres días y 7 toda la semana)
DIAS_FUTURO = 3

# 1. Lista de fuentes XMLTV públicas (puedes añadir o quitar las que quieras)
FUENTES_XML = {
    "Espana": "https://github.com/davidmuma/EPG_dobleM/raw/refs/heads/master/guiatv.xml.gz",
    "Mexico": "https://www.open-epg.com/generate/CmMYPab4EY.xml.gz",
    "Argentina": "https://iptv-org.github.io/epg/guides/ar.xml",
    "Colombia": "https://iptv-org.github.io/epg/guides/co.xml"
}

# 2. Tus canales favoritos (deben coincidir con el 'id' exacto de la fuente)
# TIP: Si no sabes el ID, puedes abrir la URL de la fuente en el navegador y buscar el canal.
# MAPEO DE CANALES: "ID_ORIGINAL_EN_FUENTE" : "ID_NUEVO_DESEADO"
MAPEO_CANALES = {
    # España
    "La 1 HD":"La 1",
    "La 2":"La 2",
    "Cuatro.es":"Cuatro",
    "Telecinco.es":"Telecinco",
    "LaSexta.es":"laSexta",
    
    # México
    "LA 1.es":"La 1 Light",
    "LasEstrellas.mx":"Las Estrellas",
    
    # Argentina
    "Telefe.ar":"Telefe",
    "ElTrece.ar":"El Trece",
    
    # Colombia
    "CaracolTV.co":"Caracol TV",
    "RCNTV.co":"RCN"
}

# ==============================================================================
# LÓGICA DE FILTRADO POR FECHAS
# ==============================================================================

def es_programa_valido(fecha_inicio_str, fecha_limite_inicio, fecha_limite_fin):
    """
    Comprueba si la fecha del programa está dentro del rango deseado.
    El formato XMLTV habitual de fecha es: YYYYMMDDHHMMSS +0000
    """
    try:
        # Extraemos solo los primeros 14 caracteres (YYYYMMDDHHMMSS)
        fecha_clean = fecha_inicio_str.split()[0][:14]
        fecha_dt = datetime.strptime(fecha_clean, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        
        # Debe ser posterior al inicio de hoy y anterior a la fecha límite futura
        return fecha_limite_inicio <= fecha_dt <= fecha_limite_fin
    except Exception:
        # Si la fecha viene en un formato extraño, lo dejamos pasar por seguridad
        return True

def obtener_arbol_xml(url, archivo_temp):
    """
    Descarga la URL. Si es un archivo .gz, lo descomprime primero.
    Retorna el objeto ElementTree parseado.
    """
    urllib.request.urlretrieve(url, archivo_temp)
    
    # Comprobamos si la fuente es un archivo comprimido .gz
    if url.endswith('.gz'):
        with gzip.open(archivo_temp, 'rb') as f_in:
            tree = ET.parse(f_in)
    else:
        tree = ET.parse(archivo_temp)
        
    return tree

def generar_epg_combinado():
    root_combinado = ET.Element('tv', generator_info_name="Mi propia EPG")
    canales_agregados = set()

    # Definimos el rango de fechas (UTC)
    ahora_utc = datetime.now(timezone.utc)
    # Desde el inicio del día de hoy (00:00:00)
    fecha_limite_inicio = ahora_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    # Hasta dentro de X días
    fecha_limite_fin = fecha_limite_inicio + timedelta(days=DIAS_FUTURO + 1)

    print(f"--> Filtrando programación desde {fecha_limite_inicio.strftime('%Y-%m-%d')} hasta {fecha_limite_fin.strftime('%Y-%m-%d')}...")

    for pais, url in FUENTES_XML.items():
        # Asignamos la extensión temporal adecuada
        ext = ".xml.gz" if url.endswith('.gz') else ".xml"
        archivo_temp = f"temp_{pais}{ext}"
        print(f"--> Descargando fuente de {pais}...")
        
        try:
            # Parseamos el archivo (sea normal o .gz)
            tree = obtener_arbol_xml(url, archivo_temp)
            root = tree.getroot()

            # 1. Copiar canales de la lista
            for channel in root.findall('channel'):
                canal_id = channel.get('id')
                
                # Si el canal está en nuestra lista de interés
                if id_original in MAPEO_CANALES:
                    id_nuevo = MAPEO_CANALES[id_original]
                    
                    if id_nuevo not in canales_agregados:
                        # Asignamos el nuevo ID al elemento <channel id="...">
                        channel.set('id', id_nuevo)
                        
                        # (Opcional) Cambiar también el nombre visible <display-name> si se quiere
                        display_name = channel.find('display-name')
                        if display_name is not None:
                            display_name.text = id_nuevo
                            
                        root_combinado.append(channel)
                        canales_agregados.add(id_nuevo)

            # 2. Copiar programas solo si son de los canales elegidos Y están en el rango de días
            for programme in root.findall('programme'):
                canal = programme.get('channel')
                start_time = programme.get('start')

                if canal in MAPEO_CANALES and start_time:
                    if es_programa_valido(start_time, fecha_limite_inicio, fecha_limite_fin):
                        id_nuevo = MAPEO_CANALES[canal_original]
                        
                        # Actualizamos el atributo channel="..." del programa al nuevo ID
                        programme.set('channel', id_nuevo)
                        root_combinado.append(programme)

            print(f"    ✔ Procesado {pais} con éxito.")

        except Exception as e:
            print(f"    ❌ Error procesando {pais}: {e}")
        
        finally:
            if os.path.exists(archivo_temp):
                os.remove(archivo_temp)

    print("--> Guardando epg.xml recortado...")
    tree_final = ET.ElementTree(root_combinado)
    ET.indent(tree_final, space="  ", level=0)
    tree_final.write("epg.xml", encoding="utf-8", xml_declaration=True)
    print("¡Proceso completado!")

if __name__ == "__main__":
    generar_epg_combinado()
