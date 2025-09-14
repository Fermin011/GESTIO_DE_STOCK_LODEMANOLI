from aplicacion.backend.caja import crud

def registrar_caja_diaria_controller(fecha: str, monto_efectivo: float, monto_transferencia: float, usuario_id: int, observaciones: str = "") -> dict:
    monto_efectivo = monto_efectivo if monto_efectivo is not None else 0.0
    monto_transferencia = monto_transferencia if monto_transferencia is not None else 0.0
    
    return crud.CajaCRUD.registrar_caja_diaria(
        fecha=fecha,
        monto_efectivo=monto_efectivo,
        monto_transferencia=monto_transferencia,
        usuario_id=usuario_id,
        observaciones=observaciones
    )

def registrar_caja_hoy_controller(monto_efectivo: float, monto_transferencia: float, usuario_id: int, observaciones: str = "") -> dict:
    monto_efectivo = monto_efectivo if monto_efectivo is not None else 0.0
    monto_transferencia = monto_transferencia if monto_transferencia is not None else 0.0
    
    return crud.registrar_caja_hoy(
        monto_efectivo=monto_efectivo,
        monto_transferencia=monto_transferencia,
        usuario_id=usuario_id,
        observaciones=observaciones
    )

def consultar_caja_por_fecha_controller(fecha: str) -> dict:
    return crud.CajaCRUD.consultar_caja_por_fecha(fecha)

def consultar_caja_hoy_controller() -> dict:
    return crud.consultar_caja_hoy()

def eliminar_registro_caja_controller(cierre_id: int, motivo: str = "") -> dict:
    return crud.CajaCRUD.eliminar_registro_caja(cierre_id, motivo)

def listar_cierres_rango_controller(fecha_inicio: str, fecha_fin: str) -> dict:
    return crud.CajaCRUD.listar_cierres_rango(fecha_inicio, fecha_fin)

def actualizar_caja_controller(cierre_id: int, monto_efectivo: float = None, monto_transferencia: float = None, observaciones: str = None) -> dict:
    return crud.CajaCRUD.actualizar_caja(
        cierre_id=cierre_id,
        monto_efectivo=monto_efectivo,
        monto_transferencia=monto_transferencia,
        observaciones=observaciones
    )

def listar_cierres_mes_actual_controller() -> dict:
    return crud.cierres_mes_actual()

def listar_cierres_semana_controller() -> dict:
    from datetime import date, timedelta
    
    hoy = date.today()
    hace_7_dias = hoy - timedelta(days=7)
    
    return crud.CajaCRUD.listar_cierres_rango(
        fecha_inicio=hace_7_dias.isoformat(),
        fecha_fin=hoy.isoformat()
    )

def listar_cierres_mes_controller(year: int, month: int) -> dict:
    from datetime import date, timedelta
    
    fecha_inicio = date(year, month, 1).isoformat()
    
    if month == 12:
        fecha_fin = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        fecha_fin = date(year, month + 1, 1) - timedelta(days=1)
    
    return crud.CajaCRUD.listar_cierres_rango(fecha_inicio, fecha_fin.isoformat())

def limpiar_registros_eliminados_controller() -> dict:
    return crud.limpiar_registros_eliminados()

def contar_registros_eliminados_controller() -> dict:
    return crud.contar_registros_eliminados()

def validar_puede_registrar_caja_controller(fecha: str = None) -> dict:
    from datetime import date
    
    if fecha is None:
        fecha = date.today().isoformat()
    
    resultado = crud.CajaCRUD.consultar_caja_por_fecha(fecha)
    
    if resultado["success"]:
        return {
            "success": True,
            "message": f"Ya existe un cierre para la fecha {fecha}",
            "puede_registrar": False,
            "cierre_existente": resultado["data"]
        }
    else:
        return {
            "success": True,
            "message": f"Se puede registrar cierre para la fecha {fecha}",
            "puede_registrar": True
        }