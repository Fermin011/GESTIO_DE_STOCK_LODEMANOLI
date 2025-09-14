from sqlalchemy.orm import sessionmaker
from aplicacion.backend.database.database import engine, Rol, Usuario, SessionLocal
import json

# Usar SessionLocal existente en lugar de crear uno nuevo
Session = SessionLocal

# ================== ESTRUCTURAS DE PERMISOS ==================

def get_estructura_permisos_default():
    """
    Estructura por defecto de todos los módulos y acciones disponibles
    """
    return {
        "ventas": {
            "ver": False,
            "crear": False,
            "editar": False,
            "eliminar": False,
            "descontar_stock": False
        },
        "stock": {
            "ver": False,
            "agregar": False,
            "editar": False,
            "eliminar": False,
            "ver_costos": False,
            "editar_precios": False
        },
        "reportes": {
            "ver": False,
            "generar": False,
            "exportar": False,
            "ver_ganancias": False
        },
        "usuarios": {
            "ver": False,
            "crear": False,
            "editar": False,
            "eliminar": False,
            "gestionar_roles": False
        },
        "caja": {
            "abrir": False,
            "cerrar": False,
            "ver_movimientos": False,
            "editar_montos": False
        },
        "configuracion": {
            "ver": False,
            "editar": False,
            "backup": False,
            "restore": False
        }
    }

def get_permisos_admin():
    """
    Permisos completos para administrador
    """
    permisos = get_estructura_permisos_default()
    for modulo in permisos:
        for accion in permisos[modulo]:
            permisos[modulo][accion] = True
    return permisos

def get_permisos_empleado_basico():
    """
    Permisos básicos para empleado (solo ventas y ver stock)
    """
    permisos = get_estructura_permisos_default()
    
    # Permisos de ventas básicos
    permisos["ventas"]["ver"] = True
    permisos["ventas"]["crear"] = True
    permisos["ventas"]["descontar_stock"] = True
    
    # Ver stock básico
    permisos["stock"]["ver"] = True
    permisos["stock"]["agregar"] = True
    
    # Caja básica
    permisos["caja"]["ver_movimientos"] = True
    
    return permisos

def get_permisos_supervisor():
    """
    Permisos intermedios para supervisor
    """
    permisos = get_permisos_empleado_basico()
    
    # Más permisos de ventas
    permisos["ventas"]["editar"] = True
    
    # Más permisos de stock
    permisos["stock"]["editar"] = True
    permisos["stock"]["ver_costos"] = True
    
    # Reportes básicos
    permisos["reportes"]["ver"] = True
    permisos["reportes"]["generar"] = True
    
    # Caja avanzada
    permisos["caja"]["abrir"] = True
    permisos["caja"]["cerrar"] = True
    
    return permisos

# ================== CRUD ROLES ==================

def crear_rol(nombre, permisos_dict=None):
    """
    Crea un nuevo rol con permisos estructurados.
    Si no se especifican permisos, usa la estructura por defecto (sin permisos)
    """
    session = Session()
    try:
        if permisos_dict is None:
            permisos_dict = get_estructura_permisos_default()
        
        # Validar estructura de permisos
        permisos_validados = validar_estructura_permisos(permisos_dict)
        
        permisos_str = json.dumps(permisos_validados, indent=2)
        nuevo_rol = Rol(nombre=nombre, permisos=permisos_str)
        session.add(nuevo_rol)
        session.commit()
        
        rol_id = nuevo_rol.id
        session.close()
        return rol_id
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error creando rol: {e}")
        return False

def editar_rol(rol_id, permisos_dict):
    """
    Edita los permisos de un rol existente.
    """
    session = Session()
    try:
        rol = session.query(Rol).filter_by(id=rol_id).first()
        if not rol:
            session.close()
            return False
        
        # Validar estructura de permisos
        permisos_validados = validar_estructura_permisos(permisos_dict)
        
        rol.permisos = json.dumps(permisos_validados, indent=2)
        session.commit()
        session.close()
        return True
    except Exception as e:
        session.rollback()
        session.close()
        print(f"Error editando rol: {e}")
        return False

def obtener_rol(rol_id):
    """
    Obtiene un rol por su ID con permisos parseados.
    """
    session = Session()
    try:
        rol = session.query(Rol).filter_by(id=rol_id).first()
        session.close()
        
        if rol and rol.permisos:
            # Parsear permisos JSON
            try:
                permisos_dict = json.loads(rol.permisos)
                return {
                    'id': rol.id,
                    'nombre': rol.nombre,
                    'permisos': permisos_dict,
                    'permisos_raw': rol.permisos
                }
            except json.JSONDecodeError:
                return {
                    'id': rol.id,
                    'nombre': rol.nombre,
                    'permisos': get_estructura_permisos_default(),
                    'permisos_raw': rol.permisos
                }
        
        return rol
    except Exception as e:
        session.close()
        print(f"Error obteniendo rol: {e}")
        return None

def listar_roles():
    """
    Lista todos los roles con permisos parseados.
    """
    session = Session()
    try:
        roles = session.query(Rol).all()
        session.close()
        
        roles_procesados = []
        for rol in roles:
            try:
                permisos_dict = json.loads(rol.permisos) if rol.permisos else get_estructura_permisos_default()
                roles_procesados.append({
                    'id': rol.id,
                    'nombre': rol.nombre,
                    'permisos': permisos_dict,
                    'permisos_raw': rol.permisos
                })
            except json.JSONDecodeError:
                roles_procesados.append({
                    'id': rol.id,
                    'nombre': rol.nombre,
                    'permisos': get_estructura_permisos_default(),
                    'permisos_raw': rol.permisos
                })
        
        return roles_procesados
    except Exception as e:
        session.close()
        print(f"Error listando roles: {e}")
        return []

def eliminar_rol(rol_id):
    """
    Elimina un rol (solo si no está siendo usado por usuarios)
    """
    session = Session()
    try:
        # Verificar si hay usuarios con este rol
        usuarios_con_rol = session.query(Usuario).filter_by(rol_id=rol_id).count()
        if usuarios_con_rol > 0:
            session.close()
            return False, f"No se puede eliminar el rol. {usuarios_con_rol} usuario(s) lo están usando."
        
        rol = session.query(Rol).filter_by(id=rol_id).first()
        if not rol:
            session.close()
            return False, "Rol no encontrado."
        
        session.delete(rol)
        session.commit()
        session.close()
        return True, "Rol eliminado correctamente."
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Error eliminando rol: {e}"

# ================== UTILIDADES ==================

def validar_estructura_permisos(permisos_dict):
    """
    Valida y completa la estructura de permisos para asegurar consistencia
    """
    estructura_completa = get_estructura_permisos_default()
    
    # Agregar módulos y acciones faltantes
    for modulo, acciones in estructura_completa.items():
        if modulo not in permisos_dict:
            permisos_dict[modulo] = acciones.copy()
        else:
            for accion, valor_default in acciones.items():
                if accion not in permisos_dict[modulo]:
                    permisos_dict[modulo][accion] = valor_default
    
    return permisos_dict

def obtener_permisos_usuario(usuario_id):
    """
    Obtiene los permisos de un usuario específico basado en su rol
    """
    session = Session()
    try:
        usuario = session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            session.close()
            return None
        
        # Si es admin (rol_id = 1), dar permisos completos
        if usuario.rol_id == 1:
            session.close()
            return get_permisos_admin()
        
        # Obtener permisos del rol
        rol = session.query(Rol).filter_by(id=usuario.rol_id).first()
        session.close()
        
        if rol and rol.permisos:
            try:
                return json.loads(rol.permisos)
            except json.JSONDecodeError:
                return get_estructura_permisos_default()
        
        return get_estructura_permisos_default()
    except Exception as e:
        session.close()
        print(f"Error obteniendo permisos de usuario: {e}")
        return get_estructura_permisos_default()

def listar_modulos_disponibles():
    """
    Lista todos los módulos y acciones disponibles
    """
    estructura = get_estructura_permisos_default()
    modulos = []
    
    for modulo, acciones in estructura.items():
        modulos.append({
            'nombre': modulo,
            'acciones': list(acciones.keys())
        })
    
    return modulos

def crear_roles_por_defecto():
    """
    Crea los roles por defecto del sistema si no existen
    """
    session = Session()
    try:
        # Verificar si ya existen roles
        roles_existentes = session.query(Rol).count()
        if roles_existentes > 0:
            session.close()
            return "Los roles ya existen"
        
        # Crear rol administrador
        admin_permisos = get_permisos_admin()
        rol_admin = Rol(nombre="Administrador", permisos=json.dumps(admin_permisos, indent=2))
        session.add(rol_admin)
        
        # Crear rol empleado básico
        empleado_permisos = get_permisos_empleado_basico()
        rol_empleado = Rol(nombre="Empleado", permisos=json.dumps(empleado_permisos, indent=2))
        session.add(rol_empleado)
        
        # Crear rol supervisor
        supervisor_permisos = get_permisos_supervisor()
        rol_supervisor = Rol(nombre="Supervisor", permisos=json.dumps(supervisor_permisos, indent=2))
        session.add(rol_supervisor)
        
        session.commit()
        session.close()
        return "Roles por defecto creados correctamente"
    except Exception as e:
        session.rollback()
        session.close()
        return f"Error creando roles por defecto: {e}"

def asignar_rol_usuario(usuario_id: int, rol_id: int):
    with Session() as s:
        try:
            user = s.get(Usuario, usuario_id)
            if not user:
                return False, "Usuario no encontrado"
            rol = s.get(Rol, rol_id)
            if not rol:
                return False, "Rol no encontrado"

            if user.rol_id == rol_id:
                return True, f"Rol '{rol.nombre}' ya estaba asignado a '{user.nombre_usuario}'"

            user.rol_id = rol.id
            nombre_user = user.nombre_usuario   # guardo antes, por las dudas
            nombre_rol = rol.nombre
            s.commit()
            return True, f"Rol '{nombre_rol}' asignado a '{nombre_user}'"
        except Exception as e:
            s.rollback()
            return False, f"Error asignando rol: {e}"
    
def obtener_permisos_dict_usuario(usuario_id):
    """
    Obtiene el diccionario de permisos de un usuario basado en su rol.
    Retorna el dict de permisos parseado directamente.
    """
    session = Session()
    try:
        # Buscar el usuario por ID
        usuario = session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            session.close()
            return None
        
        # Si no tiene rol asignado, devolver estructura vacía
        if not usuario.rol_id:
            session.close()
            return get_estructura_permisos_default()
        
        # Si es admin (rol_id = 1), dar permisos completos
        if usuario.rol_id == 1:
            session.close()
            return get_permisos_admin()
        
        # Buscar el rol del usuario
        rol = session.query(Rol).filter_by(id=usuario.rol_id).first()
        session.close()
        
        if rol and rol.permisos:
            try:
                # Parsear el JSON de permisos y devolverlo
                permisos_dict = json.loads(rol.permisos)
                return permisos_dict
            except json.JSONDecodeError:
                # Si hay error en el JSON, devolver estructura por defecto
                return get_estructura_permisos_default()
        
        # Si no hay rol o permisos, devolver estructura por defecto
        return get_estructura_permisos_default()
    
    except Exception as e:
        session.close()
        print(f"Error obteniendo permisos del usuario: {e}")
        return get_estructura_permisos_default()