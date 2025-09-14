from aplicacion.backend.ventas import crud

def agregar_producto_por_codigo_controller(codigo_barras: str) -> dict:
    """
    Controlador para agregar un producto al carrito usando código de barras.
    """
    return crud.agregar_producto_por_codigo_barras(codigo_barras)

def agregar_producto_por_id_controller(producto_id: int, cantidad: float = 1) -> dict:
    """
    Controlador para agregar un producto al carrito usando ID de producto.
    Funciona tanto para productos por unidad como por peso.
    """
    return crud.agregar_producto_por_id(producto_id, cantidad)

def agregar_producto_a_carrito_controller(codigo_barras: str = None, producto_kg_id: int = None, cantidad_kg: float = 0, producto_id: int = None, cantidad: float = 1) -> dict:
    """
    Controlador unificado para agregar productos al carrito.
    Mantiene compatibilidad con la implementación anterior.
    
    Parámetros:
    - codigo_barras: Para agregar por código de barras
    - producto_kg_id + cantidad_kg: Para agregar productos por peso (legacy)
    - producto_id + cantidad: Para agregar cualquier producto por ID
    """
    resultado = crud.agregar_producto_a_carrito(
        crud.carrito, 
        codigo_barras=codigo_barras, 
        producto_kg_id=producto_kg_id, 
        cantidad_kg=cantidad_kg,
        producto_id=producto_id,
        cantidad=cantidad
    )
    
    if resultado:
        return {"exito": True, "item": resultado}
    else:
        return {"exito": False, "mensaje": "No se pudo agregar el producto al carrito"}

def obtener_productos_por_kg_controller() -> list:
    """
    Devuelve todos los productos que se venden por kilo.
    """
    return crud.obtener_productos_por_kg()

def obtener_todos_los_productos_controller() -> list:
    """
    Devuelve todos los productos con stock disponible.
    """
    return crud.obtener_todos_los_productos()

def obtener_carrito_controller() -> list:
    """
    Devuelve el contenido actual del carrito.
    """
    return crud.obtener_carrito()

def calcular_total_carrito_controller() -> float:
    """
    Calcula el total del carrito actual.
    """
    return crud.calcular_total_carrito()

def limpiar_carrito_controller() -> dict:
    """
    Limpia el carrito completamente.
    """
    crud.limpiar_carrito()
    return {"exito": True, "mensaje": "Carrito limpiado"}

def eliminar_item_carrito_controller(indice: int) -> dict:
    """
    Elimina un item específico del carrito.
    """
    return crud.eliminar_item_carrito(indice)

def confirmar_venta_controller(data: dict) -> dict:
    """
    Confirma la venta, registra en la base de datos y limpia el carrito.
    Espera un diccionario con método de pago y usuario_id.
    """
    return crud.confirmar_venta(data)

def cancelar_ultima_venta_controller() -> dict:
    """
    Llama al CRUD para cancelar la última venta registrada.
    Devuelve un diccionario con información sobre el resultado.
    """
    return crud.cancelar_ultima_venta()

# ... (resto de imports ya existentes)
from aplicacion.backend.ventas.utils import purgar_unidades_inactivas as _purgar_unidades_inactivas




def purgar_unidades_inactivas_controller(producto_id: int | None = None):
    """Wrapper de controller para purgar unidades con estado 'inactivo'."""
    return _purgar_unidades_inactivas(producto_id)

# Agregar estos métodos al controller.py

def agregar_producto_granel_por_id_controller(producto_id: int, gramos: float) -> dict:
    """
    Controlador para agregar un producto a granel al carrito usando ID de producto.
    
    Args:
        producto_id: ID del producto
        gramos: Cantidad en gramos
    
    Returns:
        dict: Resultado de la operación
    """
    return crud.agregar_producto_granel_por_id(producto_id, gramos)

def agregar_producto_granel_por_codigo_controller(codigo_barras: str, gramos: float) -> dict:
    """
    Controlador para agregar un producto a granel al carrito usando código de barras.
    
    Args:
        codigo_barras: Código de barras del producto
        gramos: Cantidad en gramos
    
    Returns:
        dict: Resultado de la operación
    """
    return crud.agregar_producto_granel_por_codigo(codigo_barras, gramos)