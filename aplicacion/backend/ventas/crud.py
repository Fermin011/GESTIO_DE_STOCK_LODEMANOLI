from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from datetime import datetime
from aplicacion.backend.database.database import engine, Producto, StockUnidad
from aplicacion.backend.database.database import VentaRegistro, VentaDetalle

Session = sessionmaker(bind=engine)

# Carrito global (considera moverlo a una clase o session storage en el futuro)
carrito = []

def validar_codigo_barras(codigo):
    """Valida y obtiene una unidad activa por código de barras"""
    session = Session()
    try:
        unidad = session.query(StockUnidad).filter(
            and_(StockUnidad.codigo_barras == codigo, StockUnidad.estado == "activo")
        ).first()
        return unidad
    finally:
        session.close()

def obtener_producto_por_id(producto_id):
    """Obtiene un producto por su ID"""
    session = Session()
    try:
        producto = session.query(Producto).filter_by(id=producto_id).first()
        return producto
    finally:
        session.close()

def actualizar_estado_unidad_inactivo_por_codigo(codigo_barras):
    """Marca una unidad como inactiva por código de barras"""
    session = Session()
    try:
        unidad = session.query(StockUnidad).filter_by(codigo_barras=codigo_barras).first()
        if unidad:
            unidad.estado = "inactivo"
            unidad.fecha_modificacion = datetime.now().isoformat()
            session.commit()
        return unidad
    finally:
        session.close()

def descontar_stock_producto(producto_id, cantidad=1):
    """Descuenta cantidad del stock de un producto"""
    session = Session()
    try:
        producto = session.query(Producto).filter_by(id=producto_id).first()
        if producto and producto.cantidad >= cantidad:
            producto.cantidad -= cantidad
            if producto.cantidad < 0:
                producto.cantidad = 0
            producto.ultima_modificacion = datetime.now().isoformat()
            session.commit()
            return True
        return False
    finally:
        session.close()

def agregar_producto_por_codigo_barras(codigo_barras):
    """Agrega un producto al carrito usando código de barras"""
    unidad = validar_codigo_barras(codigo_barras)
    if not unidad:
        return {"exito": False, "mensaje": "Código de barras no válido o unidad inactiva"}

    producto = obtener_producto_por_id(unidad.producto_id)
    if not producto:
        return {"exito": False, "mensaje": "Producto no encontrado"}
    
    if producto.cantidad <= 0:
        return {"exito": False, "mensaje": "Producto sin stock"}

    item_carrito = {
        "unidad_id": unidad.id,
        "producto_id": producto.id,
        "nombre": producto.nombre,
        "precio_unitario": producto.precio_redondeado,
        "codigo_barras": unidad.codigo_barras,
        "cantidad": 1,
        "tipo_venta": "codigo_barras"
    }
    
    carrito.append(item_carrito)
    return {"exito": True, "item": item_carrito, "mensaje": "Producto agregado al carrito"}

def agregar_producto_por_id(producto_id, cantidad=1):
    """Agrega un producto al carrito usando ID de producto y cantidad específica"""
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return {"exito": False, "mensaje": "Producto no encontrado"}
    
    if producto.cantidad < cantidad:
        return {"exito": False, "mensaje": f"Stock insuficiente. Disponible: {producto.cantidad}"}

    item_carrito = {
        "unidad_id": None,  # No se sabe qué unidad específica
        "producto_id": producto.id,
        "nombre": producto.nombre,
        "precio_unitario": producto.precio_redondeado,
        "codigo_barras": None,
        "cantidad": cantidad,
        "tipo_venta": "producto_id"
    }
    
    carrito.append(item_carrito)
    return {"exito": True, "item": item_carrito, "mensaje": "Producto agregado al carrito"}

def agregar_producto_a_carrito(carrito_param, codigo_barras=None, producto_kg_id=None, cantidad_kg=0, producto_id=None, cantidad=1):
    """
    Función unificada para agregar productos al carrito.
    Mantiene compatibilidad con la implementación anterior pero agrega nuevas funcionalidades.
    
    Parámetros:
    - codigo_barras: Para agregar por código de barras (cantidad = 1)
    - producto_kg_id + cantidad_kg: Para agregar productos por peso
    - producto_id + cantidad: Para agregar cualquier producto por ID
    """
    
    # Caso 1: Por código de barras
    if codigo_barras:
        resultado = agregar_producto_por_codigo_barras(codigo_barras)
        return resultado.get("item") if resultado.get("exito") else None

    # Caso 2: Por peso/kg (legacy - usando producto_id internamente)
    elif producto_kg_id and cantidad_kg > 0:
        resultado = agregar_producto_por_id(producto_kg_id, cantidad_kg)
        return resultado.get("item") if resultado.get("exito") else None

    # Caso 3: Por ID de producto
    elif producto_id:
        resultado = agregar_producto_por_id(producto_id, cantidad)
        return resultado.get("item") if resultado.get("exito") else None

    return None

def obtener_carrito():
    """Devuelve el contenido actual del carrito"""
    return carrito.copy()

def limpiar_carrito():
    """Limpia el carrito"""
    carrito.clear()

def eliminar_item_carrito(indice):
    """Elimina un item específico del carrito por índice"""
    if 0 <= indice < len(carrito):
        item_eliminado = carrito.pop(indice)
        return {"exito": True, "item": item_eliminado}
    return {"exito": False, "mensaje": "Índice inválido"}

def calcular_total_carrito():
    """Calcula el total del carrito"""
    return sum(item["precio_unitario"] * item["cantidad"] for item in carrito)

# Reemplazar el método confirmar_venta en crud.py con esta versión:

def confirmar_venta(data: dict):
    """Confirma la venta, registra en la base de datos y limpia el carrito"""
    if not carrito:
        return {"exito": False, "mensaje": "El carrito está vacío"}

    session = Session()
    try:
        # Calcular total correctamente para productos a granel
        total = 0.0
        for item in carrito:
            if item.get("es_granel", False):
                # Para productos a granel: precio_por_kilo * (gramos / 1000)
                # O directamente precio_por_kilo * cantidad_kg si ya está convertido
                if "cantidad_gramos" in item:
                    gramos = item["cantidad_gramos"]
                    subtotal = item["precio_unitario"] * (gramos / 1000.0)
                else:
                    # Si ya está en kg
                    subtotal = item["precio_unitario"] * item["cantidad"]
            else:
                # Para productos normales
                subtotal = item["precio_unitario"] * item["cantidad"]
            total += subtotal

        # Crear registro de venta
        nueva_venta = VentaRegistro(
            fecha=datetime.now().isoformat(),
            total=total,
            metodo_pago=data["metodo_pago"],
            usuario_id=data["usuario_id"]
        )
        session.add(nueva_venta)
        session.commit()
        session.refresh(nueva_venta)

        # Crear detalles de venta y actualizar stock según el tipo
        for item in carrito:
            # Calcular subtotal correctamente para el detalle
            if item.get("es_granel", False):
                if "cantidad_gramos" in item:
                    gramos = item["cantidad_gramos"]
                    subtotal = item["precio_unitario"] * (gramos / 1000.0)
                    cantidad_para_detalle = gramos / 1000.0  # Guardar en kg en el detalle
                else:
                    subtotal = item["precio_unitario"] * item["cantidad"]
                    cantidad_para_detalle = item["cantidad"]
            else:
                subtotal = item["precio_unitario"] * item["cantidad"]
                cantidad_para_detalle = item["cantidad"]

            # Crear detalle de venta
            detalle = VentaDetalle(
                venta_id=nueva_venta.id,
                unidad_id=item["unidad_id"],  # Puede ser None
                producto_id=item["producto_id"],
                cantidad=cantidad_para_detalle,  # En kg para granel, en unidades para normal
                precio_unitario=item["precio_unitario"],
                subtotal=subtotal,  # Subtotal calculado correctamente
                tipo_venta=item["tipo_venta"]
            )
            session.add(detalle)

            # Procesar según el tipo de venta
            if item["tipo_venta"] == "codigo_barras":
                # Venta por código de barras: marcar unidad específica como inactiva
                if item["codigo_barras"]:
                    actualizar_estado_unidad_inactivo_por_codigo(item["codigo_barras"])
                # Descontar 1 unidad del stock
                descontar_stock_producto(item["producto_id"], 1)
                
            elif item["tipo_venta"] == "producto_id":
                # Venta por ID: solo descontar del stock, NO tocar stock_unidades
                descontar_stock_producto(item["producto_id"], item["cantidad"])
                
            elif item["tipo_venta"] in ["granel", "granel_codigo"]:
                # Ventas a granel: descontar en kilogramos
                if "cantidad_gramos" in item:
                    cantidad_kg = item["cantidad_gramos"] / 1000.0
                else:
                    cantidad_kg = item["cantidad"]
                
                descontar_stock_producto_granel(item["producto_id"], cantidad_kg)
                
                # Si fue por código de barras, también inactivar la unidad
                if item["tipo_venta"] == "granel_codigo" and item.get("codigo_barras"):
                    actualizar_estado_unidad_inactivo_por_codigo(item["codigo_barras"])

        session.commit()
        vendidos = carrito.copy()
        limpiar_carrito()
        
        return {
            "exito": True,
            "venta_id": nueva_venta.id,
            "total": total,
            "productos": vendidos
        }
    except Exception as e:
        session.rollback()
        return {"exito": False, "mensaje": str(e)}
    finally:
        session.close()
    

def obtener_productos_por_kg():
    """Devuelve los productos que se venden por kilo con su info principal"""
    session = Session()
    try:
        productos = session.query(Producto).filter_by(unidad_medida="kg").all()
        resultado = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "cantidad": p.cantidad,
                "precio_kilo": p.precio_redondeado
            }
            for p in productos
        ]
        return resultado
    finally:
        session.close()

def obtener_todos_los_productos():
    """Devuelve todos los productos con stock disponible"""
    session = Session()
    try:
        productos = session.query(Producto).filter(Producto.cantidad > 0).all()
        resultado = [
            {
                "id": p.id,
                "nombre": p.nombre,
                "cantidad": p.cantidad,
                "precio": p.precio_redondeado,
                "unidad_medida": p.unidad_medida
            }
            for p in productos
        ]
        return resultado
    finally:
        session.close()

def cancelar_ultima_venta():
    """
    Cancela la última venta registrada:
    - Cambia estado de ventas_registro a 0 (cancelada).
    - Restaura las cantidades de los productos.
    - Reactiva las unidades en stock_unidades SOLO si fueron vendidas por código de barras.
    """
    session = Session()
    try:
        # Obtener la última venta
        ultima_venta = session.query(VentaRegistro).order_by(VentaRegistro.id.desc()).first()
        if not ultima_venta or ultima_venta.estado == 0:
            return {"exito": False, "mensaje": "No hay ventas para cancelar o ya está cancelada."}

        # Cambiar estado de la venta
        ultima_venta.estado = 0
        session.commit()

        # Obtener los detalles de la venta
        detalles = session.query(VentaDetalle).filter_by(venta_id=ultima_venta.id).all()
        restaurados = []

        for det in detalles:
            producto = session.query(Producto).filter_by(id=det.producto_id).first()
            
            if producto:
                # Restaurar stock en productos
                producto.cantidad += det.cantidad
                producto.ultima_modificacion = datetime.now().isoformat()
                
                # Si fue vendido por código de barras, reactivar la unidad específica
                if det.tipo_venta == "codigo_barras" and det.unidad_id:
                    unidad = session.query(StockUnidad).filter_by(id=det.unidad_id).first()
                    if unidad:
                        unidad.estado = "activo"
                        unidad.fecha_modificacion = datetime.now().isoformat()

                restaurados.append({
                    "producto": producto.nombre,
                    "cantidad_restaurada": det.cantidad,
                    "tipo_venta": det.tipo_venta
                })

        session.commit()
        return {"exito": True, "venta_id": ultima_venta.id, "restaurados": restaurados}
    except Exception as e:
        session.rollback()
        return {"exito": False, "mensaje": str(e)}
    finally:
        session.close()
        
# Agregar estos métodos al final de crud.py

def agregar_producto_granel_por_id(producto_id, gramos):
    """
    Agrega un producto a granel al carrito usando ID de producto y cantidad en gramos.
    Convierte automáticamente gramos a kilogramos para el cálculo correcto.
    """
    producto = obtener_producto_por_id(producto_id)
    if not producto:
        return {"exito": False, "mensaje": "Producto no encontrado"}
    
    # Convertir gramos a kilogramos
    cantidad_kg = gramos / 1000.0
    
    if producto.cantidad < cantidad_kg:
        return {"exito": False, "mensaje": f"Stock insuficiente. Disponible: {producto.cantidad} kg, solicitado: {cantidad_kg} kg"}

    item_carrito = {
        "unidad_id": None,
        "producto_id": producto.id,
        "nombre": producto.nombre,
        "precio_unitario": producto.precio_redondeado,  # Precio por kilo
        "codigo_barras": None,
        "cantidad": cantidad_kg,  # Almacenar en kilogramos
        "cantidad_gramos": gramos,  # Mantener referencia de gramos originales
        "tipo_venta": "granel",
        "es_granel": True
    }
    
    carrito.append(item_carrito)
    return {"exito": True, "item": item_carrito, "mensaje": "Producto a granel agregado al carrito"}

def agregar_producto_granel_por_codigo(codigo_barras, gramos):
    """
    Agrega un producto a granel al carrito usando código de barras y cantidad en gramos.
    """
    unidad = validar_codigo_barras(codigo_barras)
    if not unidad:
        return {"exito": False, "mensaje": "Código de barras no válido o unidad inactiva"}

    producto = obtener_producto_por_id(unidad.producto_id)
    if not producto:
        return {"exito": False, "mensaje": "Producto no encontrado"}
    
    # Verificar si el producto se puede vender a granel
    if not getattr(producto, 'es_divisible', False):
        return {"exito": False, "mensaje": "Este producto no se puede vender a granel"}
    
    # Convertir gramos a kilogramos
    cantidad_kg = gramos / 1000.0
    
    if producto.cantidad < cantidad_kg:
        return {"exito": False, "mensaje": f"Stock insuficiente. Disponible: {producto.cantidad} kg"}

    item_carrito = {
        "unidad_id": unidad.id,
        "producto_id": producto.id,
        "nombre": producto.nombre,
        "precio_unitario": producto.precio_redondeado,  # Precio por kilo
        "codigo_barras": unidad.codigo_barras,
        "cantidad": cantidad_kg,  # Almacenar en kilogramos
        "cantidad_gramos": gramos,  # Mantener referencia de gramos originales
        "tipo_venta": "granel_codigo",
        "es_granel": True
    }
    
    carrito.append(item_carrito)
    return {"exito": True, "item": item_carrito, "mensaje": "Producto a granel agregado al carrito"}

def descontar_stock_producto_granel(producto_id, cantidad_kg):
    """
    Descuenta cantidad en kilogramos del stock de un producto a granel.
    """
    session = Session()
    try:
        producto = session.query(Producto).filter_by(id=producto_id).first()
        if producto and producto.cantidad >= cantidad_kg:
            producto.cantidad -= cantidad_kg
            if producto.cantidad < 0:
                producto.cantidad = 0
            producto.ultima_modificacion = datetime.now().isoformat()
            session.commit()
            return True
        return False
    finally:
        session.close()