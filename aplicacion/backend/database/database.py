# aplicacion/backend/database/database.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text, ForeignKey, REAL, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# === RUTA FIJA: aplicacion/manoli.db ===
APP_DIR = Path(__file__).resolve().parents[2]     # .../aplicacion
DB_PATH = APP_DIR / "manoli.db"                   # SIEMPRE ahí
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    future=True,
    echo=False,
    connect_args={"check_same_thread": False},     # PyQt + hilos
)
# Base declarativa
Base = declarative_base()
# Engine apuntando a SQLite


# SessionLocal global para reutilización
from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabla de proveedores
class Proveedor(Base):
    __tablename__ = 'proveedores'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    contacto = Column(String)
    direccion = Column(String)
    telefono = Column(String)
    email = Column(String)
    productos = relationship("Producto", back_populates="proveedor")

# Tabla de clasificaciones de stock
class StockClasificacion(Base):
    __tablename__ = 'stock_clasificacion'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    descripcion = Column(String)
    activa = Column(Boolean)
    productos = relationship("Producto", back_populates="clasificacion")

# Tabla de productos
class Producto(Base):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    unidad_medida = Column(String)
    cantidad = Column(REAL)
    costo_unitario = Column(REAL)
    precio_venta = Column(REAL)
    precio_redondeado = Column(REAL)
    usa_redondeo = Column(Boolean)
    margen_ganancia = Column(Float)
    es_divisible = Column(Boolean)
    unidad_base = Column(String)
    unidad_factor = Column(Integer)
    fecha_ingreso = Column(String, default=lambda: datetime.now().isoformat())
    ultima_modificacion = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'))
    categoria_id = Column(Integer, ForeignKey('stock_clasificacion.id'))

    proveedor = relationship("Proveedor", back_populates="productos")
    clasificacion = relationship("StockClasificacion", back_populates="productos")
    unidades = relationship("StockUnidad", back_populates="producto")

# Tabla de unidades de stock
class StockUnidad(Base):
    __tablename__ = 'stock_unidades'
    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'))
    codigo_barras = Column(String)
    estado = Column(String)
    fecha_ingreso = Column(String, default=lambda: datetime.now().isoformat())
    fecha_modificacion = Column(String, default=lambda: datetime.now().isoformat(), onupdate=lambda: datetime.now().isoformat())
    fecha_vencimiento = Column(String)  # formato YYYY-MM-DD
    observaciones = Column(Text)

    producto = relationship("Producto", back_populates="unidades")

# Tabla de ventas_registro
class VentaRegistro(Base):
    __tablename__ = 'ventas_registro'
    id = Column(Integer, primary_key=True)
    fecha = Column(String)
    total = Column(REAL)
    metodo_pago = Column(String)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    estado = Column(Boolean, default=True)  # True = realizada, False = cancelada
    detalles = relationship("VentaDetalle", back_populates="venta")

# Tabla de ventas_detalle - ACTUALIZADA
class VentaDetalle(Base):
    __tablename__ = 'ventas_detalle'
    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey('ventas_registro.id'))
    # unidad_id puede ser NULL cuando se vende por ID de producto
    unidad_id = Column(Integer, ForeignKey('stock_unidades.id'), nullable=True)
    # producto_id para saber siempre qué producto se vendió
    producto_id = Column(Integer, ForeignKey('productos.id'))
    cantidad = Column(REAL)
    precio_unitario = Column(REAL)
    subtotal = Column(REAL)
    # Tipo de venta: 'codigo_barras' o 'producto_id'
    tipo_venta = Column(String, default='codigo_barras')
    
    venta = relationship("VentaRegistro", back_populates="detalles")
    producto = relationship("Producto")
    unidad = relationship("StockUnidad")

# Tabla de cierre de caja - NUEVA
class CierreCaja(Base):
    __tablename__ = 'cierre_caja'
    id = Column(Integer, primary_key=True)
    fecha = Column(String)  # formato YYYY-MM-DD
    hora_cierre = Column(String, default=lambda: datetime.now().isoformat())
    monto_efectivo = Column(REAL, default=0.0)
    monto_transferencia = Column(REAL, default=0.0)
    monto_total = Column(REAL)  # efectivo + transferencia
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    observaciones = Column(Text)
    estado = Column(Boolean, default=True)  # True = cerrado, False = reabierto/cancelado
    
    usuario = relationship("Usuario", backref="cierres_caja")

# Tabla de ganancias
class Ganancia(Base):
    __tablename__ = 'ganancias'
    id = Column(Integer, primary_key=True)
    fecha = Column(String)
    ganancia_bruta = Column(REAL)
    ganancia_neta = Column(REAL)

# Tabla de usuarios
class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nombre_usuario = Column(String)
    password = Column(String)
    rol_id = Column(Integer, ForeignKey('roles.id'))
    perfil = relationship("UsuarioPerfil", back_populates="usuario", uselist=False)
    ventas = relationship("VentaRegistro", backref="usuario")
    actividades = relationship("ActividadUsuario", back_populates="usuario")

# Tabla de usuarios_perfil
class UsuarioPerfil(Base):
    __tablename__ = 'usuarios_perfil'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    nombre = Column(String)
    email = Column(String)
    telefono = Column(String)
    usuario = relationship("Usuario", back_populates="perfil")

# Tabla de roles
class Rol(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    permisos = Column(String)
    usuarios = relationship("Usuario", backref="rol")

# Tabla de actividad_usuarios
class ActividadUsuario(Base):
    __tablename__ = 'actividad_usuarios'
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    accion = Column(String)
    fecha = Column(String)
    usuario = relationship("Usuario", back_populates="actividades")

# Tabla de impuestos
class Impuesto(Base):
    __tablename__ = 'impuestos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo = Column(String)  # 'porcentaje' o 'fijo'
    valor = Column(REAL)
    activo = Column(Boolean)

# Tabla de costos_operativos
class CostoOperativo(Base):
    __tablename__ = 'costos_operativos'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    monto = Column(REAL)
    fecha_inicio = Column(String)
    recurrente = Column(Boolean)
    activo = Column(Boolean)

# Tabla de configuracion_sistema
class ConfiguracionSistema(Base):
    __tablename__ = 'configuracion_sistema'
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    valor = Column(String)

# Crear todas las tablas
def crear_tablas():
    Base.metadata.create_all(engine)