from aplicacion.backend.usuarios.usuarios import crud

def registrar_usuario_controller(nombre_usuario: str, password: str, email: str):
    """
    Registra un nuevo usuario en el sistema.
    """
    return crud.registrar_usuario(nombre_usuario, password, email)

def login_usuario_controller(nombre_usuario: str, password: str):
    """
    Inicia sesión para un usuario si las credenciales son correctas.
    """
    return crud.login_usuario(nombre_usuario, password)

def editar_usuario_controller(usuario_id: int, nuevos_datos: dict):
    """
    Edita datos de un usuario existente (nombre, email, password).
    """
    return crud.editar_usuario(usuario_id, nuevos_datos)

def recuperar_password_controller(email: str):
    """
    Recupera y restablece la contraseña de un usuario, enviándola al email.
    """
    return crud.recuperar_contraseña(email)

def obtener_usuario_controller(usuario_id: int):
    """
    Devuelve un usuario por su ID.
    """
    return crud.obtener_usuario_por_id(usuario_id)

def listar_usuarios_controller():
    """
    Devuelve la lista completa de todos los usuarios del sistema.
    """
    return crud.listar_usuarios()
