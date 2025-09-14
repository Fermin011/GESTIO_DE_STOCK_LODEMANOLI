"""
Controlador para el módulo de Ganancias
Encapsula los métodos del CRUD para uso desde frontend y testing
"""

from aplicacion.backend.metricas.ganancias import crud
from datetime import date, timedelta

# ===============================
# CONTROLADORES DE CÁLCULO
# ===============================

def calcular_ganancias_fecha_controller(fecha: str) -> dict:
    """
    Controlador para calcular ganancias de una fecha específica (sin registrar).
    """
    return crud.GananciasCRUD.calcular_ganancias_fecha(fecha)

def calcular_ganancias_hoy_controller() -> dict:
    """
    Controlador para calcular ganancias del día actual (sin registrar).
    """
    return crud.GananciasCRUD.calcular_ganancias_hoy()

def calcular_ganancia_neta_simple_fecha_controller(fecha: str) -> dict:
    """
    Controlador para calcular ganancia neta simple de una fecha específica.
    """
    return crud.GananciasCRUD.calcular_ganancia_neta_simple_fecha(fecha)

def calcular_ganancia_neta_simple_hoy_controller() -> dict:
    """
    Controlador para calcular ganancia neta simple del día actual.
    """
    return crud.GananciasCRUD.calcular_ganancia_neta_simple_hoy()

def comparar_ganancia_hoy_vs_ayer_controller() -> dict:
    """
    Controlador para comparar ganancia de hoy vs ayer.
    """
    return crud.GananciasCRUD.comparar_ganancia_hoy_vs_ayer()

def registrar_ganancias_fecha_controller(fecha: str, sobrescribir: bool = False) -> dict:
    """
    Controlador para calcular y registrar ganancias de una fecha específica.
    """
    return crud.GananciasCRUD.registrar_ganancias_fecha(fecha, sobrescribir)

def registrar_ganancias_hoy_controller(sobrescribir: bool = False) -> dict:
    """
    Controlador para calcular y registrar ganancias del día actual.
    """
    return crud.GananciasCRUD.registrar_ganancias_hoy(sobrescribir)

# ===============================
# CONTROLADORES DE CONSULTA
# ===============================

def consultar_ganancia_fecha_controller(fecha: str) -> dict:
    """
    Controlador para consultar ganancia registrada de una fecha específica.
    """
    return crud.GananciasCRUD.consultar_ganancia_fecha(fecha)

def listar_ganancias_rango_controller(fecha_inicio: str, fecha_fin: str) -> dict:
    """
    Controlador para listar ganancias en un rango de fechas.
    """
    return crud.GananciasCRUD.listar_ganancias_rango(fecha_inicio, fecha_fin)

def obtener_resumen_mes_actual_controller() -> dict:
    """
    Controlador para obtener resumen de ganancias del mes actual.
    """
    return crud.GananciasCRUD.obtener_resumen_mes_actual()

def listar_ganancias_semana_controller() -> dict:
    """
    Controlador para obtener ganancias de la última semana.
    """
    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=7)
    
    return crud.GananciasCRUD.listar_ganancias_rango(
        fecha_inicio=hace_7_dias.isoformat(),
        fecha_fin=hoy.isoformat()
    )

def listar_ganancias_mes_controller(year: int, month: int) -> dict:
    """
    Controlador para obtener ganancias de un mes específico.
    """
    # Calcular fechas del mes
    fecha_inicio = date(year, month, 1).isoformat()
    
    if month == 12:
        fecha_fin = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = date(year, month + 1, 1) - timedelta(days=1)
    
    return crud.GananciasCRUD.listar_ganancias_rango(fecha_inicio, fecha_fin.isoformat())

# ===============================
# CONTROLADORES DE ELIMINACIÓN
# ===============================

def eliminar_ganancia_fecha_controller(fecha: str) -> dict:
    """
    Controlador para eliminar registro de ganancias de una fecha específica.
    """
    return crud.GananciasCRUD.eliminar_ganancia_fecha(fecha)

# ===============================
# CONTROLADORES COMBINADOS
# ===============================

def calcular_y_registrar_fecha_controller(fecha: str, sobrescribir: bool = False) -> dict:
    """
    Controlador para calcular y registrar ganancias en una sola operación.
    """
    return crud.GananciasCRUD.registrar_ganancias_fecha(fecha, sobrescribir)