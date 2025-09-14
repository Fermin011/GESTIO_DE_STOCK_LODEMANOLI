"""
Utilidades de ventas – limpieza de unidades inactivas
"""
from __future__ import annotations
from typing import Optional, Dict

from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_

# Usamos tu patrón de imports/sesión
from aplicacion.backend.database.database import engine, StockUnidad

Session = sessionmaker(bind=engine)


def purgar_unidades_inactivas(producto_id: Optional[int] = None) -> Dict[str, object]:
    """
    Borra definitivamente de la tabla `stock_unidades` todos los registros
    cuyo `estado` sea 'inactivo'.

    - Si `producto_id` es None -> purga global (todas las unidades inactivas).
    - Si `producto_id` tiene valor -> purga sólo las unidades inactivas de ese producto.

    Returns
    -------
    dict: { "exito": bool, "eliminadas": int, "mensaje"?: str }
    """
    session = Session()
    try:
        q = session.query(StockUnidad).filter(StockUnidad.estado == "inactivo")
        if producto_id is not None:
            q = q.filter(and_(StockUnidad.producto_id == int(producto_id)))

        eliminadas = q.delete(synchronize_session=False)
        session.commit()
        return {"exito": True, "eliminadas": int(eliminadas or 0)}
    except Exception as e:
        session.rollback()
        return {"exito": False, "mensaje": str(e)}
    finally:
        session.close()


