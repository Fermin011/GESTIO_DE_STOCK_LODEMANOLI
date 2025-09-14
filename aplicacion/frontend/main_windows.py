from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QStackedWidget, QLabel, QFrame, QMessageBox
)

from aplicacion.frontend.stock import StockTab
from aplicacion.frontend.ventas import VentasTab
from aplicacion.frontend.metricas import MetricasTab
from aplicacion.frontend.style import apply_theme
from aplicacion.backend.usuarios.roles.permisos_manager import PermisosManager

# Pestañas opcionales
try:
    from aplicacion.frontend.caja import CajaTab
except ImportError:
    CajaTab = None

try:
    from aplicacion.frontend.usuario import UsuarioTab
except ImportError:
    UsuarioTab = None

try:
    from aplicacion.frontend.costos import CostosTab
except ImportError:
    CostosTab = None

try:
    from aplicacion.frontend.administrador import AdministradorTab
except ImportError:
    AdministradorTab = None

# NUEVA: Perfil
try:
    from aplicacion.frontend.perfil import PerfilTab
except ImportError:
    PerfilTab = None


class MainWindow(QMainWindow):
    def __init__(self, app, usuario: str | None = None, icon_path: str | None = None, permisos_manager: PermisosManager | None = None):
        """
        permisos_manager: Instancia de PermisosManager con todos los permisos del usuario
        """
        super().__init__()
        self.app = app
        self.usuario = usuario or "Usuario"
        self.permisos_manager = permisos_manager
        
        # Información del usuario desde el PermisosManager
        if self.permisos_manager:
            user_info = self.permisos_manager.user_info
            self.user_info = user_info
            self.rol_id = user_info.get("rol_id", 0)
            self.rol_nombre = "Administrador" if self.rol_id == 1 else "Empleado"
            self.is_admin = self.permisos_manager.is_admin
        else:
            self.user_info = {}
            self.rol_id = 0
            self.rol_nombre = "Sin permisos"
            self.is_admin = False

        # Favicon
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        else:
            fallback = Path(__file__).resolve().parent / "iconos" / "favicon.png"
            self.setWindowIcon(QIcon(str(fallback)))

        # Tema
        self.current_theme = "dark"
        apply_theme(self.app, self.current_theme)

        self.setWindowTitle("LO DE MANOLI - Sistema de Gestión")
        self.showMaximized()

        # Layout principal
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # ===== SIDEBAR =====
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)

        # Estilo común para botones
        sidebar_button_style = """
            QPushButton {
                background-color: #367B94;
                border: 2px solid #449BBA;
                border-radius: 8px;
                padding: 8px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3f8daa;
            }
            QPushButton:checked {
                background-color: #5BD4FF;
                border: 2px solid #4AC5F0;
                color: #1a1a1a;
            }
            QPushButton:disabled {
                background-color: #666666;
                border: 2px solid #888888;
                color: #cccccc;
            }
        """

        # Título
        title_label = QLabel("<b>LO DE MANOLI</b>")
        sidebar_layout.addWidget(title_label)
        sidebar_layout.addSpacing(20)

        # Botones de navegación
        self.btn_stock = QPushButton("📦 Gestión de Stock")
        self.btn_ventas = QPushButton("🛒 Punto de Venta")
        self.btn_caja = QPushButton("💰 Caja")
        self.btn_metricas = QPushButton("📊 Métricas y Reportes")
        self.btn_usuario = QPushButton("👤 Usuario")
        self.btn_costos = QPushButton("💸 Costos")
        self.btn_administrador = QPushButton("⚙️ Administrador")

        # NUEVO botón de PERFIL (muestra nombre + rol)
        self.btn_perfil = QPushButton(f"{self.usuario} ({self.rol_nombre})")

        # Aplicar estilos y propiedades comunes
        all_buttons = [
            self.btn_stock, self.btn_ventas, self.btn_caja, self.btn_metricas,
            self.btn_usuario, self.btn_costos, self.btn_administrador, self.btn_perfil
        ]
        for btn in all_buttons:
            btn.setStyleSheet(sidebar_button_style)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # APLICAR CONTROL DE ACCESO BASADO EN PERMISOS
        self._setup_access_control()

        # Botón por defecto activo
        self.btn_ventas.setChecked(True)

        # Agregar botones al sidebar (solo los habilitados serán visibles)
        sidebar_layout.addWidget(self.btn_stock)
        sidebar_layout.addWidget(self.btn_ventas)
        sidebar_layout.addWidget(self.btn_caja)
        sidebar_layout.addWidget(self.btn_metricas)
        sidebar_layout.addWidget(self.btn_usuario)
        sidebar_layout.addWidget(self.btn_costos)
        sidebar_layout.addWidget(self.btn_administrador)

        sidebar_layout.addStretch()

        # Botón pequeño para tema
        self.toggle_theme_btn = QPushButton("🌙")
        self.toggle_theme_btn.setFixedSize(35, 35)
        self.toggle_theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A4A4A;
                border: 2px solid #6A6A6A;
                border-radius: 17px;
                font-size: 16px;
                color: white;
            }
            QPushButton:hover { background-color: #5A5A5A; border: 2px solid #7A7A7A; }
            QPushButton:pressed { background-color: #3A3A3A; }
        """)
        self.toggle_theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_theme_btn.setToolTip("Cambiar tema")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        sidebar_layout.addWidget(self.toggle_theme_btn)

        # === NUEVO: botón de Perfil con nombre/rol (navega al tab Perfil) ===
        sidebar_layout.addWidget(self.btn_perfil)

        # Cerrar sesión
        logout_btn = QPushButton("🚪 Cerrar Sesión")
        logout_btn.setStyleSheet("""
            QPushButton {
                color: red;
                background: none;
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.15);
                border-radius: 6px;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        sidebar_layout.addWidget(logout_btn)

        # ===== ÁREA CENTRAL =====
        self.stack = QStackedWidget()

        # Crear pestañas con permisos
        self._create_tabs()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, stretch=1)

    def _setup_access_control(self):
        """Configurar control de acceso basado en permisos"""
        if not self.permisos_manager:
            # Si no hay permisos manager, deshabilitar todo excepto ventas
            for btn in [self.btn_stock, self.btn_caja, self.btn_metricas, 
                       self.btn_usuario, self.btn_costos, self.btn_administrador]:
                btn.setEnabled(False)
                btn.setVisible(False)
            return

        # STOCK - Requiere permiso de "ver" en stock
        can_access_stock = self.permisos_manager.puede_ver_stock()
        self.btn_stock.setEnabled(can_access_stock)
        self.btn_stock.setVisible(can_access_stock)
        if not can_access_stock:
            self.btn_stock.setToolTip("Sin permisos para gestión de stock")

        # VENTAS - Requiere permiso de "ver" en ventas
        can_access_ventas = self.permisos_manager.puede_ver_ventas()
        self.btn_ventas.setEnabled(can_access_ventas)
        self.btn_ventas.setVisible(can_access_ventas)
        if not can_access_ventas:
            self.btn_ventas.setToolTip("Sin permisos para punto de venta")

        # CAJA - Requiere permiso de "abrir" en caja (según tu especificación)
        can_access_caja = self.permisos_manager.puede_abrir_caja()
        self.btn_caja.setEnabled(can_access_caja)
        self.btn_caja.setVisible(can_access_caja)
        if not can_access_caja:
            self.btn_caja.setToolTip("Sin permisos para gestión de caja")

        # MÉTRICAS - Requiere permiso de "ver" en reportes
        can_access_metricas = self.permisos_manager.puede_ver_reportes()
        self.btn_metricas.setEnabled(can_access_metricas)
        self.btn_metricas.setVisible(can_access_metricas)
        if not can_access_metricas:
            self.btn_metricas.setToolTip("Sin permisos para métricas y reportes")

        # USUARIOS - Requiere permiso de "ver" en usuarios
        can_access_usuarios = self.permisos_manager.puede_ver_usuarios()
        self.btn_usuario.setEnabled(can_access_usuarios)
        self.btn_usuario.setVisible(can_access_usuarios)
        if not can_access_usuarios:
            self.btn_usuario.setToolTip("Sin permisos para gestión de usuarios")

        # COSTOS - Requiere permiso de "ver" en configuración (ya que costos es parte de configuración avanzada)
        can_access_costos = self.permisos_manager.puede_ver_configuracion()
        self.btn_costos.setEnabled(can_access_costos)
        self.btn_costos.setVisible(can_access_costos)
        if not can_access_costos:
            self.btn_costos.setToolTip("Sin permisos para gestión de costos")

        # ADMINISTRADOR - Solo admins pueden acceder
        can_access_admin = self.permisos_manager.is_admin
        self.btn_administrador.setEnabled(can_access_admin)
        self.btn_administrador.setVisible(can_access_admin)
        if not can_access_admin:
            self.btn_administrador.setToolTip("Solo administradores")

        # PERFIL - Todos pueden acceder a su perfil
        self.btn_perfil.setEnabled(True)
        self.btn_perfil.setVisible(True)

        # Buscar un botón habilitado para seleccionar por defecto
        self._set_default_tab()

    def _set_default_tab(self):
        """Establecer la pestaña por defecto basada en permisos"""
        # Prioridad: Ventas > Stock > Caja > Métricas > Usuario > Perfil
        if self.btn_ventas.isEnabled():
            self.btn_ventas.setChecked(True)
        elif self.btn_stock.isEnabled():
            self.btn_stock.setChecked(True)
        elif self.btn_caja.isEnabled():
            self.btn_caja.setChecked(True)
        elif self.btn_metricas.isEnabled():
            self.btn_metricas.setChecked(True)
        elif self.btn_usuario.isEnabled():
            self.btn_usuario.setChecked(True)
        else:
            # Si no tiene acceso a nada más, al menos puede ver su perfil
            self.btn_perfil.setChecked(True)

    def _create_tabs(self):
        """Crear pestañas pasando el PermisosManager a cada una"""
        
        # Pestañas base
        self.stock_tab = StockTab()
        self.ventas_tab = VentasTab()
        self.metricas_tab = MetricasTab()

        # Pasar el PermisosManager a las pestañas que lo necesiten
        if self.permisos_manager:
            # Si las pestañas tienen método para configurar permisos, llamarlo
            for tab in [self.stock_tab, self.ventas_tab, self.metricas_tab]:
                if hasattr(tab, 'set_permisos_manager'):
                    tab.set_permisos_manager(self.permisos_manager)

        # Pestañas opcionales
        if CajaTab and self.permisos_manager and self.permisos_manager.puede_abrir_caja():
            self.caja_tab = CajaTab()
            if hasattr(self.caja_tab, 'set_permisos_manager'):
                self.caja_tab.set_permisos_manager(self.permisos_manager)
        else:
            self.caja_tab = self.create_placeholder_tab("💰 CAJA - SIN PERMISOS")

        if UsuarioTab and self.permisos_manager and self.permisos_manager.puede_ver_usuarios():
            self.usuario_tab = UsuarioTab()
            if hasattr(self.usuario_tab, 'set_permisos_manager'):
                self.usuario_tab.set_permisos_manager(self.permisos_manager)
            # También configurar usuario actual para compatibilidad
            if hasattr(self.usuario_tab, 'set_current_user'):
                self.usuario_tab.set_current_user(self.user_info)
        else:
            self.usuario_tab = self.create_placeholder_tab("👤 USUARIOS - SIN PERMISOS")

        if CostosTab and self.permisos_manager and self.permisos_manager.puede_ver_configuracion():
            self.costos_tab = CostosTab()
            if hasattr(self.costos_tab, 'set_permisos_manager'):
                self.costos_tab.set_permisos_manager(self.permisos_manager)
        else:
            self.costos_tab = self.create_placeholder_tab("💸 COSTOS - SIN PERMISOS")

        if AdministradorTab and self.permisos_manager and self.permisos_manager.is_admin:
            self.administrador_tab = AdministradorTab()
            if hasattr(self.administrador_tab, 'set_permisos_manager'):
                self.administrador_tab.set_permisos_manager(self.permisos_manager)
        else:
            self.administrador_tab = self.create_placeholder_tab("⚙️ ADMINISTRADOR - SIN PERMISOS")

        # NUEVA pestaña Perfil - todos pueden acceder
        if PerfilTab:
            self.perfil_tab = PerfilTab(self.user_info)
            if hasattr(self.perfil_tab, 'set_permisos_manager'):
                self.perfil_tab.set_permisos_manager(self.permisos_manager)
        else:
            self.perfil_tab = self.create_placeholder_tab("🧑‍💼 PERFIL")

        # Agregar al stack (respeta orden de índices)
        self.stack.addWidget(self.stock_tab)         # 0
        self.stack.addWidget(self.ventas_tab)        # 1
        self.stack.addWidget(self.caja_tab)          # 2
        self.stack.addWidget(self.metricas_tab)      # 3
        self.stack.addWidget(self.usuario_tab)       # 4
        self.stack.addWidget(self.costos_tab)        # 5
        self.stack.addWidget(self.administrador_tab) # 6
        self.stack.addWidget(self.perfil_tab)        # 7

        # Establecer pestaña inicial basada en permisos
        if self.btn_ventas.isEnabled():
            self.stack.setCurrentIndex(1)  # Punto de Venta
        elif self.btn_stock.isEnabled():
            self.stack.setCurrentIndex(0)  # Stock
        else:
            # Buscar la primera pestaña habilitada
            for i, btn in enumerate([self.btn_stock, self.btn_ventas, self.btn_caja, 
                                   self.btn_metricas, self.btn_usuario, self.btn_costos, 
                                   self.btn_administrador]):
                if btn.isEnabled():
                    self.stack.setCurrentIndex(i)
                    break
            else:
                # Si ninguna está habilitada, ir a perfil
                self.stack.setCurrentIndex(7)

        # Conexiones de navegación
        self.btn_stock.clicked.connect(lambda: self.switch_view(0, self.btn_stock))
        self.btn_ventas.clicked.connect(lambda: self.switch_view(1, self.btn_ventas))
        self.btn_caja.clicked.connect(lambda: self.switch_view(2, self.btn_caja))
        self.btn_metricas.clicked.connect(lambda: self.switch_view(3, self.btn_metricas))
        self.btn_usuario.clicked.connect(lambda: self.switch_view(4, self.btn_usuario))
        self.btn_costos.clicked.connect(lambda: self.switch_view(5, self.btn_costos))
        self.btn_administrador.clicked.connect(lambda: self.switch_view(6, self.btn_administrador))
        self.btn_perfil.clicked.connect(lambda: self.switch_view(7, self.btn_perfil))

    def create_placeholder_tab(self, title: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px; color: red;")
        layout.addWidget(title_label)

        content = QLabel("No tiene permisos para acceder a esta sección")
        content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content.setStyleSheet("font-size: 16px; color: gray;")
        layout.addWidget(content)

        if self.permisos_manager:
            permisos_info = QLabel(f"Usuario: {self.permisos_manager.user_info.get('nombre_usuario')}\nRol: {self.rol_nombre}")
            permisos_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            permisos_info.setStyleSheet("font-size: 14px; color: gray; margin-top: 20px;")
            layout.addWidget(permisos_info)

        layout.addStretch()
        return widget

    def switch_view(self, index: int, active_btn: QPushButton):
        # Verificar si el botón está habilitado
        if not active_btn.isEnabled():
            QMessageBox.warning(
                self, "Acceso Denegado", 
                "No tiene permisos para acceder a esta sección."
            )
            return

        # Caso especial: volver al menú principal de stock si ya estás en stock
        if index == 0 and self.stack.currentIndex() == 0:
            current_widget = self.stock_tab.stack.currentWidget() if hasattr(self.stock_tab, 'stack') else None
            if hasattr(self.stock_tab, 'main_widget') and current_widget != self.stock_tab.main_widget:
                if hasattr(self.stock_tab, 'switch_to_tab'):
                    self.stock_tab.switch_to_tab("GESTIÓN DE STOCK")
                return

        self.stack.setCurrentIndex(index)

        # Desmarcar todos y marcar activo
        for btn in [
            self.btn_stock, self.btn_ventas, self.btn_caja, self.btn_metricas,
            self.btn_usuario, self.btn_costos, self.btn_administrador, self.btn_perfil
        ]:
            btn.setChecked(False)
        active_btn.setChecked(True)

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        apply_theme(self.app, self.current_theme)

    def logout(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText("¿Estás seguro de que quieres cerrar sesión?")
        msg.setWindowTitle("Confirmar cierre de sesión")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)

        if msg.exec() == QMessageBox.StandardButton.Yes:
            self.app.setStyleSheet("")
            from aplicacion.frontend.login import LoginWindow
            self.login_window = LoginWindow(self.app)
            self.login_window.show()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.isFullScreen():
                self.showMaximized()
            elif self.isMaximized():
                self.showNormal()
        super().keyPressEvent(event)