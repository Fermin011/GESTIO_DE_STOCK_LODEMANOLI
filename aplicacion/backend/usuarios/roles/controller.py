from aplicacion.backend.usuarios.roles import crud

# ================== CONTROLADORES DE ROLES ==================

def crear_rol_controller(nombre, permisos_dict=None):
    """
    Crea un nuevo rol con permisos estructurados.
    """
    return crud.crear_rol(nombre, permisos_dict)

def editar_rol_controller(rol_id, permisos_dict):
    """
    Edita los permisos de un rol existente.
    """
    return crud.editar_rol(rol_id, permisos_dict)

def obtener_rol_controller(rol_id):
    """
    Obtiene un rol por su ID con permisos parseados.
    """
    return crud.obtener_rol(rol_id)

def listar_roles_controller():
    """
    Lista todos los roles con permisos parseados.
    """
    return crud.listar_roles()

def eliminar_rol_controller(rol_id):
    """
    Elimina un rol (solo si no está siendo usado).
    """
    return crud.eliminar_rol(rol_id)

# ================== CONTROLADORES DE PERMISOS ==================

def obtener_permisos_usuario_controller(usuario_id):
    """
    Obtiene los permisos de un usuario específico.
    """
    return crud.obtener_permisos_usuario(usuario_id)

def validar_permiso_usuario_controller(usuario_id, modulo, accion):
    """
    Valida si un usuario tiene un permiso específico.
    """
    permisos = crud.obtener_permisos_usuario(usuario_id)
    if not permisos:
        return False
    
    return permisos.get(modulo, {}).get(accion, False)

def asignar_rol_usuario_controller(usuario_id, rol_id):
    """
    Asigna un rol a un usuario.
    """
    return crud.asignar_rol_usuario(usuario_id, rol_id)

# ================== CONTROLADORES DE UTILIDADES ==================

def listar_modulos_disponibles_controller():
    """
    Lista todos los módulos y acciones disponibles.
    """
    return crud.listar_modulos_disponibles()

def obtener_estructura_permisos_controller():
    """
    Obtiene la estructura por defecto de permisos.
    """
    return crud.get_estructura_permisos_default()

def crear_roles_por_defecto_controller():
    """
    Crea los roles por defecto del sistema.
    """
    return crud.crear_roles_por_defecto()

# ================== CONTROLADORES DE PLANTILLAS ==================

def obtener_permisos_admin_controller():
    """
    Obtiene plantilla de permisos de administrador.
    """
    return crud.get_permisos_admin()

def obtener_permisos_empleado_basico_controller():
    """
    Obtiene plantilla de permisos de empleado básico.
    """
    return crud.get_permisos_empleado_basico()

def obtener_permisos_supervisor_controller():
    """
    Obtiene plantilla de permisos de supervisor.
    """
    return crud.get_permisos_supervisor()

# ================== CONTROLADORES AVANZADOS ==================

def clonar_rol_controller(rol_id_origen, nuevo_nombre):
    """
    Clona un rol existente con un nuevo nombre.
    """
    rol_origen = crud.obtener_rol(rol_id_origen)
    if not rol_origen:
        return False
    
    return crud.crear_rol(nuevo_nombre, rol_origen['permisos'])

def comparar_roles_controller(rol_id_1, rol_id_2):
    """
    Compara los permisos entre dos roles.
    """
    rol1 = crud.obtener_rol(rol_id_1)
    rol2 = crud.obtener_rol(rol_id_2)
    
    if not rol1 or not rol2:
        return None
    
    diferencias = {}
    permisos1 = rol1['permisos']
    permisos2 = rol2['permisos']
    
    for modulo in permisos1:
        diferencias[modulo] = {}
        for accion in permisos1[modulo]:
            valor1 = permisos1[modulo][accion]
            valor2 = permisos2.get(modulo, {}).get(accion, False)
            
            if valor1 != valor2:
                diferencias[modulo][accion] = {
                    'rol1': valor1,
                    'rol2': valor2
                }
    
    return {
        'rol1': {'id': rol1['id'], 'nombre': rol1['nombre']},
        'rol2': {'id': rol2['id'], 'nombre': rol2['nombre']},
        'diferencias': diferencias
    }

def obtener_estadisticas_roles_controller():
    """
    Obtiene estadísticas de uso de roles.
    """
    from aplicacion.backend.database.database import SessionLocal, Usuario
    
    session = SessionLocal()
    try:
        roles = crud.listar_roles()
        usuarios = session.query(Usuario).all()
        
        estadisticas = {
            'total_roles': len(roles),
            'total_usuarios': len(usuarios),
            'roles_detalle': [],
            'usuarios_sin_rol': 0
        }
        
        for rol in roles:
            usuarios_con_rol = session.query(Usuario).filter_by(rol_id=rol['id']).count()
            estadisticas['roles_detalle'].append({
                'rol': rol['nombre'],
                'usuarios_asignados': usuarios_con_rol,
                'porcentaje_uso': (usuarios_con_rol / len(usuarios) * 100) if usuarios else 0
            })
        
        # Contar usuarios sin rol
        estadisticas['usuarios_sin_rol'] = session.query(Usuario).filter_by(rol_id=None).count()
        
        session.close()
        return estadisticas
    except Exception as e:
        session.close()
        return {'error': str(e)}
    
def obtener_permisos_dict_usuario_controller(usuario_id):
    """
    Obtiene el diccionario de permisos de un usuario para el frontend.
    Retorna directamente el dict de permisos basado en su rol.
    """
    return crud.obtener_permisos_dict_usuario(usuario_id)