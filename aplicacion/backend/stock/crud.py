from sqlalchemy.orm import sessionmaker
from aplicacion.backend.database.database import engine, Producto, Proveedor, StockClasificacion, StockUnidad
from sqlalchemy import func
from datetime import datetime, timedelta
import os
import json
import tempfile

Session = sessionmaker(bind=engine)

def crear_producto(data):
    session = Session()
    nuevo = Producto(**data)
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    session.close()
    return nuevo

def obtener_producto(id_producto):
    session = Session()
    producto = session.query(Producto).filter_by(id=id_producto).first()
    session.close()
    return producto

def obtener_todos_productos():
    session = Session()
    productos = session.query(Producto).all()
    session.close()
    return productos

def actualizar_producto(id_producto, data):
    session = Session()
    producto = session.query(Producto).filter_by(id=id_producto).first()
    if producto:
        for key, value in data.items():
            setattr(producto, key, value)
        session.commit()
    session.close()
    return producto

def eliminar_producto(id_producto):
    session = Session()
    producto = session.query(Producto).filter_by(id=id_producto).first()
    if producto:
        session.delete(producto)
        session.commit()
    session.close()
    return producto

def crear_proveedor(data):
    session = Session()
    nuevo = Proveedor(
        nombre=data.get("nombre"),
        contacto=data.get("contacto", ""),
        direccion=data.get("direccion", ""),
        telefono=data.get("telefono", ""),
        email=data.get("email", "")
    )
    session.add(nuevo)
    session.commit()
    session.refresh(nuevo)
    session.close()
    return nuevo

def obtener_proveedor(id_proveedor):
    session = Session()
    proveedor = session.query(Proveedor).filter_by(id=id_proveedor).first()
    session.close()
    return proveedor

def obtener_todos_proveedores():
    session = Session()
    proveedores = session.query(Proveedor).all()
    session.close()
    return proveedores

def actualizar_proveedor(id_proveedor, data):
    session = Session()
    proveedor = session.query(Proveedor).filter_by(id=id_proveedor).first()
    if proveedor:
        for key, value in data.items():
            setattr(proveedor, key, value)
        session.commit()
    session.close()
    return proveedor

def eliminar_proveedor(id_proveedor):
    session = Session()
    proveedor = session.query(Proveedor).filter_by(id=id_proveedor).first()
    if proveedor:
        session.delete(proveedor)
        session.commit()
    session.close()
    return proveedor

def crear_clasificacion(data):
    session = Session()
    nueva = StockClasificacion(**data)
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    session.close()
    return nueva

def obtener_clasificacion(id_categoria):
    session = Session()
    categoria = session.query(StockClasificacion).filter_by(id=id_categoria).first()
    session.close()
    return categoria

def obtener_todas_clasificaciones():
    session = Session()
    categorias = session.query(StockClasificacion).all()
    session.close()
    return categorias

def actualizar_clasificacion(id_categoria, data):
    session = Session()
    categoria = session.query(StockClasificacion).filter_by(id=id_categoria).first()
    if categoria:
        for key, value in data.items():
            setattr(categoria, key, value)
        session.commit()
    session.close()
    return categoria

def eliminar_clasificacion(id_categoria):
    session = Session()
    categoria = session.query(StockClasificacion).filter_by(id=id_categoria).first()
    if categoria:
        session.delete(categoria)
        session.commit()
    session.close()
    return categoria

def crear_unidad(data):
    session = Session()
    nueva = StockUnidad(
        producto_id=data.get("producto_id"),
        codigo_barras=data.get("codigo_barras"),
        fecha_ingreso=data.get("fecha_ingreso"),
        fecha_modificacion=data.get("fecha_modificacion"),
        fecha_vencimiento=data.get("fecha_vencimiento"),
        observaciones=data.get("observaciones")
    )
    session.add(nueva)
    session.commit()
    session.refresh(nueva)
    session.close()
    return nueva

def obtener_unidad(id_unidad):
    session = Session()
    unidad = session.query(StockUnidad).filter_by(id=id_unidad).first()
    session.close()
    return unidad

def obtener_todas_unidades():
    session = Session()
    unidades = session.query(StockUnidad).all()
    session.close()
    return unidades

def obtener_unidades_por_producto(producto_id):
    session = Session()
    unidades = session.query(StockUnidad).filter_by(producto_id=producto_id).all()
    session.close()
    return unidades

def actualizar_unidad(id_unidad, data):
    session = Session()
    unidad = session.query(StockUnidad).filter_by(id=id_unidad).first()
    if unidad:
        for key, value in data.items():
            setattr(unidad, key, value)
        session.commit()
    session.close()
    return unidad

def eliminar_unidad(id_unidad):
    session = Session()
    unidad = session.query(StockUnidad).filter_by(id=id_unidad).first()
    if unidad:
        session.delete(unidad)
        session.commit()
    session.close()
    return unidad

def asignar_producto_a_categoria(id_producto, id_categoria):
    session = Session()
    producto = session.query(Producto).filter_by(id=id_producto).first()
    if producto:
        producto.categoria_id = id_categoria
        session.commit()
    session.close()
    return producto

def quitar_categoria_a_producto(id_producto):
    session = Session()
    producto = session.query(Producto).filter_by(id=id_producto).first()
    if producto:
        producto.categoria_id = None
        session.commit()
    session.close()
    return producto

def crear_categoria_sin_categoria():
    session = Session()
    existente = session.query(StockClasificacion).filter_by(nombre="Sin categoria").first()
    if not existente:
        sin_cat = StockClasificacion(
            nombre="Sin categoria",
            descripcion="Clasificacion por defecto para productos sin categoria.",
            activa=True
        )
        session.add(sin_cat)
        session.commit()
        session.refresh(sin_cat)
        session.close()
        return sin_cat
    session.close()
    return existente

def obtener_unidades_vencidas():
    session = Session()
    try:
        hoy = datetime.now().date().isoformat()
        
        resultados = session.query(
            StockUnidad.id,
            StockUnidad.codigo_barras,
            StockUnidad.fecha_vencimiento,
            StockUnidad.estado,
            Producto.nombre,
            StockClasificacion.nombre.label('categoria_nombre')
        ).join(
            Producto, StockUnidad.producto_id == Producto.id
        ).outerjoin(
            StockClasificacion, Producto.categoria_id == StockClasificacion.id
        ).filter(
            StockUnidad.fecha_vencimiento != None,
            StockUnidad.fecha_vencimiento <= hoy
        ).all()
        
        unidades_vencidas = []
        hoy_date = datetime.now().date()
        
        for row in resultados:
            try:
                fecha_venc_obj = datetime.strptime(row.fecha_vencimiento, "%Y-%m-%d").date()
                dias_restantes = (fecha_venc_obj - hoy_date).days
            except:
                dias_restantes = None
            
            unidades_vencidas.append({
                "codigo": str(row.codigo_barras or ""),
                "nombre": str(row.nombre or ""),
                "categoria": str(row.categoria_nombre or "Sin categoria"),
                "fecha_venc": str(row.fecha_vencimiento or ""),
                "dias_rest": dias_restantes,
                "estado": "VENCIDO"
            })
        
        return unidades_vencidas
        
    finally:
        session.close()

def obtener_unidades_por_vencer(dias_limite=10):
    session = Session()
    try:
        hoy = datetime.now().date()
        limite = hoy + timedelta(days=dias_limite)
        hoy_str = hoy.isoformat()
        limite_str = limite.isoformat()
        
        resultados = session.query(
            StockUnidad.id,
            StockUnidad.codigo_barras,
            StockUnidad.fecha_vencimiento,
            StockUnidad.estado,
            Producto.nombre,
            StockClasificacion.nombre.label('categoria_nombre')
        ).join(
            Producto, StockUnidad.producto_id == Producto.id
        ).outerjoin(
            StockClasificacion, Producto.categoria_id == StockClasificacion.id
        ).filter(
            StockUnidad.fecha_vencimiento != None,
            StockUnidad.fecha_vencimiento > hoy_str,
            StockUnidad.fecha_vencimiento <= limite_str
        ).all()
        
        unidades_por_vencer = []
        
        for row in resultados:
            try:
                fecha_venc_obj = datetime.strptime(row.fecha_vencimiento, "%Y-%m-%d").date()
                dias_restantes = (fecha_venc_obj - hoy).days
            except:
                dias_restantes = None
            
            unidades_por_vencer.append({
                "codigo": row.codigo_barras or "",
                "nombre": row.nombre or "",
                "categoria": row.categoria_nombre or "Sin categoria",
                "fecha_venc": row.fecha_vencimiento or "",
                "dias_rest": dias_restantes,
                "estado": "POR VENCER"
            })
        
        return unidades_por_vencer
        
    finally:
        session.close()

def agregar_stock(id_producto, cantidad):
    session = Session()
    try:
        producto = session.query(Producto).filter_by(id=id_producto).first()
        if not producto:
            return None
        
        stock_actual = producto.cantidad if producto.cantidad is not None else 0
        nuevo_stock = stock_actual + cantidad
        
        if nuevo_stock < 0:
            raise ValueError(f"No se puede reducir el stock. Stock actual: {stock_actual}, cantidad a restar: {abs(cantidad)}. Esto resultaria en stock negativo ({nuevo_stock}).")
        
        producto.cantidad = nuevo_stock
        
        if producto.es_divisible:
            print(f"Producto divisible ({producto.unidad_medida}): Stock actualizado a {nuevo_stock}")
        else:
            if cantidad > 0:
                cantidad_agregar = int(cantidad)
                print(f"Agregando {cantidad_agregar} unidades fisicas para '{producto.nombre}'")
                
                from datetime import datetime
                fecha_actual = datetime.now().isoformat()
                
                from aplicacion.backend.stock.utils import generar_codigo_barras
                
                for i in range(cantidad_agregar):
                    codigo_barras = generar_codigo_barras()
                    
                    while session.query(StockUnidad).filter_by(codigo_barras=codigo_barras).first():
                        codigo_barras = generar_codigo_barras()
                    
                    nueva_unidad = StockUnidad(
                        producto_id=producto.id,
                        codigo_barras=codigo_barras,
                        estado="activo",
                        fecha_ingreso=fecha_actual,
                        fecha_modificacion=fecha_actual,
                        fecha_vencimiento=None,
                        observaciones="Unidad agregada por incremento de stock"
                    )
                    session.add(nueva_unidad)
                    print(f"  Unidad {i+1}/{cantidad_agregar}: {codigo_barras}")
                
            elif cantidad < 0:
                cantidad_restar = int(abs(cantidad))
                print(f"Restando {cantidad_restar} unidades fisicas para '{producto.nombre}'")
                
                unidades_activas = session.query(StockUnidad).filter_by(
                    producto_id=producto.id, 
                    estado="activo"
                ).order_by(StockUnidad.fecha_ingreso.desc()).limit(cantidad_restar).all()
                
                if len(unidades_activas) < cantidad_restar:
                    print(f"Advertencia: Solo hay {len(unidades_activas)} unidades fisicas activas, pero se intentan restar {cantidad_restar}")
                
                from datetime import datetime
                fecha_actual = datetime.now().isoformat()
                
                for i, unidad in enumerate(unidades_activas):
                    unidad.estado = "inactivo"
                    unidad.fecha_modificacion = fecha_actual
                    unidad.observaciones = f"Unidad desactivada por reduccion de stock - {unidad.observaciones or ''}"
                    print(f"  Desactivada unidad {i+1}/{len(unidades_activas)}: {unidad.codigo_barras}")
        
        session.commit()
        session.refresh(producto)
        
        if nuevo_stock == 0:
            limpiar_unidades_fantasma(id_producto)
        
        print(f"Stock actualizado exitosamente: {producto.nombre} -> {nuevo_stock} {producto.unidad_medida}")
        return producto
        
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar stock: {e}")
        raise e
    finally:
        session.close()

def limpiar_unidades_fantasma(producto_id):
    session = Session()
    try:
        producto = session.query(Producto).filter_by(id=producto_id).first()
        if producto and producto.cantidad == 0:
            unidades_activas = session.query(StockUnidad).filter_by(
                producto_id=producto_id, estado="activo"
            ).all()
            for unidad in unidades_activas:
                unidad.estado = "inactivo"
                unidad.fecha_modificacion = datetime.now()
            session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

def formatear_moneda(valor):
    if valor is None:
        return "$0,00"
    
    try:
        valor = float(valor)
    except (ValueError, TypeError):
        return "$0,00"
    
    formatted = f"{valor:,.2f}"
    
    parts = formatted.split('.')
    if len(parts) == 2:
        entero = parts[0].replace(',', '.')
        decimal = parts[1]
        formatted = f"{entero},{decimal}"
    else:
        formatted = formatted.replace(',', '.') + ",00"
    
    return f"${formatted}"

def obtener_productos_json():
    session = Session()
    try:
        productos = session.query(Producto).all()
        
        resultado = []
        
        for producto in productos:
            if producto.categoria_id and producto.clasificacion:
                categoria = producto.clasificacion.nombre
            else:
                categoria = "sin_categoria"
            
            estado = "activo" if producto.cantidad > 0 else "no disponible"
            
            costo = producto.costo_unitario if producto.costo_unitario is not None else 0
            precio = producto.precio_redondeado if producto.precio_redondeado is not None else 0
            cantidad = producto.cantidad if producto.cantidad is not None else 0
            margen = producto.margen_ganancia
            
            es_divisible = False
            if hasattr(producto, 'unidad_medida') and producto.unidad_medida:
                es_divisible = producto.unidad_medida == "kilogramos"
            elif hasattr(producto, 'es_divisible'):
                es_divisible = producto.es_divisible
            
            ganancia_bruta_unitaria = precio
            ganancia_neta_unitaria = precio - costo
            ganancia_bruta_total = precio * cantidad
            ganancia_neta_total = (precio - costo) * cantidad
            
            producto_dict = {
                "id": producto.id,
                "nombre": producto.nombre,
                "categoria": categoria,
                "stock": cantidad,
                "costo": formatear_moneda(costo),
                "precio": formatear_moneda(precio),
                "estado": estado,
                "margen": margen,
                "ganancia_bruta_unitaria": formatear_moneda(ganancia_bruta_unitaria),
                "ganancia_neta_unitaria": formatear_moneda(ganancia_neta_unitaria),
                "ganancia_bruta_total": formatear_moneda(ganancia_bruta_total),
                "ganancia_neta_total": formatear_moneda(ganancia_neta_total),
                "es_divisible": es_divisible
            }
            
            resultado.append(producto_dict)
        
        return resultado
        
    except Exception as e:
        print(f"Error al obtener productos JSON: {e}")
        return []
    finally:
        session.close()

def exportar_productos_json():
    try:
        productos = obtener_productos_json()

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        json_dir = os.path.join(base_dir, "frontend", "json")
        archivo_path = os.path.join(json_dir, "stock.json")

        os.makedirs(json_dir, exist_ok=True)

        if os.path.exists(archivo_path):
            try:
                os.remove(archivo_path)
                print("Archivo existente stock.json eliminado.")
            except Exception as e:
                print(f"No se pudo eliminar el stock.json existente: {e}")
                return False

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=json_dir, delete=False) as tmp:
            json.dump(productos, tmp, ensure_ascii=False, indent=4)
            tmp_path = tmp.name

        os.replace(tmp_path, archivo_path)

        print(f"Productos exportados exitosamente a {archivo_path}")
        return True

    except Exception as e:
        print(f"Error al exportar productos a JSON: {e}")
        return False
    
def obtener_categorias_json():
    session = Session()
    try:
        categorias = session.query(StockClasificacion).filter_by(activa=True).all()
        
        resultado = []
        
        for categoria in categorias:
            categoria_dict = {
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion if categoria.descripcion else "",
                "activa": categoria.activa
            }
            
            resultado.append(categoria_dict)
        
        return resultado
        
    except Exception as e:
        print(f"Error al obtener categorias JSON: {e}")
        return []
    finally:
        session.close()

def exportar_categorias_json():
    try:
        categorias = obtener_categorias_json()

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        json_dir = os.path.join(base_dir, "frontend", "json")
        archivo_path = os.path.join(json_dir, "categorias.json")

        os.makedirs(json_dir, exist_ok=True)

        if os.path.exists(archivo_path):
            try:
                os.remove(archivo_path)
                print("Archivo existente categorias.json eliminado.")
            except Exception as e:
                print(f"No se pudo eliminar el categorias.json existente: {e}")
                return False

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=json_dir, delete=False) as tmp:
            json.dump(categorias, tmp, ensure_ascii=False, indent=4)
            tmp_path = tmp.name

        os.replace(tmp_path, archivo_path)

        print(f"Categorias exportadas exitosamente a {archivo_path}")
        return True

    except Exception as e:
        print(f"Error al exportar categorias a JSON: {e}")
        return False

def obtener_proveedores_json():
    session = Session()
    try:
        proveedores = session.query(Proveedor).all()
        
        resultado = []
        
        for proveedor in proveedores:
            proveedor_dict = {
                "id": proveedor.id,
                "nombre": proveedor.nombre if proveedor.nombre else "",
                "telefono": proveedor.telefono if proveedor.telefono else "",
                "email": proveedor.email if proveedor.email else "",
                "direccion": proveedor.direccion if proveedor.direccion else "",
                "contacto": proveedor.contacto if proveedor.contacto else ""
            }
            
            resultado.append(proveedor_dict)
        
        return resultado
        
    except Exception as e:
        print(f"Error al obtener proveedores JSON: {e}")
        return []
    finally:
        session.close()

def exportar_proveedores_json():
    try:
        proveedores = obtener_proveedores_json()

        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        json_dir = os.path.join(base_dir, "frontend", "json")
        archivo_path = os.path.join(json_dir, "proveedores.json")

        os.makedirs(json_dir, exist_ok=True)

        if os.path.exists(archivo_path):
            try:
                os.remove(archivo_path)
                print("Archivo existente proveedores.json eliminado.")
            except Exception as e:
                print(f"No se pudo eliminar el proveedores.json existente: {e}")
                return False

        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=json_dir, delete=False) as tmp:
            json.dump(proveedores, tmp, ensure_ascii=False, indent=4)
            tmp_path = tmp.name

        os.replace(tmp_path, archivo_path)

        print(f"Proveedores exportados exitosamente a {archivo_path}")
        return True

    except Exception as e:
        print(f"Error al exportar proveedores a JSON: {e}")
        return False

def eliminar_unidades_vencidas():
    session = Session()
    try:
        unidades_a_eliminar = session.query(
            StockUnidad.producto_id,
            func.count(StockUnidad.id).label('cantidad')
        ).filter(
            StockUnidad.fecha_vencimiento != None,
            StockUnidad.fecha_vencimiento <= func.current_date()
        ).group_by(StockUnidad.producto_id).all()
        
        print(f"[DEBUG] Unidades vencidas por producto a eliminar: {[(p_id, cant) for p_id, cant in unidades_a_eliminar]}")
        
        borrados = (
            session.query(StockUnidad)
            .filter(
                StockUnidad.fecha_vencimiento != None,
                StockUnidad.fecha_vencimiento <= func.current_date()
            )
            .delete(synchronize_session=False)
        )
        
        productos_actualizados = 0
        for producto_id, cantidad_eliminada in unidades_a_eliminar:
            producto = session.query(Producto).filter_by(id=producto_id).first()
            if producto:
                stock_anterior = producto.cantidad or 0
                nueva_cantidad = max(0, stock_anterior - cantidad_eliminada)
                producto.cantidad = nueva_cantidad
                productos_actualizados += 1
                print(f"[DEBUG] Producto ID {producto_id} '{producto.nombre}': stock {stock_anterior} -> {nueva_cantidad} (eliminadas: {cantidad_eliminada})")
        
        session.commit()
        
        print(f"[INFO] Eliminadas {borrados} unidades vencidas de {productos_actualizados} productos diferentes")
        return borrados
        
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Error al eliminar unidades vencidas: {e}")
        raise e
    finally:
        session.close()
        
def actualizar_fecha_vencimiento_unidad(id_unidad, nueva_fecha):
    session = Session()
    try:
        unidad = session.query(StockUnidad).filter_by(id=id_unidad).first()
        if not unidad:
            return False
        
        if nueva_fecha and nueva_fecha.strip():
            try:
                from datetime import datetime
                datetime.strptime(nueva_fecha.strip(), '%Y-%m-%d')
                unidad.fecha_vencimiento = nueva_fecha.strip()
            except ValueError:
                raise ValueError(f"Formato de fecha invalido: {nueva_fecha}. Use YYYY-MM-DD")
        else:
            unidad.fecha_vencimiento = None
        
        unidad.fecha_modificacion = datetime.now().isoformat()
        
        session.commit()
        return True
        
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar fecha de vencimiento: {e}")
        raise e
    finally:
        session.close()

def actualizar_fechas_vencimiento_lote(cambios_lote):
    session = Session()
    resultado = {
        "exitosos": 0,
        "fallidos": 0,
        "errores": []
    }
    
    try:
        from datetime import datetime
        fecha_modificacion = datetime.now().isoformat()
        
        for cambio in cambios_lote:
            try:
                unidad_id = cambio.get("unidad_id")
                nueva_fecha = cambio.get("nueva_fecha", "").strip()
                codigo = cambio.get("codigo", "N/A")
                
                unidad = session.query(StockUnidad).filter_by(id=unidad_id).first()
                if not unidad:
                    resultado["fallidos"] += 1
                    resultado["errores"].append(f"Unidad ID {unidad_id} no encontrada")
                    continue
                
                if nueva_fecha:
                    try:
                        datetime.strptime(nueva_fecha, '%Y-%m-%d')
                        unidad.fecha_vencimiento = nueva_fecha
                    except ValueError:
                        resultado["fallidos"] += 1
                        resultado["errores"].append(f"Formato invalido para codigo {codigo}: {nueva_fecha}")
                        continue
                else:
                    unidad.fecha_vencimiento = None
                
                unidad.fecha_modificacion = fecha_modificacion
                
                resultado["exitosos"] += 1
                print(f"Actualizada unidad {unidad_id} (codigo {codigo}): {nueva_fecha or 'Sin fecha'}")
                
            except Exception as e:
                resultado["fallidos"] += 1
                error_msg = f"Error en unidad {cambio.get('unidad_id', 'N/A')}: {str(e)}"
                resultado["errores"].append(error_msg)
                print(f"Error: {error_msg}")
        
        session.commit()
        print(f"Lote procesado: {resultado['exitosos']} exitosos, {resultado['fallidos']} fallidos")
        
        return resultado
        
    except Exception as e:
        session.rollback()
        print(f"Error critico en actualizacion de lote: {e}")
        resultado["fallidos"] = len(cambios_lote)
        resultado["exitosos"] = 0
        resultado["errores"].append(f"Error critico: {e}")
        return resultado
    finally:
        session.close()