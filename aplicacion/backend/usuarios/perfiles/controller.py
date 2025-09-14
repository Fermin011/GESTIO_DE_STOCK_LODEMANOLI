from aplicacion.backend.usuarios.perfiles import crud

def obtener_perfil_controller(usuario_id: int):
    """
    Devuelve los datos del perfil asociado a un usuario.
    """
    return crud.obtener_perfil(usuario_id)

def actualizar_nombre_perfil_controller(usuario_id: int, nuevo_nombre: str):
    """
    Actualiza el nombre del perfil del usuario.
    """
    return crud.actualizar_nombre(usuario_id, nuevo_nombre)

def actualizar_email_perfil_controller(usuario_id: int, nuevo_email: str):
    """
    Actualiza el email del perfil del usuario.
    """
    return crud.actualizar_email(usuario_id, nuevo_email)

def actualizar_telefono_perfil_controller(usuario_id: int, nuevo_telefono: str):
    """
    Actualiza el teléfono del perfil del usuario.
    """
    return crud.actualizar_telefono(usuario_id, nuevo_telefono)
