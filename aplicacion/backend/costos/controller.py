"""
Controlador para el módulo de Costos Operativos e Impuestos
Encapsula los métodos del CRUD para uso desde frontend y testing
"""

from aplicacion.backend.costos import crud

# ===============================
# CONTROLADORES COSTOS OPERATIVOS
# ===============================

def crear_costo_operativo_controller(nombre: str, monto: float, fecha_inicio: str, recurrente: bool = False, activo: bool = True) -> dict:
    """
    Controlador para crear un nuevo costo operativo.
    """
    return crud.CostosCRUD.crear_costo_operativo(
        nombre=nombre,
        monto=monto,
        fecha_inicio=fecha_inicio,
        recurrente=recurrente,
        activo=activo
    )

def crear_costo_operativo_simple_controller(nombre: str, monto: float, recurrente: bool = False) -> dict:
    """
    Controlador para crear un costo operativo con fecha actual.
    """
    return crud.crear_costo_operativo_simple(nombre, monto, recurrente)

def listar_costos_operativos_controller(solo_activos: bool = True) -> dict:
    """
    Controlador para listar costos operativos.
    """
    return crud.CostosCRUD.listar_costos_operativos(solo_activos)

def actualizar_costo_operativo_controller(costo_id: int, nombre: str = None, monto: float = None, fecha_inicio: str = None, recurrente: bool = None, activo: bool = None) -> dict:
    """
    Controlador para actualizar un costo operativo existente.
    """
    return crud.CostosCRUD.actualizar_costo_operativo(
        costo_id=costo_id,
        nombre=nombre,
        monto=monto,
        fecha_inicio=fecha_inicio,
        recurrente=recurrente,
        activo=activo
    )

def eliminar_costo_operativo_controller(costo_id: int) -> dict:
    """
    Controlador para desactivar un costo operativo.
    """
    return crud.CostosCRUD.eliminar_costo_operativo(costo_id)

# ===============================
# CONTROLADORES IMPUESTOS
# ===============================

def crear_impuesto_controller(nombre: str, tipo: str, valor: float, activo: bool = True) -> dict:
    """
    Controlador para crear un nuevo impuesto.
    """
    return crud.CostosCRUD.crear_impuesto(
        nombre=nombre,
        tipo=tipo,
        valor=valor,
        activo=activo
    )

def listar_impuestos_controller(solo_activos: bool = True) -> dict:
    """
    Controlador para listar impuestos.
    """
    return crud.CostosCRUD.listar_impuestos(solo_activos)

def actualizar_impuesto_controller(impuesto_id: int, nombre: str = None, tipo: str = None, valor: float = None, activo: bool = None) -> dict:
    """
    Controlador para actualizar un impuesto existente.
    """
    return crud.CostosCRUD.actualizar_impuesto(
        impuesto_id=impuesto_id,
        nombre=nombre,
        tipo=tipo,
        valor=valor,
        activo=activo
    )

def eliminar_impuesto_controller(impuesto_id: int) -> dict:
    """
    Controlador para desactivar un impuesto.
    """
    return crud.CostosCRUD.eliminar_impuesto(impuesto_id)

# ===============================
# CONTROLADORES DE LIMPIEZA
# ===============================

def limpiar_costos_operativos_eliminados_controller() -> dict:
    """
    Controlador para eliminar permanentemente costos operativos con activo=False.
    """
    return crud.limpiar_costos_operativos_eliminados()

def limpiar_impuestos_eliminados_controller() -> dict:
    """
    Controlador para eliminar permanentemente impuestos con activo=False.
    """
    return crud.limpiar_impuestos_eliminados()

def limpiar_todos_los_eliminados_controller() -> dict:
    """
    Controlador para eliminar permanentemente todos los registros eliminados.
    """
    return crud.limpiar_todos_los_eliminados()

def contar_registros_eliminados_controller() -> dict:
    """
    Controlador para contar registros marcados como eliminados.
    """
    return crud.contar_registros_eliminados()

# ===============================
# CONTROLADORES COMBINADOS
# ===============================

def obtener_resumen_costos_controller() -> dict:
    """
    Controlador para obtener resumen completo de costos e impuestos.
    """
    return crud.CostosCRUD.obtener_resumen_costos()

def listar_costos_activos_controller() -> dict:
    """
    Controlador para listar solo costos operativos activos.
    """
    return crud.listar_costos_activos()

def listar_impuestos_activos_controller() -> dict:
    """
    Controlador para listar solo impuestos activos.
    """
    return crud.listar_impuestos_activos()

def obtener_resumen_completo_controller() -> dict:
    """
    Controlador para obtener resumen completo.
    """
    return crud.obtener_resumen_completo()