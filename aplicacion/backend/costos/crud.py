
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


from aplicacion.backend.database.database import SessionLocal, CostoOperativo, Impuesto


class CostosCRUD:
    
    
    @staticmethod
    def get_session() -> Session:
        """Obtiene una sesión de base de datos"""
        return SessionLocal()
    

    @staticmethod
    def crear_costo_operativo(
        nombre: str,
        monto: float,
        fecha_inicio: str,
        recurrente: bool = False,
        activo: bool = True
    ) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            costo_existente = session.query(CostoOperativo).filter(
                CostoOperativo.nombre == nombre,
                CostoOperativo.activo == True
            ).first()
            
            if costo_existente:
                return {
                    "success": False,
                    "message": f"Ya existe un costo operativo activo con el nombre '{nombre}'",
                    "data": None
                }
            
            if monto < 0:
                return {
                    "success": False,
                    "message": "El monto no puede ser negativo",
                    "data": None
                }
            
            nuevo_costo = CostoOperativo(
                nombre=nombre,
                monto=monto,
                fecha_inicio=fecha_inicio,
                recurrente=recurrente,
                activo=activo
            )
            
            session.add(nuevo_costo)
            session.commit()
            session.refresh(nuevo_costo)
            
            return {
                "success": True,
                "message": "Costo operativo creado exitosamente",
                "data": {
                    "id": nuevo_costo.id,
                    "nombre": nuevo_costo.nombre,
                    "monto": nuevo_costo.monto,
                    "fecha_inicio": nuevo_costo.fecha_inicio,
                    "recurrente": nuevo_costo.recurrente,
                    "activo": nuevo_costo.activo
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
    def listar_costos_operativos(solo_activos: bool = True) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            query = session.query(CostoOperativo)
            
            if solo_activos:
                query = query.filter(CostoOperativo.activo == True)
            
            costos = query.order_by(CostoOperativo.nombre).all()
            
            lista_costos = []
            total_costos = 0
            costos_recurrentes = 0
            
            for costo in costos:
                costo_data = {
                    "id": costo.id,
                    "nombre": costo.nombre,
                    "monto": costo.monto,
                    "fecha_inicio": costo.fecha_inicio,
                    "recurrente": costo.recurrente,
                    "activo": costo.activo
                }
                
                lista_costos.append(costo_data)
                
                if costo.activo:
                    total_costos += costo.monto
                    if costo.recurrente:
                        costos_recurrentes += costo.monto
            
            return {
                "success": True,
                "message": f"Se encontraron {len(lista_costos)} costos operativos",
                "data": {
                    "costos": lista_costos,
                    "resumen": {
                        "cantidad_costos": len(lista_costos),
                        "total_costos": total_costos,
                        "costos_recurrentes": costos_recurrentes,
                        "costos_una_vez": total_costos - costos_recurrentes
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
    def actualizar_costo_operativo(
        costo_id: int,
        nombre: str = None,
        monto: float = None,
        fecha_inicio: str = None,
        recurrente: bool = None,
        activo: bool = None
    ) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            costo = session.query(CostoOperativo).filter(
                CostoOperativo.id == costo_id
            ).first()
            
            if not costo:
                return {
                    "success": False,
                    "message": f"No se encontró el costo operativo con ID {costo_id}",
                    "data": None
                }
            
            if nombre is not None:
                costo.nombre = nombre
            
            if monto is not None:
                if monto < 0:
                    return {
                        "success": False,
                        "message": "El monto no puede ser negativo",
                        "data": None
                    }
                costo.monto = monto
            
            if fecha_inicio is not None:
                costo.fecha_inicio = fecha_inicio
            
            if recurrente is not None:
                costo.recurrente = recurrente
            
            if activo is not None:
                costo.activo = activo
            
            session.commit()
            session.refresh(costo)
            
            return {
                "success": True,
                "message": "Costo operativo actualizado exitosamente",
                "data": {
                    "id": costo.id,
                    "nombre": costo.nombre,
                    "monto": costo.monto,
                    "fecha_inicio": costo.fecha_inicio,
                    "recurrente": costo.recurrente,
                    "activo": costo.activo
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
    def eliminar_costo_operativo(costo_id: int) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            costo = session.query(CostoOperativo).filter(
                CostoOperativo.id == costo_id
            ).first()
            
            if not costo:
                return {
                    "success": False,
                    "message": f"No se encontró el costo operativo con ID {costo_id}",
                    "data": None
                }
            
            if not costo.activo:
                return {
                    "success": False,
                    "message": "El costo operativo ya está desactivado",
                    "data": None
                }
            
            costo.activo = False
            session.commit()
            
            return {
                "success": True,
                "message": "Costo operativo desactivado exitosamente",
                "data": {
                    "id": costo.id,
                    "nombre": costo.nombre,
                    "monto": costo.monto
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
    def crear_impuesto(
        nombre: str,
        tipo: str,
        valor: float,
        activo: bool = True
    ) -> Dict[str, Any]:
        """
        Crea un nuevo impuesto
        
        Args:
            nombre (str): Nombre del impuesto
            tipo (str): Tipo: 'porcentaje' o 'fijo'
            valor (float): Valor del impuesto
            activo (bool): Si el impuesto está activo
        
        Returns:
            Dict: Resultado de la operación
        """
        session = CostosCRUD.get_session()
        
        try:
            if tipo not in ['porcentaje', 'fijo']:
                return {
                    "success": False,
                    "message": "El tipo debe ser 'porcentaje' o 'fijo'",
                    "data": None
                }
            
            impuesto_existente = session.query(Impuesto).filter(
                Impuesto.nombre == nombre,
                Impuesto.activo == True
            ).first()
            
            if impuesto_existente:
                return {
                    "success": False,
                    "message": f"Ya existe un impuesto activo con el nombre '{nombre}'",
                    "data": None
                }
            
            if tipo == 'porcentaje' and (valor < 0 or valor > 100):
                return {
                    "success": False,
                    "message": "El valor del porcentaje debe estar entre 0 y 100",
                    "data": None
                }
            
            if tipo == 'fijo' and valor < 0:
                return {
                    "success": False,
                    "message": "El valor fijo no puede ser negativo",
                    "data": None
                }
            
            nuevo_impuesto = Impuesto(
                nombre=nombre,
                tipo=tipo,
                valor=valor,
                activo=activo
            )
            
            session.add(nuevo_impuesto)
            session.commit()
            session.refresh(nuevo_impuesto)
            
            return {
                "success": True,
                "message": "Impuesto creado exitosamente",
                "data": {
                    "id": nuevo_impuesto.id,
                    "nombre": nuevo_impuesto.nombre,
                    "tipo": nuevo_impuesto.tipo,
                    "valor": nuevo_impuesto.valor,
                    "activo": nuevo_impuesto.activo
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
    def listar_impuestos(solo_activos: bool = True) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            query = session.query(Impuesto)
            
            if solo_activos:
                query = query.filter(Impuesto.activo == True)
            
            impuestos = query.order_by(Impuesto.nombre).all()
            
            lista_impuestos = []
            impuestos_porcentaje = []
            impuestos_fijo = []
            
            for impuesto in impuestos:
                impuesto_data = {
                    "id": impuesto.id,
                    "nombre": impuesto.nombre,
                    "tipo": impuesto.tipo,
                    "valor": impuesto.valor,
                    "activo": impuesto.activo
                }
                
                lista_impuestos.append(impuesto_data)
                
                if impuesto.activo:
                    if impuesto.tipo == 'porcentaje':
                        impuestos_porcentaje.append(impuesto)
                    else:
                        impuestos_fijo.append(impuesto)
            
            total_fijo = sum(imp.valor for imp in impuestos_fijo)
            total_porcentaje = sum(imp.valor for imp in impuestos_porcentaje)
            
            return {
                "success": True,
                "message": f"Se encontraron {len(lista_impuestos)} impuestos",
                "data": {
                    "impuestos": lista_impuestos,
                    "resumen": {
                        "cantidad_impuestos": len(lista_impuestos),
                        "impuestos_fijo": len(impuestos_fijo),
                        "impuestos_porcentaje": len(impuestos_porcentaje),
                        "total_fijo": total_fijo,
                        "total_porcentaje": total_porcentaje
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
    def actualizar_impuesto(
        impuesto_id: int,
        nombre: str = None,
        tipo: str = None,
        valor: float = None,
        activo: bool = None
    ) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            impuesto = session.query(Impuesto).filter(
                Impuesto.id == impuesto_id
            ).first()
            
            if not impuesto:
                return {
                    "success": False,
                    "message": f"No se encontró el impuesto con ID {impuesto_id}",
                    "data": None
                }
            
            if tipo is not None and tipo not in ['porcentaje', 'fijo']:
                return {
                    "success": False,
                    "message": "El tipo debe ser 'porcentaje' o 'fijo'",
                    "data": None
                }
            
            if nombre is not None:
                impuesto.nombre = nombre
            
            if tipo is not None:
                impuesto.tipo = tipo
            
            if valor is not None:
                tipo_final = tipo if tipo is not None else impuesto.tipo
                
                if tipo_final == 'porcentaje' and (valor < 0 or valor > 100):
                    return {
                        "success": False,
                        "message": "El valor del porcentaje debe estar entre 0 y 100",
                        "data": None
                    }
                
                if tipo_final == 'fijo' and valor < 0:
                    return {
                        "success": False,
                        "message": "El valor fijo no puede ser negativo",
                        "data": None
                    }
                
                impuesto.valor = valor
            
            if activo is not None:
                impuesto.activo = activo
            
            session.commit()
            session.refresh(impuesto)
            
            return {
                "success": True,
                "message": "Impuesto actualizado exitosamente",
                "data": {
                    "id": impuesto.id,
                    "nombre": impuesto.nombre,
                    "tipo": impuesto.tipo,
                    "valor": impuesto.valor,
                    "activo": impuesto.activo
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
    def eliminar_impuesto(impuesto_id: int) -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            impuesto = session.query(Impuesto).filter(
                Impuesto.id == impuesto_id
            ).first()
            
            if not impuesto:
                return {
                    "success": False,
                    "message": f"No se encontró el impuesto con ID {impuesto_id}",
                    "data": None
                }
            
            if not impuesto.activo:
                return {
                    "success": False,
                    "message": "El impuesto ya está desactivado",
                    "data": None
                }
            
            impuesto.activo = False
            session.commit()
            
            return {
                "success": True,
                "message": "Impuesto desactivado exitosamente",
                "data": {
                    "id": impuesto.id,
                    "nombre": impuesto.nombre,
                    "tipo": impuesto.tipo,
                    "valor": impuesto.valor
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
    def obtener_resumen_costos() -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            costos = session.query(CostoOperativo).filter(
                CostoOperativo.activo == True
            ).all()
            
            impuestos = session.query(Impuesto).filter(
                Impuesto.activo == True
            ).all()
            
            total_costos = sum(costo.monto for costo in costos)
            costos_recurrentes = sum(costo.monto for costo in costos if costo.recurrente)
            
            total_impuestos_fijo = sum(imp.valor for imp in impuestos if imp.tipo == 'fijo')
            total_porcentajes = sum(imp.valor for imp in impuestos if imp.tipo == 'porcentaje')
            
            return {
                "success": True,
                "message": "Resumen de costos calculado",
                "data": {
                    "costos_operativos": {
                        "cantidad": len(costos),
                        "total": total_costos,
                        "recurrentes": costos_recurrentes,
                        "una_vez": total_costos - costos_recurrentes
                    },
                    "impuestos": {
                        "cantidad": len(impuestos),
                        "cantidad_fijo": len([imp for imp in impuestos if imp.tipo == 'fijo']),
                        "cantidad_porcentaje": len([imp for imp in impuestos if imp.tipo == 'porcentaje']),
                        "total_fijo": total_impuestos_fijo,
                        "total_porcentaje": total_porcentajes
                    },
                    "resumen_general": {
                        "total_costos_fijos": total_costos + total_impuestos_fijo,
                        "porcentajes_aplicables": total_porcentajes
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
    def limpiar_costos_operativos_eliminados() -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            costos_eliminados = session.query(CostoOperativo).filter(
                CostoOperativo.activo == False
            ).all()
            
            if not costos_eliminados:
                return {
                    "success": True,
                    "message": "No hay costos operativos eliminados para limpiar",
                    "data": {
                        "registros_eliminados": 0,
                        "detalles": []
                    }
                }
            
            detalles_eliminados = []
            for costo in costos_eliminados:
                detalles_eliminados.append({
                    "id": costo.id,
                    "nombre": costo.nombre,
                    "monto": costo.monto,
                    "fecha_inicio": costo.fecha_inicio,
                    "recurrente": costo.recurrente
                })
            
            cantidad_eliminada = len(costos_eliminados)
            
            for costo in costos_eliminados:
                session.delete(costo)
            
            session.commit()
            
            return {
                "success": True,
                "message": f"Se eliminaron permanentemente {cantidad_eliminada} costos operativos",
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
    def limpiar_impuestos_eliminados() -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            impuestos_eliminados = session.query(Impuesto).filter(
                Impuesto.activo == False
            ).all()
            
            if not impuestos_eliminados:
                return {
                    "success": True,
                    "message": "No hay impuestos eliminados para limpiar",
                    "data": {
                        "registros_eliminados": 0,
                        "detalles": []
                    }
                }
            
            detalles_eliminados = []
            for impuesto in impuestos_eliminados:
                detalles_eliminados.append({
                    "id": impuesto.id,
                    "nombre": impuesto.nombre,
                    "tipo": impuesto.tipo,
                    "valor": impuesto.valor
                })
            
            cantidad_eliminada = len(impuestos_eliminados)
            
            for impuesto in impuestos_eliminados:
                session.delete(impuesto)
            
            session.commit()
            
            return {
                "success": True,
                "message": f"Se eliminaron permanentemente {cantidad_eliminada} impuestos",
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
    def limpiar_todos_los_eliminados() -> Dict[str, Any]:

        resultado_costos = CostosCRUD.limpiar_costos_operativos_eliminados()
        
        resultado_impuestos = CostosCRUD.limpiar_impuestos_eliminados()
        
        if resultado_costos["success"] and resultado_impuestos["success"]:
            total_eliminados = (resultado_costos["data"]["registros_eliminados"] + 
                              resultado_impuestos["data"]["registros_eliminados"])
            
            return {
                "success": True,
                "message": f"Se eliminaron permanentemente {total_eliminados} registros en total",
                "data": {
                    "costos_eliminados": resultado_costos["data"]["registros_eliminados"],
                    "impuestos_eliminados": resultado_impuestos["data"]["registros_eliminados"],
                    "total_eliminados": total_eliminados,
                    "detalles_costos": resultado_costos["data"]["detalles"],
                    "detalles_impuestos": resultado_impuestos["data"]["detalles"]
                }
            }
        else:
            errores = []
            if not resultado_costos["success"]:
                errores.append(f"Costos: {resultado_costos['message']}")
            if not resultado_impuestos["success"]:
                errores.append(f"Impuestos: {resultado_impuestos['message']}")
            
            return {
                "success": False,
                "message": f"Errores en la limpieza: {'; '.join(errores)}",
                "data": None
            }
    
    @staticmethod
    def contar_registros_eliminados() -> Dict[str, Any]:

        session = CostosCRUD.get_session()
        
        try:
            costos_count = session.query(CostoOperativo).filter(
                CostoOperativo.activo == False
            ).count()
            
            impuestos_count = session.query(Impuesto).filter(
                Impuesto.activo == False
            ).count()
            
            ejemplos_costos = []
            ejemplos_impuestos = []
            
            if costos_count > 0:
                costos_muestra = session.query(CostoOperativo).filter(
                    CostoOperativo.activo == False
                ).limit(3).all()
                
                for costo in costos_muestra:
                    ejemplos_costos.append({
                        "nombre": costo.nombre,
                        "monto": costo.monto,
                        "recurrente": costo.recurrente
                    })
            
            if impuestos_count > 0:
                impuestos_muestra = session.query(Impuesto).filter(
                    Impuesto.activo == False
                ).limit(3).all()
                
                for impuesto in impuestos_muestra:
                    ejemplos_impuestos.append({
                        "nombre": impuesto.nombre,
                        "tipo": impuesto.tipo,
                        "valor": impuesto.valor
                    })
            
            total = costos_count + impuestos_count
            
            return {
                "success": True,
                "message": f"Se encontraron {total} registros eliminados",
                "data": {
                    "total": total,
                    "costos_eliminados": costos_count,
                    "impuestos_eliminados": impuestos_count,
                    "ejemplos_costos": ejemplos_costos,
                    "ejemplos_impuestos": ejemplos_impuestos
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


def crear_costo_operativo_simple(nombre: str, monto: float, recurrente: bool = False):
    """Crear costo operativo con fecha actual"""
    fecha_actual = date.today().isoformat()
    return CostosCRUD.crear_costo_operativo(nombre, monto, fecha_actual, recurrente)

def listar_costos_activos():
    """Lista solo costos operativos activos"""
    return CostosCRUD.listar_costos_operativos(solo_activos=True)

def listar_impuestos_activos():
    """Lista solo impuestos activos"""
    return CostosCRUD.listar_impuestos(solo_activos=True)

def obtener_resumen_completo():
    """Obtiene resumen completo de costos e impuestos"""
    return CostosCRUD.obtener_resumen_costos()

def limpiar_costos_operativos_eliminados():
    """Elimina permanentemente costos operativos marcados como eliminados"""
    return CostosCRUD.limpiar_costos_operativos_eliminados()

def limpiar_impuestos_eliminados():
    """Elimina permanentemente impuestos marcados como eliminados"""
    return CostosCRUD.limpiar_impuestos_eliminados()

def limpiar_todos_los_eliminados():
    """Elimina permanentemente todos los registros eliminados"""
    return CostosCRUD.limpiar_todos_los_eliminados()

def contar_registros_eliminados():
    """Cuenta registros marcados como eliminados"""
    return CostosCRUD.contar_registros_eliminados()