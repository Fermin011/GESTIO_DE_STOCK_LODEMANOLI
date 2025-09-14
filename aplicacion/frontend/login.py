import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QLinearGradient, QColor, QBrush, QPixmap, QRegion, QIcon

from aplicacion.frontend.main_windows import MainWindow
from aplicacion.backend.usuarios.usuarios import controller
from aplicacion.backend.usuarios.roles.permisos_manager import PermisosManager


class LoginWindow(QWidget):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowTitle("LO DE MANOLI - Iniciar Sesión")
        self.setFixedSize(500, 600)

        BASE_DIR = Path(__file__).resolve().parent
        favicon_path = BASE_DIR / "iconos" / "favicon.png"
        lo_de_manoli_path = BASE_DIR / "Lo de manoli.png"

        try:
            favicon = QIcon(str(favicon_path))
            if not favicon.isNull():
                self.setWindowIcon(favicon)
                self.app.setWindowIcon(favicon)
                import ctypes
                myappid = "lodemanoli.sistema.gestion.1.0"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 102, 204))
        gradient.setColorAt(1, QColor(0, 51, 153))
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

        container = QWidget(self)
        container.setFixedSize(400, 500)
        container.move(50, 50)
        container.setStyleSheet("background-color: white; border-radius: 15px;")
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setStyleSheet("""
            QLabel { background-color: #21AFBD; border-radius: 10px; border: 3px solid #FFFFFF; }
        """)
        try:
            pixmap = QPixmap(str(lo_de_manoli_path))
            if not pixmap.isNull():
                scaled = pixmap.scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled)
                region = QRegion(3, 3, 54, 54, QRegion.RegionType.Ellipse)
                icon_label.setMask(region)
        except Exception:
            pass

        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container = QHBoxLayout()
        icon_container.addStretch(); icon_container.addWidget(icon_label); icon_container.addStretch()
        icon_widget = QWidget(); icon_widget.setLayout(icon_container)
        icon_widget.setStyleSheet("margin-top: 1px;")
        layout.addWidget(icon_widget)

        title = QLabel("LO DE MANOLI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #0033cc; font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("Sistema de Gestión Comercial")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray; font-size: 14px;")
        layout.addWidget(subtitle)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario...")
        self.user_input.setFixedHeight(35)
        self.user_input.setFixedWidth(341)
        self.user_input.setStyleSheet("""
            border: 2px solid black; border-radius: 2px; padding-left: 8px; font-size: 14px; color: black;
        """)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña...")
        self.pass_input.setFixedHeight(35)
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("""
            border: 2px solid black; border-radius: 2px; padding-left: 8px; font-size: 14px; color: black;
        """)

        toggle_button = QPushButton("👁")
        toggle_button.setFixedSize(35, 35)
        toggle_button.setStyleSheet("border: none; font-size: 18px; background-color: transparent;")
        toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_button.clicked.connect(self._toggle_password)

        pass_layout = QHBoxLayout()
        pass_layout.addWidget(self.pass_input)
        pass_layout.addWidget(toggle_button)

        self.remember_checkbox = QCheckBox("Recordar usuario")
        self.remember_checkbox.setStyleSheet("margin-top: 10px; font-size: 13px;")

        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setFixedHeight(40)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton { background-color: #1b8bb4; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: bold; }
            QPushButton:hover { background-color: #147aa0; }
            QPushButton:pressed { background-color: #0f5e7b; }
        """)
        self.login_button.clicked.connect(self.login_user)

        self.recover_button = QPushButton("¿Olvidaste tu contraseña?")
        self.recover_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.recover_button.setStyleSheet("""
            QPushButton { background: transparent; color: #1b8bb4; border: none; font-size: 13px; text-decoration: underline; }
            QPushButton:hover { color: #147aa0; }
        """)
        self.recover_button.clicked.connect(self.recover_password)

        version_label = QLabel("Versión 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet("color: gray; font-size: 12px; margin-top: 5px;")

        layout.addWidget(self.user_input)
        layout.addLayout(pass_layout)
        layout.addWidget(self.remember_checkbox)
        layout.addWidget(self.login_button)
        layout.addWidget(self.recover_button)
        layout.addWidget(version_label)

        self.user_input.returnPressed.connect(self.login_user)
        self.pass_input.returnPressed.connect(self.login_user)

        # Inicializar sistema de roles por defecto si es necesario
        self._inicializar_roles_por_defecto()

    def _inicializar_roles_por_defecto(self):
        """
        Crear roles por defecto si no existen (solo en el primer arranque)
        """
        try:
            from aplicacion.backend.usuarios.roles import controller as roles_controller
            roles_existentes = roles_controller.listar_roles_controller()
            if not roles_existentes or len(roles_existentes) == 0:
                resultado = roles_controller.crear_roles_por_defecto_controller()
                print(f"Sistema de roles inicializado: {resultado}")
        except Exception as e:
            print(f"Error al inicializar roles por defecto: {e}")

    def _crear_permisos_manager(self, user_obj) -> PermisosManager:
        """
        Crea el PermisosManager con toda la información del usuario logueado
        """
        try:
            # Crear el diccionario user_info con la información completa del usuario
            user_info = {
                "id": getattr(user_obj, "id", None),
                "nombre_usuario": getattr(user_obj, "nombre_usuario", ""),
                "rol_id": getattr(user_obj, "rol_id", None),
                "nombre_completo": getattr(user_obj, "nombre_completo", ""),
                "email": getattr(user_obj, "email", ""),
            }
            
            # Crear la instancia del PermisosManager
            permisos_manager = PermisosManager(user_info)
            
            print(f"PermisosManager creado para usuario: {user_info['nombre_usuario']} (ID: {user_info['id']})")
            print(f"Rol ID: {user_info['rol_id']}, Es admin: {permisos_manager.is_admin}")
            
            return permisos_manager
                
        except Exception as e:
            print(f"Error creando PermisosManager: {e}")
            return None

    def _toggle_password(self):
        if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

    def login_user(self):
        usuario = self.user_input.text().strip()
        password = self.pass_input.text()

        if not usuario or not password:
            QMessageBox.warning(self, "Faltan datos", "Completá usuario y contraseña.")
            return

        try:
            # Autenticar usuario
            user_obj = controller.login_usuario_controller(usuario, password)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al intentar iniciar sesión:\n{e}")
            return

        if user_obj:
            # Crear PermisosManager con los datos del usuario
            permisos_manager = self._crear_permisos_manager(user_obj)
            
            if not permisos_manager:
                QMessageBox.warning(
                    self, 
                    "Error de configuración", 
                    "Error al cargar permisos del usuario. Contacte al administrador."
                )
                return
            
            # Verificar que el usuario tenga al menos algunos permisos o sea admin
            if not permisos_manager.is_admin:
                # Verificar si tiene algún permiso
                tiene_permisos = any(
                    any(acciones.values()) for acciones in permisos_manager.permisos.values()
                )
                
                if not tiene_permisos:
                    QMessageBox.warning(
                        self, 
                        "Sin permisos", 
                        "Usuario sin permisos asignados. Contacte al administrador."
                    )
                    return

            # Mostrar información de debug sobre permisos
            permisos_manager.imprimir_permisos()

            # Crear MainWindow pasando el PermisosManager
            self.main_window = MainWindow(self.app, usuario, permisos_manager=permisos_manager)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Error de login", "Usuario o contraseña incorrectos")

    def recover_password(self):
        usuario = self.user_input.text().strip()
        if not usuario:
            QMessageBox.warning(self, "Campo vacío", "Ingresá el nombre de usuario para recuperar la contraseña.")
            return

        try:
            ok = controller.recuperar_password_controller(usuario)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante la recuperación:\n{e}")
            return

        if ok:
            QMessageBox.information(self, "Recuperación enviada",
                                    "Te enviamos la contraseña al email registrado de ese usuario.")
        else:
            QMessageBox.warning(self, "Usuario inválido",
                                "No existe ese usuario o no tiene email registrado.")


# ===== Demo =====
if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow(app)
    login.show()
    sys.exit(app.exec())