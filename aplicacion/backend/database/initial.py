from aplicacion.backend.database.database import SessionLocal, Usuario, Rol

def crear_rol_admin():
    session = SessionLocal()
    try:
        rol_existente = session.query(Rol).filter_by(id=1).first()
        
        if rol_existente:
            return True
        
        nuevo_rol = Rol(
            id=1,
            nombre="Administrador",
            permisos="all"
        )
        
        session.add(nuevo_rol)
        session.commit()
        print("Rol administrador creado con ID: 1")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"Error al crear rol admin: {e}")
        return False
    finally:
        session.close()

def crear_usuario_admin():
    session = SessionLocal()
    try:
        usuario_existente = session.query(Usuario).filter_by(nombre_usuario="admin").first()
        
        if usuario_existente:
            print("Usuario admin ya existe")
            return True
        
        crear_rol_admin()
        
        nuevo_admin = Usuario(
            nombre_usuario="admin",
            password="admin",
            rol_id=1
        )
        
        session.add(nuevo_admin)
        session.commit()
        session.refresh(nuevo_admin)
        
        print(f"Usuario admin creado con ID: {nuevo_admin.id}")
        return True
        
    except Exception as e:
        session.rollback()
        print(f"Error al crear usuario admin: {e}")
        return False
    finally:
        session.close()

def inicializar_usuario_admin():
    return crear_usuario_admin()

if __name__ == "__main__":
    inicializar_usuario_admin()