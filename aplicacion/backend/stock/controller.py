from aplicacion.backend.stock.utils import calcular_precio_con_margen, redondear_precio, clasificar_producto_por_unidad, calcular_margen_con_precio
from aplicacion.backend.stock import crud

def agregar_producto_controller(data):
    data["es_divisible"] = clasificar_producto_por_unidad(data.get("unidad_medida", ""))

    if data.get("costo_unitario") is not None and data.get("margen_ganancia") is not None:
        precio = calcular_precio_con_margen(data["costo_unitario"], data["margen_ganancia"])
        data["precio_venta"] = precio

        if data.get("usa_redondeo"):
            data["precio_redondeado"] = redondear_precio(precio)
        else:
            data["precio_redondeado"] = precio

    return crud.crear_producto(data)

def editar_producto_controller(id_producto, data):
    if "unidad_medida" in data:
        data["es_divisible"] = clasificar_producto_por_unidad(data["unidad_medida"])

    if "costo_unitario" in data or "margen_ganancia" in data or "precio_venta" in data:
        producto_actual = crud.obtener_producto(id_producto)
        costo = data.get("costo_unitario", producto_actual.costo_unitario)
        margen = data.get("margen_ganancia", producto_actual.margen_ganancia)
        precio = data.get("precio_venta", producto_actual.precio_venta)

        if "precio_venta" in data and "margen_ganancia" not in data:
            margen = calcular_margen_con_precio(costo, precio)
            data["margen_ganancia"] = margen

        elif "costo_unitario" in data and "margen_ganancia" not in data:
            margen = calcular_margen_con_precio(costo, precio)
            data["margen_ganancia"] = margen

        if "margen_ganancia" in data and "precio_venta" not in data:
            precio = calcular_precio_con_margen(costo, margen)
            data["precio_venta"] = precio

        data["precio_redondeado"] = redondear_precio(precio)

    crud.actualizar_producto(id_producto, data)

    return crud.obtener_producto(id_producto)

def eliminar_producto_controller(id_producto):
    return crud.eliminar_producto(id_producto)

def obtener_producto_controller(id_producto):
    return crud.obtener_producto(id_producto)

def listar_productos_controller():
    return crud.obtener_todos_productos()

def agregar_proveedor_controller(data):
    return crud.crear_proveedor(data)

def obtener_proveedor_controller(id_proveedor):
    return crud.obtener_proveedor(id_proveedor)

def listar_proveedores_controller():
    return crud.obtener_todos_proveedores()

def agregar_clasificacion_controller(data):
    return crud.crear_clasificacion(data)

def obtener_clasificacion_controller(id_categoria):
    return crud.obtener_clasificacion(id_categoria)

def listar_clasificaciones_controller():
    return crud.obtener_todas_clasificaciones()

def asignar_producto_a_categoria_controller(id_producto, id_categoria):
    return crud.asignar_producto_a_categoria(id_producto, id_categoria)

def quitar_categoria_a_producto_controller(id_producto):
    return crud.quitar_categoria_a_producto(id_producto)

def crear_categoria_sin_categoria_controller():
    return crud.crear_categoria_sin_categoria()

def agregar_unidad_controller(data):
    return crud.crear_unidad({
        "producto_id": data.get("producto_id"),
        "codigo_barras": data.get("codigo_barras"),
        "estado": "activo",
        "fecha_ingreso": data.get("fecha_ingreso"),
        "fecha_modificacion": data.get("fecha_modificacion"),
        "fecha_vencimiento": data.get("fecha_vencimiento"),
        "observaciones": data.get("observaciones")
    })

def agregar_stock_controller(id_producto, cantidad):
    return crud.agregar_stock(id_producto, cantidad)

def obtener_unidades_de_producto_controller(producto_id):
    return crud.obtener_unidades_por_producto(producto_id)

def limpiar_unidades_fantasma_controller(producto_id):
    return crud.limpiar_unidades_fantasma(producto_id)

def modificar_stock_controller(id_producto, cantidad):
    return crud.agregar_stock(id_producto, cantidad)

def limpiar_unidades_vencidas_controller():
    return crud.eliminar_unidades_vencidas()

def actualizar_fecha_vencimiento_unidad_controller(id_unidad, nueva_fecha):
    try:
        return crud.actualizar_fecha_vencimiento_unidad(id_unidad, nueva_fecha)
    except Exception as e:
        print(f"Error en controller al actualizar fecha de vencimiento: {e}")
        return False

def actualizar_fechas_vencimiento_lote_controller(cambios_lote):
    try:
        return crud.actualizar_fechas_vencimiento_lote(cambios_lote)
    except Exception as e:
        print(f"Error en controller al actualizar lote de fechas: {e}")
        return {
            "exitosos": 0,
            "fallidos": len(cambios_lote) if cambios_lote else 0,
            "errores": [f"Error critico en controller: {e}"]
        }