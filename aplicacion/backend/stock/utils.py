import string
import math
import uuid

# ----- REDONDEO DE PRECIOS -----

def redondear_precio(precio, modo="superior"):
    if modo == "superior":
        return math.ceil(precio)
    elif modo == "inferior":
        return math.floor(precio)
    elif modo == "entero":
        return round(precio)
    else:
        return precio

# ----- CÁLCULO DE PRECIO CON MARGEN -----

def calcular_precio_con_margen(costo_unitario, margen):
    if margen >= 1.0:
        raise ValueError("El margen debe ser menor a 1 (representa porcentaje de ganancia sobre el precio final).")
    return costo_unitario / (1 - margen)

def calcular_margen_con_precio(costo_unitario, precio_venta):
    if precio_venta == 0:
        return 0.0
    return round(1 - (costo_unitario / precio_venta), 4)

# ----- SOPORTE PARA PRODUCTOS DIVISIBLES -----

def es_producto_divisible(producto):
    return producto.es_divisible

# ----- BÚSQUEDA -----

def buscar_productos_por_nombre(lista_productos, termino):
    termino = termino.lower()
    palabras = termino.split()
    resultados = []
    for p in lista_productos:
        nombre = str(p.nombre).lower() if p.nombre else ""
        if all(palabra in nombre for palabra in palabras):
            resultados.append(p)
    return resultados

def buscar_productos_por_codigo(lista_unidades, codigo_barras):
    return [u for u in lista_unidades if codigo_barras in u.codigo_barras]

# ----- BÚSQUEDA INCREMENTAL -----

def filtrar_productos_incremental(lista_productos, texto_busqueda):
    return [p for p in lista_productos if texto_busqueda.lower() in p.nombre.lower()]

# ----- ALERTAS DE STOCK -----

def verificar_stock_bajo(producto, umbral=5):
    return producto.cantidad <= umbral

def verificar_sin_stock(producto):
    return producto.cantidad <= 0

# ----- CLASIFICACIÓN DE PRODUCTOS DIVISIBLES -----

def clasificar_producto_por_unidad(unidad):
    unidades_divisibles = ['g', 'kg', 'ml', 'l']
    return unidad.lower() in unidades_divisibles

# ----- GENERACIÓN DE CÓDIGOS DE BARRAS -----

# ----- GENERACIÓN DE CÓDIGOS DE BARRAS -----

def generar_codigo_barras_con_letras(longitud=13):
    """
    Genera un código alfanumérico de 13 caracteres para identificar productos a granel (kg).
    Combina letras y números para diferenciarlos de los códigos de barras EAN-13 normales.
    """
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

import random

def generar_codigo_barras():
    """
    Genera un código de barras numérico de 13 dígitos.
    Compatible con el estándar EAN-13 (sin cálculo de checksum por ahora).
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(13)])


# ----- FECHA ACTUAL -----

from datetime import datetime

def fecha_actual_iso():
    return datetime.now().isoformat()


# Agregar esta función al final de utils.py

def obtener_codigos_por_producto(producto_id):
    """
    Busca todos los códigos de barras asociados a un producto_id en la tabla stock_unidades.
    
    Args:
        producto_id (int): ID del producto a buscar
        
    Returns:
        dict: Diccionario con códigos de barras como claves y información como valores
              Formato: {
                  "codigo_barras": {
                      "vencimiento": "YYYY-MM-DD" o None,
                      "estado": "activo/inactivo",
                      "observaciones": "texto" o "",
                      "fecha_ingreso": "fecha_iso",
                      "id_unidad": int
                  }
              }
              Retorna diccionario vacío si no encuentra unidades
    """
    from sqlalchemy.orm import sessionmaker
    from aplicacion.backend.database.database import engine, StockUnidad
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Buscar todas las unidades del producto
        unidades = session.query(StockUnidad).filter_by(producto_id=producto_id).all()
        
        # Crear diccionario con la información
        codigos_dict = {}
        
        for unidad in unidades:
            codigos_dict[unidad.codigo_barras] = {
                "vencimiento": unidad.fecha_vencimiento,
                "estado": unidad.estado,
                "observaciones": unidad.observaciones or "",
                "fecha_ingreso": unidad.fecha_ingreso,
                "id_unidad": unidad.id
            }
            
        return codigos_dict
        
    except Exception as e:
        print(f"Error al obtener códigos del producto {producto_id}: {e}")
        return {}
    finally:
        session.close()


def obtener_codigos_activos_por_producto(producto_id):
    """
    Versión simplificada que solo retorna códigos de barras activos.
    
    Args:
        producto_id (int): ID del producto a buscar
        
    Returns:
        dict: Diccionario solo con unidades activas
              Formato: {"codigo_barras": "vencimiento"}
    """
    codigos_completos = obtener_codigos_por_producto(producto_id)
    
    # Filtrar solo los activos y simplificar el formato
    codigos_activos = {}
    for codigo, info in codigos_completos.items():
        if info["estado"] == "activo":
            codigos_activos[codigo] = info["vencimiento"]
    
    return codigos_activos


# Función adicional para debugging/testing
def mostrar_codigos_producto(producto_id):
    """
    Función de utilidad para mostrar en consola todos los códigos de un producto.
    Útil para debugging y testing.
    """
    codigos = obtener_codigos_por_producto(producto_id)
    
    if not codigos:
        print(f"No se encontraron códigos para el producto ID: {producto_id}")
        return
    
    print(f"\n=== CÓDIGOS DEL PRODUCTO ID: {producto_id} ===")
    for codigo, info in codigos.items():
        venc = info["vencimiento"] or "Sin vencimiento"
        estado = info["estado"]
        obs = info["observaciones"] or "Sin observaciones"
        print(f"Código: {codigo}")
        print(f"  └─ Estado: {estado}")
        print(f"  └─ Vencimiento: {venc}")
        print(f"  └─ Observaciones: {obs}")
        print(f"  └─ ID Unidad: {info['id_unidad']}")
        print("")