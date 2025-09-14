

from sqlalchemy.orm import sessionmaker
from aplicacion.backend.database.database import engine, UsuarioPerfil

Session = sessionmaker(bind=engine)

def obtener_perfil(usuario_id: int):
    """
    Devuelve el perfil asociado a un usuario por su ID.
    """
    session = Session()
    perfil = session.query(UsuarioPerfil).filter_by(usuario_id=usuario_id).first()
    session.close()
    return perfil

def actualizar_nombre(usuario_id: int, nuevo_nombre: str):
    """
    Actualiza el nombre del perfil del usuario.
    """
    session = Session()
    perfil = session.query(UsuarioPerfil).filter_by(usuario_id=usuario_id).first()
    if perfil:
        perfil.nombre = nuevo_nombre
        session.commit()
    session.close()
    return perfil is not None

def actualizar_email(usuario_id: int, nuevo_email: str):
    """
    Actualiza el email asociado al perfil del usuario.
    """
    session = Session()
    perfil = session.query(UsuarioPerfil).filter_by(usuario_id=usuario_id).first()
    if perfil:
        perfil.email = nuevo_email
        session.commit()
    session.close()
    return perfil is not None

def actualizar_telefono(usuario_id: int, nuevo_telefono: str):
    """
    Actualiza o agrega un teléfono al perfil del usuario.
    """
    session = Session()
    perfil = session.query(UsuarioPerfil).filter_by(usuario_id=usuario_id).first()
    if perfil:
        perfil.telefono = nuevo_telefono
        session.commit()
    session.close()
    return perfil is not None