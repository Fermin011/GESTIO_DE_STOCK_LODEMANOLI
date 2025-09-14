from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from datetime import datetime
from aplicacion.backend.database.database import engine, Usuario, UsuarioPerfil
import random
import string

Session = sessionmaker(bind=engine)

# --- FUNCIONES AUXILIARES ---
def generar_contraseña_temporal(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

# --- CRUD DE USUARIOS ---
def registrar_usuario(nombre_usuario, password, email, rol_id=0):
    session = Session()
    try:
        # Registrar en la tabla usuarios
        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            password=password,
            rol_id=rol_id
        )
        session.add(nuevo_usuario)
        session.commit()
        session.refresh(nuevo_usuario)

        # Registrar en la tabla usuarios_perfil con email, usando nombre_usuario y dejando telefono vacío
        perfil = UsuarioPerfil(
            usuario_id=nuevo_usuario.id,
            nombre=nombre_usuario,
            email=email,
            telefono=""
        )
        session.add(perfil)
        session.commit()

        registrado = nuevo_usuario.id is not None
    except Exception:
        session.rollback()
        registrado = False
    finally:
        session.close()

    return registrado

def login_usuario(nombre_usuario, password):
    session = Session()
    usuario = session.query(Usuario).filter(
        and_(Usuario.nombre_usuario == nombre_usuario, Usuario.password == password)
    ).first()
    session.close()
    return usuario

def recuperar_contraseña(nombre_usuario):
    from aplicacion.backend.usuarios.usuarios.utils import enviar_email

    session = Session()
    usuario = session.query(Usuario).filter_by(nombre_usuario=nombre_usuario).first()
    if not usuario:
        session.close()
        return None
    
    perfil = session.query(UsuarioPerfil).filter_by(usuario_id=usuario.id).first()
    if not perfil or not perfil.email:
        session.close()
        return None

    # Obtener la contraseña actual
    contraseña_actual = usuario.password
    email = perfil.email
    session.close()

    # Enviar correo con la contraseña actual
    enviar_email(email, f"Tu contraseña actual es: {contraseña_actual}")

    # Confirmar ejecución exitosa
    return True

def editar_usuario(usuario_id, nuevo_password=None):
    session = Session()
    usuario = session.query(Usuario).filter_by(id=usuario_id).first()
    if usuario and nuevo_password:
        usuario.password = nuevo_password
        session.commit()
    session.close()
    return usuario

def editar_perfil(usuario_id, nombre=None, email=None, telefono=None):
    session = Session()
    perfil = session.query(UsuarioPerfil).filter_by(usuario_id=usuario_id).first()
    if perfil:
        if nombre is not None:
            perfil.nombre = nombre
        if email is not None:
            perfil.email = email
        if telefono is not None:
            perfil.telefono = telefono
        session.commit()
    session.close()
    return perfil

def obtener_usuario_por_id(usuario_id):
    session = Session()
    usuario = session.query(Usuario).filter_by(id=usuario_id).first()
    session.close()
    return usuario

def listar_usuarios():
    """
    Devuelve todos los usuarios registrados.
    """
    session = Session()
    usuarios = session.query(Usuario).all()
    session.close()
    return usuarios