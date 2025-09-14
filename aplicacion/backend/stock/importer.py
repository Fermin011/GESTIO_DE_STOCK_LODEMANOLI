def convertir_a_float(valor):
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"No se pudo convertir a float: {valor}")


import csv
import pandas as pd
from aplicacion.backend.stock.controller import agregar_producto_controller
import random
from sqlalchemy import text
from aplicacion.backend.database.database import SessionLocal
from datetime import datetime
from collections import defaultdict

ruta_csv = "aplicacion/backend/temp/big/stock.csv"

def generar_codigo_barras_existente(session):
    while True:
        codigo = str(random.randint(1000000000000, 9999999999999))
        existe = session.execute(
            text("SELECT 1 FROM stock_unidades WHERE codigo_barras = :codigo"),
            {"codigo": codigo}
        ).first()
        if not existe:
            return codigo


# ---- Utilidades de normalización ----
import unicodedata

def normalizar_texto(texto):
    if texto is None:
        return ""
    texto = str(texto).strip().lower()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto

def obtener_clave_normalizada(nombre, unidad_medida, costo_unitario, usa_redondeo, proveedor_id, categoria_id, precio_venta, margen_ganancia):
    # Todos los campos relevantes, normalizados, para usar como clave hashable (tuple)
    return (
        normalizar_texto(nombre),
        normalizar_texto(unidad_medida),
        round(float(costo_unitario), 4) if costo_unitario is not None and costo_unitario != "" else None,
        bool(usa_redondeo),
        int(proveedor_id) if proveedor_id not in (None, "") else None,
        int(categoria_id) if categoria_id not in (None, "") else None,
        round(float(precio_venta), 2) if precio_venta not in (None, "") else None,
        round(float(margen_ganancia), 4) if margen_ganancia not in (None, "") else None,
    )

def cargar_productos_desde_csv():
    global ruta_csv
    exitosos = 0
    fallidos = 0
    fallidos_detalle = []  # Para trackear qué falló
    productos_dict = {}
    unidades_dict = []
    codigos_usados = set()  # Para trackear códigos ya usados en esta sesión

    print("\n" + "="*50)
    print("INICIANDO IMPORTACIÓN DE CSV")
    print("="*50)

    # 1. Leer CSV y limpiar columnas
    with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
        lector = csv.DictReader(csvfile)
        filas = []
        for fila in lector:
            if "cantidad" in fila:
                del fila["cantidad"]
            filas.append(fila)
    
    print(f"→ Filas a procesar: {len(filas)}")

    # 2. Obtener códigos existentes en la BD
    session = SessionLocal()
    try:
        existentes = session.execute(
            text("SELECT codigo_barras FROM stock_unidades")
        ).fetchall()
        for (codigo,) in existentes:
            if codigo:
                codigos_usados.add(codigo)
        print(f"→ Códigos de barras existentes en BD: {len(codigos_usados)}")
    finally:
        session.close()

    # 3. Normalizar textos y crear claves únicas de producto
    print("\nProcesando productos...")
    productos_kg = 0
    productos_unidad = 0
    
    for idx, fila in enumerate(filas, start=1):
        try:
            nombre = fila.get("nombre", "").strip()
            if not nombre:  # Si no hay nombre, saltar
                print(f"[SKIP] Fila {idx}: Sin nombre de producto")
                fallidos += 1
                fallidos_detalle.append(f"Fila {idx}: Sin nombre")
                continue
                
            # Determinar unidad_medida automáticamente basándose en el nombre
            # Si el nombre contiene "x kg" o "xkg" (a granel), es kg, sino es unidad
            nombre_upper = nombre.upper()
            # Buscar patrones que indican venta por kg (a granel)
            if "XKG" in nombre_upper or "X KG" in nombre_upper or "X  KG" in nombre_upper or "X   KG" in nombre_upper:
                unidad_medida = "kg"
                productos_kg += 1
            else:
                unidad_medida = "unidad"
                productos_unidad += 1
            
            # Valores por defecto mejorados
            costo_unitario = fila.get("costo_unitario", "")
            precio_venta = fila.get("precio_venta", "")
            margen_ganancia = fila.get("margen_ganancia", "")
            
            # Convertir a float con valores por defecto
            try:
                costo_unitario_f = float(costo_unitario) if costo_unitario not in (None, "", "nan", "NaN") else 0.0
            except (ValueError, TypeError):
                costo_unitario_f = 0.0
                
            try:
                precio_venta_f = float(precio_venta) if precio_venta not in (None, "", "nan", "NaN") else None
            except (ValueError, TypeError):
                precio_venta_f = None
                
            try:
                margen_ganancia_f = float(margen_ganancia) if margen_ganancia not in (None, "", "nan", "NaN") else None
                # Si el margen viene como porcentaje entero (ej: 48 en vez de 0.48)
                if margen_ganancia_f is not None and margen_ganancia_f > 1:
                    margen_ganancia_f = margen_ganancia_f / 100
            except (ValueError, TypeError):
                margen_ganancia_f = None

            # MANEJO ESPECIAL PARA MARGEN = 100%
            if margen_ganancia_f is not None and margen_ganancia_f >= 1.0:
                # Si el margen es 100% o más, usar una lógica diferente
                if margen_ganancia_f == 1.0:
                    # Margen del 100% significa precio = costo * 2
                    if precio_venta_f is None and costo_unitario_f > 0:
                        precio_venta_f = costo_unitario_f * 2
                    margen_ganancia_f = 0.5  # Ajustar a 50% para evitar división por 0
                else:
                    # Margen > 100% no tiene sentido, ajustar a 50%
                    margen_ganancia_f = 0.5
                    if precio_venta_f is None and costo_unitario_f > 0:
                        precio_venta_f = costo_unitario_f * 2

            # Convertir usa_redondeo de forma más robusta
            usa_redondeo_str = str(fila.get("usa_redondeo", "false")).strip().lower()
            usa_redondeo = usa_redondeo_str in ["true", "1", "yes", "si", "sí"]
            
            # IDs con manejo de errores
            try:
                proveedor_id_str = str(fila.get("proveedor_id", "")).strip()
                proveedor_id = int(proveedor_id_str) if proveedor_id_str not in ("", "None", "nan", "NaN", "null") else None
            except (ValueError, TypeError):
                proveedor_id = None
                
            try:
                categoria_id_str = str(fila.get("categoria_id", "")).strip()
                categoria_id = int(categoria_id_str) if categoria_id_str not in ("", "None", "nan", "NaN", "null") else None
            except (ValueError, TypeError):
                categoria_id = None

            # Lógica mejorada de cálculo de precio_venta o margen_ganancia
            if margen_ganancia_f is None and precio_venta_f is not None and costo_unitario_f >= 0:
                try:
                    if precio_venta_f > 0:
                        margen_ganancia_f = round((precio_venta_f - costo_unitario_f) / precio_venta_f, 4)
                        # Validar que el margen sea razonable
                        if margen_ganancia_f < 0:
                            margen_ganancia_f = 0.0
                        elif margen_ganancia_f >= 1.0:
                            margen_ganancia_f = 0.5
                    else:
                        margen_ganancia_f = 0.0
                except (ZeroDivisionError, TypeError):
                    margen_ganancia_f = 0.0
                    
            elif precio_venta_f is None and margen_ganancia_f is not None and costo_unitario_f >= 0:
                try:
                    if margen_ganancia_f < 1.0:  # Solo si el margen es menor a 100%
                        precio_venta_f = round(costo_unitario_f / (1 - margen_ganancia_f), 2)
                    else:
                        precio_venta_f = costo_unitario_f * 2  # Si margen >= 100%, duplicar el costo
                except (ZeroDivisionError, TypeError):
                    precio_venta_f = costo_unitario_f if costo_unitario_f > 0 else 0.0
            
            # Valores por defecto finales
            if margen_ganancia_f is None:
                margen_ganancia_f = 0.0
            if precio_venta_f is None:
                precio_venta_f = costo_unitario_f if costo_unitario_f > 0 else 0.0
            
            # Validación final de valores
            costo_unitario_f = max(0.0, costo_unitario_f)  # No permitir negativos
            precio_venta_f = max(0.0, precio_venta_f)  # No permitir negativos
            margen_ganancia_f = max(0.0, min(0.99, margen_ganancia_f))  # Entre 0 y 99%

            # Crear clave única normalizada
            clave = obtener_clave_normalizada(
                nombre, unidad_medida, costo_unitario_f, usa_redondeo, 
                proveedor_id, categoria_id, precio_venta_f, margen_ganancia_f
            )
            
            # Agregar o actualizar producto en productos_dict
            if clave not in productos_dict:
                productos_dict[clave] = {
                    "nombre": nombre,
                    "unidad_medida": unidad_medida,
                    "costo_unitario": costo_unitario_f,
                    "precio_venta": precio_venta_f,
                    "margen_ganancia": margen_ganancia_f,
                    "usa_redondeo": usa_redondeo,
                    "proveedor_id": proveedor_id,
                    "categoria_id": categoria_id,
                    "cantidad": 1
                }
            else:
                productos_dict[clave]["cantidad"] += 1

            # Procesar código de barras
            codigo_barras = str(fila.get("codigo_barras", "")).strip()
            if codigo_barras in ["", "None", "nan", "NaN", "null"]:
                codigo_barras = ""
                
            # Procesar vencimiento con valor por defecto
            vencimiento = str(fila.get("vencimiento", "")).strip()
            if vencimiento in ["", "None", "nan", "NaN", "null"]:
                vencimiento = "2030-12-12"  # Fecha por defecto
            
            # Añadir unidad individual a unidades_dict
            unidades_dict.append({
                "clave": clave,
                "codigo_barras": codigo_barras,
                "vencimiento": vencimiento,
                "fila_idx": idx,
                "nombre": nombre
            })
            
        except Exception as e:
            print(f"[ERROR] Fila {idx} falló en procesamiento ({fila.get('nombre', 'Sin nombre')}): {e}")
            fallidos += 1
            fallidos_detalle.append(f"Fila {idx}: {str(e)[:50]}")

    print(f"\n→ Productos únicos identificados: {len(productos_dict)}")
    print(f"→ Productos tipo 'kg': {productos_kg}")
    print(f"→ Productos tipo 'unidad': {productos_unidad}")
    print(f"→ Unidades totales a crear: {len(unidades_dict)}")

    # 4. Registrar productos únicos
    print("\nCreando productos en la base de datos...")
    productos_creados = {}
    productos_fallidos = []
    
    for clave, data in productos_dict.items():
        try:
            data_producto = data.copy()
            # Redondeo final para insertar
            if data_producto["precio_venta"] is not None:
                data_producto["precio_venta"] = round(data_producto["precio_venta"], 2)
            if data_producto["margen_ganancia"] is not None:
                data_producto["margen_ganancia"] = round(data_producto["margen_ganancia"], 4)
            
            producto = agregar_producto_controller(data_producto)
            productos_creados[clave] = producto
            
            if len(productos_creados) % 50 == 0:
                print(f"  [{len(productos_creados)}/{len(productos_dict)}] productos creados...")
            
        except Exception as e:
            error_msg = f"Producto '{data.get('nombre', 'Sin nombre')}': {str(e)[:100]}"
            print(f"[ERROR] {error_msg}")
            productos_fallidos.append(error_msg)
            fallidos += data.get("cantidad", 1)

    print(f"✓ Productos creados exitosamente: {len(productos_creados)}")
    if productos_fallidos:
        print(f"✗ Productos que fallaron: {len(productos_fallidos)}")

    # 5. Registrar las unidades físicas
    print("\nInsertando unidades físicas...")
    session = SessionLocal()
    unidades_fallidas = []
    
    try:
        fecha_actual = datetime.now().date()
        
        for unidad in unidades_dict:
            try:
                clave = unidad["clave"]
                producto = productos_creados.get(clave)
                if not producto:
                    fallidos += 1
                    continue
                    
                codigo_barras = unidad.get("codigo_barras", "")
                
                # Generar código si está vacío o ya existe
                if not codigo_barras or codigo_barras in codigos_usados:
                    # Generar código único
                    intentos = 0
                    while intentos < 100:  # Límite de intentos
                        nuevo_codigo = generar_codigo_barras_existente(session)
                        if nuevo_codigo not in codigos_usados:
                            codigo_barras = nuevo_codigo
                            codigos_usados.add(codigo_barras)
                            break
                        intentos += 1
                    
                    if intentos >= 100:
                        print(f"[ERROR] No se pudo generar código único para fila {unidad['fila_idx']}")
                        fallidos += 1
                        unidades_fallidas.append(f"Fila {unidad['fila_idx']}: No se pudo generar código único")
                        continue
                else:
                    # Verificar si el código ya existe en BD
                    existe_codigo = session.execute(
                        text("SELECT 1 FROM stock_unidades WHERE codigo_barras = :codigo"),
                        {"codigo": codigo_barras}
                    ).first()
                    
                    if existe_codigo:
                        # Generar nuevo código
                        codigo_barras = generar_codigo_barras_existente(session)
                    
                    codigos_usados.add(codigo_barras)
                
                # Procesar fecha de vencimiento
                fecha_vencimiento_str = unidad.get("vencimiento", "2030-12-12")
                fecha_vencimiento = None
                
                try:
                    # Intentar varios formatos de fecha
                    for formato in ["%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]:
                        try:
                            fecha_vencimiento = datetime.strptime(fecha_vencimiento_str, formato).date()
                            break
                        except ValueError:
                            continue
                    
                    # Si no se pudo parsear, usar fecha por defecto
                    if fecha_vencimiento is None:
                        fecha_vencimiento = datetime(2030, 12, 12).date()
                        
                except Exception:
                    fecha_vencimiento = datetime(2030, 12, 12).date()

                # Insertar unidad
                session.execute(
                    text(
                        "INSERT INTO stock_unidades (producto_id, codigo_barras, estado, fecha_ingreso, fecha_modificacion, fecha_vencimiento) "
                        "VALUES (:producto_id, :codigo_barras, :estado, :fecha_ingreso, :fecha_modificacion, :fecha_vencimiento)"
                    ),
                    {
                        "producto_id": producto.id,
                        "codigo_barras": codigo_barras,
                        "estado": "activo",
                        "fecha_ingreso": fecha_actual,
                        "fecha_modificacion": fecha_actual,
                        "fecha_vencimiento": fecha_vencimiento
                    }
                )
                exitosos += 1
                
                if exitosos % 100 == 0:  # Commit parcial cada 100 registros
                    session.commit()
                    print(f"  [{exitosos}/{len(unidades_dict)}] unidades insertadas...")
                    
            except Exception as e:
                session.rollback()
                error_msg = f"Fila {unidad['fila_idx']} ({unidad.get('nombre', 'Sin nombre')}): {str(e)[:50]}"
                unidades_fallidas.append(error_msg)
                fallidos += 1
                
        session.commit()  # Commit final
        print(f"✓ Unidades insertadas exitosamente: {exitosos}")
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR CRÍTICO] Error en la sesión de BD: {e}")
    finally:
        session.close()

    # 6. Resumen detallado
    print("\n" + "="*50)
    print("RESUMEN DE IMPORTACIÓN")
    print("="*50)
    print(f"✓ Productos únicos creados: {len(productos_creados)}")
    print(f"✓ Unidades físicas insertadas: {exitosos}")
    print(f"✗ Fallos totales: {fallidos}")
    print(f"→ Total de filas procesadas: {len(filas)}")
    print(f"→ Tasa de éxito: {(exitosos/(len(filas))*100 if len(filas) > 0 else 0):.1f}%")
    
    if fallidos > 0:
        print("\n⚠ DETALLE DE FALLOS:")
        print(f"  - Productos que no se crearon: {len(productos_fallidos)}")
        print(f"  - Unidades que no se insertaron: {len(unidades_fallidas)}")
        
        if len(fallidos_detalle) > 0:
            print("\n  Primeros errores:")
            for error in fallidos_detalle[:10]:
                print(f"    • {error}")
                
    print("="*50)
    
# ---- Nueva función para Excel ----
def cargar_productos_desde_excel():
    """
    Carga productos desde un archivo Excel (.xlsx) ubicado en la misma carpeta que el CSV.
    """
    ruta_excel = "aplicacion/backend/temp/big/stock.xlsx"
    exitosos = 0
    fallidos = 0
    try:
        df = pd.read_excel(ruta_excel)
        # Excluir la columna "cantidad" si estuviera presente
        if "cantidad" in df.columns:
            df = df.drop(columns=["cantidad"])
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo Excel: {e}")
        return

    productos_ya_registrados = {}

    # Contar repeticiones de cada clave producto usando clave robusta
    conteo_productos = defaultdict(int)
    for _, fila in df.iterrows():
        try:
            nombre = fila["nombre"]
            unidad_medida = fila["unidad_medida"]
            costo_unitario = convertir_a_float(fila["costo_unitario"])
            precio_venta = convertir_a_float(fila["precio_venta"]) if not pd.isna(fila["precio_venta"]) else None
            margen_ganancia = convertir_a_float(fila["margen_ganancia"]) if not pd.isna(fila["margen_ganancia"]) else None
            usa_redondeo = str(fila["usa_redondeo"]).strip().lower() == "true"
            proveedor_id = int(fila["proveedor_id"]) if not pd.isna(fila["proveedor_id"]) else None
            categoria_id = int(fila["categoria_id"]) if not pd.isna(fila["categoria_id"]) else None
            # Redondeo consistente para claves
            precio_venta_r = round(precio_venta, 2) if precio_venta is not None else ""
            margen_ganancia_r = round(margen_ganancia, 4) if margen_ganancia is not None else ""
            clave_producto = f"{nombre}|{unidad_medida}|{costo_unitario}|{usa_redondeo}|{proveedor_id}|{categoria_id}|{precio_venta_r}|{margen_ganancia_r}"
            conteo_productos[clave_producto] += 1
        except Exception:
            continue

    # Primero procesar productos únicos
    for idx, fila in df.iterrows():
        try:
            nombre = fila["nombre"]
            unidad_medida = fila["unidad_medida"]
            costo_unitario = convertir_a_float(fila["costo_unitario"])
            precio_venta = convertir_a_float(fila["precio_venta"]) if not pd.isna(fila["precio_venta"]) else None
            margen_ganancia = convertir_a_float(fila["margen_ganancia"]) if not pd.isna(fila["margen_ganancia"]) else None

            # Si falta margen_ganancia pero hay costo y precio_venta => calcular margen
            if margen_ganancia is None and precio_venta is not None and costo_unitario is not None:
                try:
                    margen_ganancia = round((precio_venta - costo_unitario) / precio_venta, 4)
                except ZeroDivisionError:
                    margen_ganancia = 0.0

            # Si falta precio_venta pero hay margen y costo_unitario => calcular precio_venta
            if precio_venta is None and margen_ganancia is not None and costo_unitario is not None:
                try:
                    precio_venta = round(costo_unitario / (1 - margen_ganancia), 2)
                except ZeroDivisionError:
                    precio_venta = 0.0

            # Redondeo consistente para claves
            precio_venta_r = round(precio_venta, 2) if precio_venta is not None else ""
            margen_ganancia_r = round(margen_ganancia, 4) if margen_ganancia is not None else ""

            usa_redondeo = str(fila["usa_redondeo"]).strip().lower() == "true"
            proveedor_id = int(fila["proveedor_id"]) if not pd.isna(fila["proveedor_id"]) else None
            categoria_id = int(fila["categoria_id"]) if not pd.isna(fila["categoria_id"]) else None

            data = {
                "nombre": nombre,
                "unidad_medida": unidad_medida,
                "costo_unitario": costo_unitario,
                "precio_venta": precio_venta_r if precio_venta_r != "" else None,
                "margen_ganancia": margen_ganancia_r if margen_ganancia_r != "" else None,
                "usa_redondeo": usa_redondeo,
                "proveedor_id": proveedor_id,
                "categoria_id": categoria_id
            }

            clave_producto = f"{nombre}|{unidad_medida}|{costo_unitario}|{usa_redondeo}|{proveedor_id}|{categoria_id}|{precio_venta_r}|{margen_ganancia_r}"
            if clave_producto not in productos_ya_registrados:
                data["cantidad"] = conteo_productos[clave_producto]
                producto = agregar_producto_controller(data)
                productos_ya_registrados[clave_producto] = producto

        except Exception as e:
            print(f"[ERROR] Fila {idx + 1} falló en procesamiento de producto ({fila.get('nombre', 'Sin nombre')}): {e}")
            fallidos += 1

    # Ahora insertar unidades físicas
    session = SessionLocal()
    try:
        fecha_actual = datetime.now().date()
        for idx, fila in df.iterrows():
            try:
                nombre = fila["nombre"]
                unidad_medida = fila["unidad_medida"]
                costo_unitario = convertir_a_float(fila["costo_unitario"])
                precio_venta = convertir_a_float(fila["precio_venta"]) if not pd.isna(fila["precio_venta"]) else None
                margen_ganancia = convertir_a_float(fila["margen_ganancia"]) if not pd.isna(fila["margen_ganancia"]) else None
                # Redondeo consistente para claves
                precio_venta_r = round(precio_venta, 2) if precio_venta is not None else ""
                margen_ganancia_r = round(margen_ganancia, 4) if margen_ganancia is not None else ""
                usa_redondeo = str(fila["usa_redondeo"]).strip().lower() == "true"
                proveedor_id = int(fila["proveedor_id"]) if not pd.isna(fila["proveedor_id"]) else None
                categoria_id = int(fila["categoria_id"]) if not pd.isna(fila["categoria_id"]) else None

                clave_producto = f"{nombre}|{unidad_medida}|{costo_unitario}|{usa_redondeo}|{proveedor_id}|{categoria_id}|{precio_venta_r}|{margen_ganancia_r}"
                producto = productos_ya_registrados.get(clave_producto)
                if not producto:
                    fallidos += 1
                    continue

                codigo_barras = str(fila["codigo_barras"]).strip() if "codigo_barras" in fila else ""
                fecha_vencimiento = None
                if "fecha_vencimiento" in fila and not pd.isna(fila["fecha_vencimiento"]):
                    fecha_vencimiento_val = fila["fecha_vencimiento"]
                    if isinstance(fecha_vencimiento_val, pd.Timestamp):
                        fecha_vencimiento = fecha_vencimiento_val.date()
                    else:
                        try:
                            fecha_vencimiento = datetime.strptime(str(fecha_vencimiento_val), "%Y-%m-%d").date()
                        except Exception:
                            fecha_vencimiento = None

                # Validar que el codigo_barras no esté repetido o vacío
                if not codigo_barras:
                    codigo_barras = generar_codigo_barras_existente(session)
                else:
                    existe_codigo = session.execute(
                        text("SELECT 1 FROM stock_unidades WHERE codigo_barras = :codigo"),
                        {"codigo": codigo_barras}
                    ).first()
                    if existe_codigo:
                        codigo_barras = generar_codigo_barras_existente(session)

                session.execute(
                    text(
                        "INSERT INTO stock_unidades (producto_id, codigo_barras, fecha_ingreso, fecha_modificacion, fecha_vencimiento) "
                        "VALUES (:producto_id, :codigo_barras, :fecha_ingreso, :fecha_modificacion, :fecha_vencimiento)"
                    ),
                    {
                        "producto_id": producto.id,
                        "codigo_barras": codigo_barras,
                        "fecha_ingreso": fecha_actual,
                        "fecha_modificacion": fecha_actual,
                        "fecha_vencimiento": fecha_vencimiento
                    }
                )
                exitosos += 1
                print(f"[OK] Fila {idx + 1} cargada correctamente: {nombre}")
            except Exception as e:
                session.rollback()
                nombre_fila = fila["nombre"] if "nombre" in fila else "Sin nombre"
                print(f"[ERROR] Fila {idx + 1} falló en inserción de unidad ({nombre_fila}): {e}")
                fallidos += 1
        session.commit()
    finally:
        session.close()

    print(f"\nResumen:")
    print(f"- Productos creados: {len(productos_ya_registrados)}")
    print(f"- Unidades físicas insertadas: {exitosos}")
    print(f"- Fallos en inserción de unidades: {fallidos}")
    
# ----- GENERACIÓN MASIVA DE CSV DE STOCK -----
import csv
import os

def generar_csv_stock_masivo(productos, ruta='aplicacion/backend/temp/big/stock_g.csv'):
    """
    Genera un archivo CSV con los datos de productos proporcionados.

    Parámetros:
    - productos: lista de diccionarios con los campos:
        nombre, unidad_medida, costo_unitario, margen_ganancia,
        precio_venta, usa_redondeo, proveedor_id, categoria_id
    - ruta: ruta donde se guardará el archivo CSV
    """
    campos = [
        'nombre',
        'unidad_medida',
        'costo_unitario',
        'precio_venta',
        'margen_ganancia',
        'usa_redondeo',
        'proveedor_id',
        'categoria_id',
        'codigo_barras',
        'vencimiento'
    ]

    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    with open(ruta, mode='w', newline='', encoding='utf-8') as archivo_csv:
        writer = csv.DictWriter(archivo_csv, fieldnames=campos)
        writer.writeheader()
        for producto in productos:
            if (
                producto.get("margen_ganancia") in (None, "") and
                producto.get("precio_venta") not in (None, "") and
                producto.get("costo_unitario") not in (None, "")
            ):
                try:
                    costo = float(producto["costo_unitario"])
                    precio = float(producto["precio_venta"])
                    producto["margen_ganancia"] = round((precio - costo) / precio, 4)
                except (ValueError, ZeroDivisionError):
                    producto["margen_ganancia"] = 0.0

            if (
                producto.get("precio_venta") in (None, "") and
                producto.get("costo_unitario") not in (None, "") and
                producto.get("margen_ganancia") not in (None, "")
            ):
                try:
                    costo = float(producto["costo_unitario"])
                    margen = float(producto["margen_ganancia"])
                    producto["precio_venta"] = round(costo / (1 - margen), 2)
                except (ValueError, ZeroDivisionError):
                    producto["precio_venta"] = 0.0
            # Eliminar el campo 'cantidad' si existe antes de escribir
            if "cantidad" in producto:
                del producto["cantidad"]
            writer.writerow(producto)