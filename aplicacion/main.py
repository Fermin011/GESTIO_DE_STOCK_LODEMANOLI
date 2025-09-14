import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

import sys as _sys
if _sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.lodemano.app") 
    except Exception:
        pass

from aplicacion.backend.database.database import crear_tablas, engine, StockClasificacion
from sqlalchemy.orm import sessionmaker
from aplicacion.frontend.login import LoginWindow

def inicializar_sistema():
    from aplicacion.backend.database.database import DB_PATH
    
    if DB_PATH.exists():
        print("Base de datos existente - Inicialización normal")
        crear_tablas()  
    else:
        print("Base de datos nueva - Creando admin")
        crear_tablas()
        from aplicacion.backend.database.initial import inicializar_usuario_admin
        inicializar_usuario_admin()
    
    Session = sessionmaker(bind=engine)
    s = Session()
    try:
        cat = s.query(StockClasificacion).filter_by(nombre="sin_categoria").first()
        if not cat:
            s.add(StockClasificacion(nombre="sin_categoria",
                                     descripcion="productos sin categoria asignada",
                                     activa=True))
            s.commit()
            print(" Categoría por defecto 'sin_categoria' creada.")
        else:
            print(" Categoría por defecto ya existe.")
    except Exception as e:
        s.rollback()
        print(f" Error al crear categoría por defecto: {e}")
    finally:
        s.close()

def inicializar_snap_en_hilo():
    import threading
    
    def snap_worker():
        try:
            print("SNAP: Iniciando en hilo separado...")
            
            from aplicacion.backend.backup.snap.snap import init_snap, start_snap
            
            snap_instance = init_snap()
            if snap_instance:
                success = start_snap()
                if success:
                    print("SNAP: Sistema iniciado en hilo separado")
                else:
                    print(" SNAP: Iniciado pero falló backup inicial")
                return snap_instance
            else:
                print(" SNAP: No se pudo inicializar")
                return None
                
        except Exception as e:
            print(f"SNAP: Error en hilo - {e}")
            print(" La aplicación continúa funcionando normalmente")
            return None
    
    snap_thread = threading.Thread(target=snap_worker, daemon=True)
    snap_thread.start()
    
    print(" SNAP: Hilo de backup lanzado en segundo plano")
    return snap_thread

def main():
    inicializar_sistema()

    app = QApplication(sys.argv)

    icon_path = Path(__file__).resolve().parent / "frontend" / "iconos" / "favicon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        print(f"Favicon cargado correctamente desde: {icon_path}")
    else:
        print(f"[WARN] No se encontró favicon en: {icon_path}")

    snap_thread = inicializar_snap_en_hilo()

    login = LoginWindow(app)

    if hasattr(login, "login_success"):
        def on_login_success(usuario):
            from aplicacion.frontend.main_windows import MainWindow
            mw = MainWindow(app, usuario=usuario, icon_path=str(icon_path))
            mw.show()
            login.close()
        login.login_success.connect(on_login_success)

    login.show()
    
    try:
        sys.exit(app.exec())
    finally:
        print(" Aplicación finalizada")

def manual_backup():
    try:
        from aplicacion.backend.backup.snap.snap import manual_backup as snap_manual
        return snap_manual()
    except Exception as e:
        print(f" Error en backup manual: {e}")
        return False

def get_snap_status():
    try:
        from aplicacion.backend.backup.snap.snap import get_snap_instance
        instance = get_snap_instance()
        if instance:
            return {
                "enabled": True,
                "running": instance.running,
                "database_path": instance.database_path,
                "recipient": instance.recipient_email,
                "last_backup": instance.get_last_backup_date()
            }
        return {"enabled": False}
    except Exception:
        return {"enabled": False, "error": True}

def cleanup_snap_temp_files():
    try:
        from aplicacion.backend.backup.snap.snap import cleanup_all_temp_files
        return cleanup_all_temp_files()
    except Exception as e:
        print(f" Error limpiando archivos temporales: {e}")
        return 0

if __name__ == "__main__":
    main()