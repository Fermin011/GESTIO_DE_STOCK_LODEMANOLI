"""
Módulo CRUD para cálculo y gestión de Ganancias Diarias
Calcula ganancias brutas y netas basándose en ventas, costos e impuestos
"""

from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Importar desde tu aplicación
from aplicacion.backend.database.database import (
    SessionLocal, Ganancia, VentaRegistro, VentaDetalle, 
    Producto, StockUnidad, CostoOperativo, Impuesto
)


class GananciasCRUD:
    """Clase para operaciones CRUD y cálculo de Ganancias"""
    
    @staticmethod
    def get_session() -> Session:
        """Obtiene una sesión de base de datos"""
        return SessionLocal()
    
    # ===============================
    # CÁLCULO DE GANANCIAS
    # ===============================
    
    @staticmethod
    def calcular_ganancias_fecha(fecha: str) -> Dict[str, Any]:
        """
        Calcula las ganancias brutas y netas para una fecha específica
        
        Args:
            fecha (str): Fecha en formato YYYY-MM-DD
        
        Returns:
            Dict: Resultado del cálculo con detalles
        """
        session = GananciasCRUD.get_session()
        
        try:
            ganancia_existente = session.query(Ganancia).filter(
                Ganancia.fecha == fecha
            ).first()
            
            ventas_fecha = session.query(VentaRegistro).filter(
                and_(
                    VentaRegistro.fecha.like(f"{fecha}%"),
                    VentaRegistro.estado == True
                )
            ).all()
            
            if not ventas_fecha:
                return {
                    "success": True,
                    "message": f"No hay ventas registradas para la fecha {fecha}",
                    "data": {
                        "fecha": fecha,
                        "ganancia_bruta": 0.0,
                        "ganancia_neta": 0.0,
                        "total_ventas": 0.0,
                        "total_costos_productos": 0.0,
                        "total_costos_operativos_diarios": 0.0,
                        "total_impuestos_fijos_diarios": 0.0,
                        "total_impuestos_porcentuales_diarios": 0.0,
                        "cantidad_ventas": 0,
                        "ya_calculado": ganancia_existente is not None
                    }
                }
            
            ganancia_bruta_total = 0.0
            total_costos_productos = 0.0
            detalles_calculo = []
            
            for venta in ventas_fecha:
                ganancia_bruta_total += venta.total
            
            for venta in ventas_fecha:
                detalles_venta = session.query(VentaDetalle).filter(
                    VentaDetalle.venta_id == venta.id
                ).all()
                
                for detalle in detalles_venta:
                    producto = None
                    
                    if detalle.tipo_venta == 'codigo_barras' and detalle.unidad_id:
                        unidad_stock = session.query(StockUnidad).filter(
                            StockUnidad.id == detalle.unidad_id
                        ).first()
                        
                        if unidad_stock:
                            producto = session.query(Producto).filter(
                                Producto.id == unidad_stock.producto_id
                            ).first()
                    
                    elif detalle.tipo_venta == 'producto_id' and detalle.producto_id:
                        producto = session.query(Producto).filter(
                            Producto.id == detalle.producto_id
                        ).first()
                    
                    if producto:
                        costo_unitario = producto.costo_unitario or 0.0
                        precio_venta = detalle.precio_unitario
                        cantidad = detalle.cantidad
                        
                        costo_total_item = costo_unitario * cantidad
                        total_costos_productos += costo_total_item
                        
                        detalles_calculo.append({
                            "producto": producto.nombre,
                            "cantidad": cantidad,
                            "precio_venta": precio_venta,
                            "costo_unitario": costo_unitario,
                            "costo_total": costo_total_item,
                            "subtotal_venta": precio_venta * cantidad,
                            "tipo_venta": detalle.tipo_venta
                        })
            
            costos_operativos = session.query(CostoOperativo).filter(
                CostoOperativo.activo == True
            ).all()
            
            total_costos_operativos_diarios = 0.0
            costos_aplicados = []
            
            for costo in costos_operativos:
                costo_diario = costo.monto / 30
                total_costos_operativos_diarios += costo_diario
                costos_aplicados.append({
                    "nombre": costo.nombre,
                    "monto_mensual": costo.monto,
                    "monto_diario": costo_diario,
                    "tipo": "recurrente" if costo.recurrente else "único"
                })
            
            impuestos_activos = session.query(Impuesto).filter(
                Impuesto.activo == True
            ).all()
            
            total_impuestos_fijos_diarios = 0.0
            total_impuestos_porcentuales_diarios = 0.0
            impuestos_aplicados = []
            
            for impuesto in impuestos_activos:
                if impuesto.tipo == 'fijo':
                    impuesto_diario = impuesto.valor / 30
                    total_impuestos_fijos_diarios += impuesto_diario
                    impuestos_aplicados.append({
                        "nombre": impuesto.nombre,
                        "tipo": "fijo",
                        "valor_mensual": impuesto.valor,
                        "valor_diario": impuesto_diario
                    })
                elif impuesto.tipo == 'porcentaje':
                    porcentaje_diario = impuesto.valor / 30
                    impuesto_porcentual_aplicado = (ganancia_bruta_total * porcentaje_diario / 100)
                    total_impuestos_porcentuales_diarios += impuesto_porcentual_aplicado
                    impuestos_aplicados.append({
                        "nombre": impuesto.nombre,
                        "tipo": "porcentaje",
                        "porcentaje_mensual": impuesto.valor,
                        "porcentaje_diario": porcentaje_diario,
                        "monto_aplicado": impuesto_porcentual_aplicado
                    })
            
            ganancia_neta = (ganancia_bruta_total - 
                           total_costos_productos - 
                           total_costos_operativos_diarios - 
                           total_impuestos_fijos_diarios - 
                           total_impuestos_porcentuales_diarios)
            
            resultado_calculo = {
                "fecha": fecha,
                "ganancia_bruta": ganancia_bruta_total,
                "ganancia_neta": ganancia_neta,
                "total_ventas": ganancia_bruta_total,
                "total_costos_productos": total_costos_productos,
                "total_costos_operativos_diarios": total_costos_operativos_diarios,
                "total_impuestos_fijos_diarios": total_impuestos_fijos_diarios,
                "total_impuestos_porcentuales_diarios": total_impuestos_porcentuales_diarios,
                "cantidad_ventas": len(ventas_fecha),
                "detalles_productos": detalles_calculo,
                "costos_aplicados": costos_aplicados,
                "impuestos_aplicados": impuestos_aplicados,
                "ya_calculado": ganancia_existente is not None,
                "total_costos_operativos_mensuales": sum(costo["monto_mensual"] for costo in costos_aplicados),
                "total_impuestos_fijos_mensuales": sum(imp["valor_mensual"] for imp in impuestos_aplicados if imp["tipo"] == "fijo")
            }
            
            return {
                "success": True,
                "message": f"Ganancias calculadas para {fecha}",
                "data": resultado_calculo
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
    def registrar_ganancias_fecha(fecha: str, sobrescribir: bool = False) -> Dict[str, Any]:
        """
        Calcula y registra las ganancias en la base de datos para una fecha específica
        
        Args:
            fecha (str): Fecha en formato YYYY-MM-DD
            sobrescribir (bool): Si sobrescribir cálculo existente
        
        Returns:
            Dict: Resultado de la operación
        """
        session = GananciasCRUD.get_session()
        
        try:
            ganancia_existente = session.query(Ganancia).filter(
                Ganancia.fecha == fecha
            ).first()
            
            if ganancia_existente and not sobrescribir:
                return {
                    "success": False,
                    "message": f"Ya existe un cálculo de ganancias para {fecha}",
                    "data": {
                        "ganancia_existente": {
                            "id": ganancia_existente.id,
                            "ganancia_bruta": ganancia_existente.ganancia_bruta,
                            "ganancia_neta": ganancia_existente.ganancia_neta
                        }
                    }
                }
            
            resultado_calculo = GananciasCRUD.calcular_ganancias_fecha(fecha)
            
            if not resultado_calculo["success"]:
                return resultado_calculo
            
            data = resultado_calculo["data"]
            
            if ganancia_existente:
                ganancia_existente.ganancia_bruta = data["ganancia_bruta"]
                ganancia_existente.ganancia_neta = data["ganancia_neta"]
                session.commit()
                
                return {
                    "success": True,
                    "message": f"Ganancias actualizadas para {fecha}",
                    "data": {
                        "id": ganancia_existente.id,
                        "fecha": fecha,
                        "ganancia_bruta": data["ganancia_bruta"],
                        "ganancia_neta": data["ganancia_neta"],
                        "accion": "actualizado"
                    }
                }
            else:
                nueva_ganancia = Ganancia(
                    fecha=fecha,
                    ganancia_bruta=data["ganancia_bruta"],
                    ganancia_neta=data["ganancia_neta"]
                )
                
                session.add(nueva_ganancia)
                session.commit()
                session.refresh(nueva_ganancia)
                
                return {
                    "success": True,
                    "message": f"Ganancias registradas para {fecha}",
                    "data": {
                        "id": nueva_ganancia.id,
                        "fecha": fecha,
                        "ganancia_bruta": data["ganancia_bruta"],
                        "ganancia_neta": data["ganancia_neta"],
                        "accion": "creado"
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
    def calcular_ganancia_neta_simple_fecha(fecha: str) -> Dict[str, Any]:

        session = GananciasCRUD.get_session()
        
        try:
            ventas_fecha = session.query(VentaRegistro).filter(
                and_(
                    VentaRegistro.fecha.like(f"{fecha}%"),
                    VentaRegistro.estado == True
                )
            ).all()
            
            if not ventas_fecha:
                return {
                    "success": True,
                    "message": f"No hay ventas registradas para la fecha {fecha}",
                    "data": {
                        "fecha": fecha,
                        "total_vendido": 0.0,
                        "total_costos_productos": 0.0,
                        "ganancia_neta_simple": 0.0,
                        "cantidad_ventas": 0,
                        "detalles_productos": []
                    }
                }
            
            total_vendido = 0.0
            total_costos_productos = 0.0
            detalles_productos = []
            
            for venta in ventas_fecha:
                total_vendido += venta.total
                
                detalles_venta = session.query(VentaDetalle).filter(
                    VentaDetalle.venta_id == venta.id
                ).all()
                
                for detalle in detalles_venta:
                    producto = None
                    
                    if detalle.tipo_venta == 'codigo_barras' and detalle.unidad_id:
                        unidad_stock = session.query(StockUnidad).filter(
                            StockUnidad.id == detalle.unidad_id
                        ).first()
                        
                        if unidad_stock:
                            producto = session.query(Producto).filter(
                                Producto.id == unidad_stock.producto_id
                            ).first()
                    
                    elif detalle.tipo_venta == 'producto_id' and detalle.producto_id:
                        producto = session.query(Producto).filter(
                            Producto.id == detalle.producto_id
                        ).first()
                    
                    if producto:
                        precio_venta_unitario = producto.precio_redondeado or detalle.precio_unitario
                        costo_unitario = producto.costo_unitario or 0.0
                        cantidad = detalle.cantidad
                        
                        ganancia_unitaria = precio_venta_unitario - costo_unitario
                        ganancia_total_producto = ganancia_unitaria * cantidad
                        costo_total_producto = costo_unitario * cantidad
                        
                        total_costos_productos += costo_total_producto
                        
                        detalles_productos.append({
                            "producto": producto.nombre,
                            "cantidad": cantidad,
                            "precio_venta_unitario": precio_venta_unitario,
                            "costo_unitario": costo_unitario,
                            "ganancia_unitaria": ganancia_unitaria,
                            "ganancia_total_producto": ganancia_total_producto,
                            "costo_total_producto": costo_total_producto,
                            "tipo_venta": detalle.tipo_venta
                        })
            
            ganancia_neta_simple = total_vendido - total_costos_productos
            
            return {
                "success": True,
                "message": f"Ganancia neta simple calculada para {fecha}",
                "data": {
                    "fecha": fecha,
                    "total_vendido": total_vendido,
                    "total_costos_productos": total_costos_productos,
                    "ganancia_neta_simple": ganancia_neta_simple,
                    "cantidad_ventas": len(ventas_fecha),
                    "detalles_productos": detalles_productos
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
    def comparar_ganancia_hoy_vs_ayer() -> Dict[str, Any]:

        try:
            fecha_hoy = date.today().isoformat()
            fecha_ayer = (date.today() - timedelta(days=1)).isoformat()
            
            resultado_hoy = GananciasCRUD.calcular_ganancia_neta_simple_fecha(fecha_hoy)
            
            if not resultado_hoy["success"]:
                return {
                    "success": False,
                    "message": f"Error al calcular ganancia de hoy: {resultado_hoy['message']}",
                    "data": None
                }
            
            if resultado_hoy["data"]["cantidad_ventas"] == 0:
                return {
                    "success": True,
                    "message": "No hay ganancia hoy para comparar",
                    "data": None
                }
            
            resultado_ayer = GananciasCRUD.calcular_ganancia_neta_simple_fecha(fecha_ayer)
            
            if not resultado_ayer["success"]:
                return {
                    "success": False,
                    "message": f"Error al calcular ganancia de ayer: {resultado_ayer['message']}",
                    "data": None
                }
            
            if resultado_ayer["data"]["cantidad_ventas"] == 0:
                return {
                    "success": True,
                    "message": "Hay ganancia hoy pero no ayer",
                    "data": False
                }
            
            ganancia_hoy = resultado_hoy["data"]["ganancia_neta_simple"]
            ganancia_ayer = resultado_ayer["data"]["ganancia_neta_simple"]
            diferencia = ganancia_hoy - ganancia_ayer
            
            porcentaje_cambio = 0.0
            if ganancia_ayer != 0:
                porcentaje_cambio = (diferencia / abs(ganancia_ayer)) * 100
            
            return {
                "success": True,
                "message": "Comparación realizada exitosamente",
                "data": {
                    "fecha_hoy": fecha_hoy,
                    "fecha_ayer": fecha_ayer,
                    "ganancia_hoy": ganancia_hoy,
                    "ganancia_ayer": ganancia_ayer,
                    "diferencia": diferencia,
                    "porcentaje_cambio": porcentaje_cambio,
                    "tendencia": "subida" if diferencia > 0 else ("bajada" if diferencia < 0 else "igual"),
                    "ventas_hoy": resultado_hoy["data"]["cantidad_ventas"],
                    "ventas_ayer": resultado_ayer["data"]["cantidad_ventas"],
                    "total_vendido_hoy": resultado_hoy["data"]["total_vendido"],
                    "total_vendido_ayer": resultado_ayer["data"]["total_vendido"]
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Error inesperado: {str(e)}",
                "data": None
            }
    
    @staticmethod
    def calcular_ganancia_neta_simple_hoy() -> Dict[str, Any]:
        """
        Calcula la ganancia neta simple para el día actual
        """
        fecha_hoy = date.today().isoformat()
        return GananciasCRUD.calcular_ganancia_neta_simple_fecha(fecha_hoy)
    
    @staticmethod
    def calcular_ganancias_hoy() -> Dict[str, Any]:
        """
        Calcula las ganancias para el día actual
        """
        fecha_hoy = date.today().isoformat()
        return GananciasCRUD.calcular_ganancias_fecha(fecha_hoy)
    
    @staticmethod
    def registrar_ganancias_hoy(sobrescribir: bool = False) -> Dict[str, Any]:
        """
        Registra las ganancias para el día actual
        """
        fecha_hoy = date.today().isoformat()
        return GananciasCRUD.registrar_ganancias_fecha(fecha_hoy, sobrescribir)
    
    # ===============================
    # CONSULTAS DE GANANCIAS
    # ===============================
    
    @staticmethod
    def consultar_ganancia_fecha(fecha: str) -> Dict[str, Any]:
        """
        Consulta la ganancia registrada para una fecha específica
        """
        session = GananciasCRUD.get_session()
        
        try:
            ganancia = session.query(Ganancia).filter(
                Ganancia.fecha == fecha
            ).first()
            
            if not ganancia:
                return {
                    "success": False,
                    "message": f"No se encontró registro de ganancias para {fecha}",
                    "data": None
                }
            
            return {
                "success": True,
                "message": f"Ganancia encontrada para {fecha}",
                "data": {
                    "id": ganancia.id,
                    "fecha": ganancia.fecha,
                    "ganancia_bruta": ganancia.ganancia_bruta,
                    "ganancia_neta": ganancia.ganancia_neta
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
    def listar_ganancias_rango(fecha_inicio: str, fecha_fin: str) -> Dict[str, Any]:
        """
        Lista todas las ganancias registradas en un rango de fechas
        """
        session = GananciasCRUD.get_session()
        
        try:
            ganancias = session.query(Ganancia).filter(
                and_(
                    Ganancia.fecha >= fecha_inicio,
                    Ganancia.fecha <= fecha_fin
                )
            ).order_by(Ganancia.fecha.desc()).all()
            
            lista_ganancias = []
            total_bruta = 0.0
            total_neta = 0.0
            
            for ganancia in ganancias:
                ganancia_data = {
                    "id": ganancia.id,
                    "fecha": ganancia.fecha,
                    "ganancia_bruta": ganancia.ganancia_bruta,
                    "ganancia_neta": ganancia.ganancia_neta
                }
                
                lista_ganancias.append(ganancia_data)
                total_bruta += ganancia.ganancia_bruta
                total_neta += ganancia.ganancia_neta
            
            return {
                "success": True,
                "message": f"Se encontraron {len(lista_ganancias)} registros de ganancias",
                "data": {
                    "ganancias": lista_ganancias,
                    "resumen": {
                        "cantidad_dias": len(lista_ganancias),
                        "total_bruta": total_bruta,
                        "total_neta": total_neta,
                        "promedio_bruta": total_bruta / len(lista_ganancias) if lista_ganancias else 0,
                        "promedio_neta": total_neta / len(lista_ganancias) if lista_ganancias else 0
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
    def obtener_resumen_mes_actual() -> Dict[str, Any]:
        """
        Obtiene un resumen de las ganancias del mes actual
        """
        hoy = date.today()
        fecha_inicio = date(hoy.year, hoy.month, 1).isoformat()
        fecha_fin = hoy.isoformat()
        
        return GananciasCRUD.listar_ganancias_rango(fecha_inicio, fecha_fin)
    
    @staticmethod
    def eliminar_ganancia_fecha(fecha: str) -> Dict[str, Any]:
        """
        Elimina el registro de ganancias para una fecha específica
        """
        session = GananciasCRUD.get_session()
        
        try:
            ganancia = session.query(Ganancia).filter(
                Ganancia.fecha == fecha
            ).first()
            
            if not ganancia:
                return {
                    "success": False,
                    "message": f"No se encontró registro de ganancias para {fecha}",
                    "data": None
                }
            
            info_eliminada = {
                "fecha": ganancia.fecha,
                "ganancia_bruta": ganancia.ganancia_bruta,
                "ganancia_neta": ganancia.ganancia_neta
            }
            
            session.delete(ganancia)
            session.commit()
            
            return {
                "success": True,
                "message": f"Registro de ganancias eliminado para {fecha}",
                "data": info_eliminada
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


# Funciones helper para uso más fácil
def calcular_ganancias_hoy():
    """Calcula ganancias para hoy sin registrar"""
    return GananciasCRUD.calcular_ganancias_hoy()

def calcular_ganancia_neta_simple_hoy():
    """Calcula ganancia neta simple para hoy"""
    return GananciasCRUD.calcular_ganancia_neta_simple_hoy()

def comparar_ganancia_hoy_vs_ayer():
    """Compara ganancia de hoy vs ayer"""
    return GananciasCRUD.comparar_ganancia_hoy_vs_ayer()

def registrar_ganancias_hoy(sobrescribir: bool = False):
    """Registra ganancias para hoy"""
    return GananciasCRUD.registrar_ganancias_hoy(sobrescribir)

def consultar_ganancias_mes_actual():
    """Obtiene resumen del mes actual"""
    return GananciasCRUD.obtener_resumen_mes_actual()

def calcular_y_registrar_fecha(fecha: str, sobrescribir: bool = False):
    """Calcula y registra ganancias para una fecha específica"""
    return GananciasCRUD.registrar_ganancias_fecha(fecha, sobrescribir)