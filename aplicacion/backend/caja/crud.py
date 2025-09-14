from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from aplicacion.backend.database.database import SessionLocal, CierreCaja, Usuario


class CajaCRUD:
    
    @staticmethod
    def get_session() -> Session:
        return SessionLocal()
    
    @staticmethod
    def registrar_caja_diaria(
        fecha: str,
        monto_efectivo: float,
        monto_transferencia: float,
        usuario_id: int,
        observaciones: str = ""
    ) -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            cierre_existente = session.query(CierreCaja).filter(
                CierreCaja.fecha == fecha,
                CierreCaja.estado == True
            ).first()
            
            if cierre_existente:
                return {
                    "success": False,
                    "message": f"Ya existe un cierre de caja para la fecha {fecha}",
                    "data": None
                }
            
            monto_total = monto_efectivo + monto_transferencia
            
            if monto_total < 0:
                return {
                    "success": False,
                    "message": "Los montos no pueden ser negativos",
                    "data": None
                }
            
            nuevo_cierre = CierreCaja(
                fecha=fecha,
                hora_cierre=datetime.now().isoformat(),
                monto_efectivo=monto_efectivo,
                monto_transferencia=monto_transferencia,
                monto_total=monto_total,
                usuario_id=usuario_id,
                observaciones=observaciones,
                estado=True
            )
            
            session.add(nuevo_cierre)
            session.commit()
            session.refresh(nuevo_cierre)
            
            return {
                "success": True,
                "message": "Cierre de caja registrado exitosamente",
                "data": {
                    "id": nuevo_cierre.id,
                    "fecha": nuevo_cierre.fecha,
                    "monto_efectivo": nuevo_cierre.monto_efectivo,
                    "monto_transferencia": nuevo_cierre.monto_transferencia,
                    "monto_total": nuevo_cierre.monto_total,
                    "hora_cierre": nuevo_cierre.hora_cierre,
                    "observaciones": nuevo_cierre.observaciones
                }
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()
    
    @staticmethod
    def consultar_caja_por_fecha(fecha: str) -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            cierre = session.query(CierreCaja).filter(
                CierreCaja.fecha == fecha,
                CierreCaja.estado == True
            ).first()
            
            if not cierre:
                return {
                    "success": False,
                    "message": f"No se encontro cierre de caja para la fecha {fecha}",
                    "data": None
                }
            
            usuario_nombre = None
            if cierre.usuario_id:
                usuario = session.query(Usuario).filter(Usuario.id == cierre.usuario_id).first()
                if usuario:
                    usuario_nombre = usuario.nombre_usuario
            
            return {
                "success": True,
                "message": "Cierre encontrado exitosamente",
                "data": {
                    "id": cierre.id,
                    "fecha": cierre.fecha,
                    "hora_cierre": cierre.hora_cierre,
                    "monto_efectivo": cierre.monto_efectivo,
                    "monto_transferencia": cierre.monto_transferencia,
                    "monto_total": cierre.monto_total,
                    "usuario_id": cierre.usuario_id,
                    "usuario_nombre": usuario_nombre,
                    "observaciones": cierre.observaciones,
                    "estado": cierre.estado
                }
            }
            
        except SQLAlchemyError as e:
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()
    
    @staticmethod
    def eliminar_registro_caja(cierre_id: int, motivo: str = "") -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            cierre = session.query(CierreCaja).filter(
                CierreCaja.id == cierre_id
            ).first()
            
            if not cierre:
                return {
                    "success": False,
                    "message": f"No se encontro el cierre con ID {cierre_id}",
                    "data": None
                }
            
            if not cierre.estado:
                return {
                    "success": False,
                    "message": "El cierre ya estaba eliminado/inactivo",
                    "data": None
                }
            
            cierre.estado = False
            
            if motivo:
                observaciones_actuales = cierre.observaciones or ""
                cierre.observaciones = f"{observaciones_actuales} | ELIMINADO: {motivo} ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            
            session.commit()
            
            return {
                "success": True,
                "message": "Registro de caja eliminado exitosamente",
                "data": {
                    "id": cierre.id,
                    "fecha": cierre.fecha,
                    "monto_total": cierre.monto_total,
                    "motivo_eliminacion": motivo
                }
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()
    
    @staticmethod
    def listar_cierres_rango(fecha_inicio: str, fecha_fin: str) -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            cierres = session.query(CierreCaja).filter(
                CierreCaja.fecha >= fecha_inicio,
                CierreCaja.fecha <= fecha_fin,
                CierreCaja.estado == True
            ).order_by(CierreCaja.fecha.desc()).all()
            
            lista_cierres = []
            total_efectivo = 0
            total_transferencia = 0
            total_general = 0
            
            for cierre in cierres:
                usuario_nombre = None
                if cierre.usuario_id:
                    usuario = session.query(Usuario).filter(Usuario.id == cierre.usuario_id).first()
                    if usuario:
                        usuario_nombre = usuario.nombre_usuario
                
                cierre_data = {
                    "id": cierre.id,
                    "fecha": cierre.fecha,
                    "hora_cierre": cierre.hora_cierre,
                    "monto_efectivo": cierre.monto_efectivo,
                    "monto_transferencia": cierre.monto_transferencia,
                    "monto_total": cierre.monto_total,
                    "usuario_nombre": usuario_nombre,
                    "observaciones": cierre.observaciones
                }
                
                lista_cierres.append(cierre_data)
                total_efectivo += cierre.monto_efectivo
                total_transferencia += cierre.monto_transferencia
                total_general += cierre.monto_total
            
            return {
                "success": True,
                "message": f"Se encontraron {len(lista_cierres)} cierres",
                "data": {
                    "cierres": lista_cierres,
                    "resumen": {
                        "cantidad_cierres": len(lista_cierres),
                        "total_efectivo": total_efectivo,
                        "total_transferencia": total_transferencia,
                        "total_general": total_general,
                        "promedio_diario": total_general / len(lista_cierres) if lista_cierres else 0
                    }
                }
            }
            
        except SQLAlchemyError as e:
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()
    
    @staticmethod
    def actualizar_caja(
        cierre_id: int,
        monto_efectivo: float = None,
        monto_transferencia: float = None,
        observaciones: str = None
    ) -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            cierre = session.query(CierreCaja).filter(
                CierreCaja.id == cierre_id,
                CierreCaja.estado == True
            ).first()
            
            if not cierre:
                return {
                    "success": False,
                    "message": f"No se encontro el cierre con ID {cierre_id}",
                    "data": None
                }
            
            if monto_efectivo is not None:
                cierre.monto_efectivo = monto_efectivo
            
            if monto_transferencia is not None:
                cierre.monto_transferencia = monto_transferencia
            
            if monto_efectivo is not None or monto_transferencia is not None:
                cierre.monto_total = cierre.monto_efectivo + cierre.monto_transferencia
            
            if observaciones is not None:
                cierre.observaciones = observaciones
            
            session.commit()
            session.refresh(cierre)
            
            return {
                "success": True,
                "message": "Cierre actualizado exitosamente",
                "data": {
                    "id": cierre.id,
                    "fecha": cierre.fecha,
                    "monto_efectivo": cierre.monto_efectivo,
                    "monto_transferencia": cierre.monto_transferencia,
                    "monto_total": cierre.monto_total,
                    "observaciones": cierre.observaciones
                }
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()


    @staticmethod
    def limpiar_registros_eliminados() -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            registros_eliminados = session.query(CierreCaja).filter(
                CierreCaja.estado == False
            ).all()
            
            if not registros_eliminados:
                return {
                    "success": True,
                    "message": "No hay registros eliminados para limpiar",
                    "data": {
                        "registros_eliminados": 0,
                        "detalles": []
                    }
                }
            
            detalles_eliminados = []
            for registro in registros_eliminados:
                detalles_eliminados.append({
                    "id": registro.id,
                    "fecha": registro.fecha,
                    "monto_total": registro.monto_total,
                    "observaciones": registro.observaciones
                })
            
            cantidad_eliminada = len(registros_eliminados)
            
            for registro in registros_eliminados:
                session.delete(registro)
            
            session.commit()
            
            return {
                "success": True,
                "message": f"Se eliminaron permanentemente {cantidad_eliminada} registros",
                "data": {
                    "registros_eliminados": cantidad_eliminada,
                    "detalles": detalles_eliminados
                }
            }
            
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()
    
    @staticmethod
    def contar_registros_eliminados() -> Dict[str, Any]:
        session = CajaCRUD.get_session()
        
        try:
            count = session.query(CierreCaja).filter(
                CierreCaja.estado == False
            ).count()
            
            ejemplos = []
            if count > 0:
                registros_muestra = session.query(CierreCaja).filter(
                    CierreCaja.estado == False
                ).limit(5).all()
                
                for registro in registros_muestra:
                    ejemplos.append({
                        "fecha": registro.fecha,
                        "monto_total": registro.monto_total,
                        "observaciones": registro.observaciones or "Sin observaciones"
                    })
            
            return {
                "success": True,
                "message": f"Se encontraron {count} registros eliminados",
                "data": {
                    "cantidad": count,
                    "ejemplos": ejemplos
                }
            }
            
        except SQLAlchemyError as e:
            return {
                "success": False,
                "message": f"Error de base de datos: {str(e)}",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
        finally:
            session.close()


def registrar_caja_hoy(monto_efectivo: float, monto_transferencia: float, usuario_id: int, observaciones: str = ""):
    fecha_hoy = date.today().isoformat()
    return CajaCRUD.registrar_caja_diaria(fecha_hoy, monto_efectivo, monto_transferencia, usuario_id, observaciones)

def consultar_caja_hoy():
    fecha_hoy = date.today().isoformat()
    return CajaCRUD.consultar_caja_por_fecha(fecha_hoy)

def cierres_mes_actual():
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1).isoformat()
    fin_mes = hoy.isoformat()
    return CajaCRUD.listar_cierres_rango(inicio_mes, fin_mes)

def limpiar_registros_eliminados():
    return CajaCRUD.limpiar_registros_eliminados()

def contar_registros_eliminados():
    return CajaCRUD.contar_registros_eliminados()