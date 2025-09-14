from __future__ import annotations
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
    QProgressBar, QTabWidget, QTextEdit, QSplitter, QLineEdit,
    QFormLayout, QGroupBox
)
from datetime import datetime
import re

# Importar el controller del backend
from aplicacion.backend.usuarios.usuarios import controller

# ====== Paleta y estilos ======
BG_DARK = "#2B2D31"
FRAME_BG = "#36393F"
CARD_BG = "#FFFFFF"
CARD_SUCCESS = "#E8F5E8"
CARD_WARNING = "#FFF3E0"
CARD_ERROR = "#FFEBEE"
CARD_INFO = "#E3F2FD"
TEXT_WHITE = "#FFFFFF"
TEXT_DARK = "#2C2C2C"
TEXT_MUTED = "#72767D"
TEXT_SUCCESS = "#4CAF50"
TEXT_WARNING = "#FF9800"
TEXT_ERROR = "#F44336"
TEXT_INFO = "#2196F3"
ACCENT_BLUE = "#5865F2"
ACCENT_GREEN = "#57F287"
ACCENT_PURPLE = "#9C27B0"

QSS = f"""
QWidget#Root {{
    background: {BG_DARK};
    font-family: 'Segoe UI', Arial, sans-serif;
}}

QFrame#MainFrame {{
    background: {FRAME_BG};
    border: 1px solid #4F545C;
    border-radius: 12px;
}}

QLabel.H1 {{
    color: {TEXT_WHITE};
    font-size: 28px;
    font-weight: 700;
    margin: 8px 0px;
}}

QLabel.Section {{
    color: {TEXT_WHITE};
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QFrame.MetricCard {{
    background: {CARD_BG};
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 12px;
}}
QFrame.MetricCard.success {{ background: {CARD_SUCCESS}; border-color: {TEXT_SUCCESS}; }}
QFrame.MetricCard.warning {{ background: {CARD_WARNING}; border-color: {TEXT_WARNING}; }}
QFrame.MetricCard.error   {{ background: {CARD_ERROR};   border-color: {TEXT_ERROR}; }}
QFrame.MetricCard.info    {{ background: {CARD_INFO};    border-color: {TEXT_INFO}; }}

QLabel.MetricValue {{ color: {TEXT_DARK}; font-size: 24px; font-weight: 700; }}
QLabel.MetricLabel {{ color: {TEXT_MUTED}; font-size: 12px; font-weight: 500; text-transform: uppercase; }}
QLabel.MetricSubtitle {{ color: {TEXT_MUTED}; font-size: 11px; font-style: italic; }}

QPushButton.ActionBtn {{
    background: {ACCENT_BLUE};
    color: {TEXT_WHITE};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}}
QPushButton.ActionBtn:hover {{ background: #4752C4; }}
QPushButton.ActionBtn:pressed {{ background: #3C45A3; }}
QPushButton.ActionBtn.success {{ background: {TEXT_SUCCESS}; }}
QPushButton.ActionBtn.warning {{ background: {TEXT_WARNING}; }}
QPushButton.ActionBtn.error   {{ background: {TEXT_ERROR}; }}

QLineEdit {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 500;
    color: {TEXT_DARK};
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: {ACCENT_BLUE}; }}

QTableWidget#UsuariosTable {{
    background: {CARD_BG};
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    gridline-color: #F0F0F0;
}}
QHeaderView::section {{
    background: #F8F9FA;
    border: none;
    border-bottom: 2px solid #E9ECEF;
    padding: 8px;
    font-weight: 600;
    color: {TEXT_DARK};
}}
QTableWidget::item {{ padding: 6px; color: {TEXT_DARK}; }}
QTableWidget::item:selected {{ background: #E3F2FD; }}

QTextEdit.LogArea {{
    background: {FRAME_BG};
    border: 1px solid #4F545C;
    border-radius: 6px;
    color: {TEXT_WHITE};
    font-family: 'Consolas', monospace;
    font-size: 11px;
}}

QTabWidget::pane {{
    border: 1px solid #4F545C;
    border-radius: 6px;
    background: {FRAME_BG};
}}
QTabBar::tab {{
    background: #4F545C;
    color: {TEXT_WHITE};
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{ background: {ACCENT_BLUE}; }}

QProgressBar {{
    border: 1px solid #D0D0D0;
    border-radius: 4px;
    text-align: center;
    font-weight: 600;
}}
QProgressBar::chunk {{ background: {ACCENT_GREEN}; border-radius: 3px; }}

QGroupBox {{
    color: {TEXT_WHITE};
    font-weight: 600;
    border: 2px solid #4F545C;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
}}
"""

class MetricCard(QFrame):
    def __init__(self, title: str, value: str = "N/A", subtitle: str = "", status: str = "normal"):
        super().__init__()
        self.setObjectName("MetricCard")
        self.setProperty("class", f"MetricCard {status}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricLabel")
        self.title_label.setProperty("class", "MetricLabel")
        layout.addWidget(self.title_label)

        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setProperty("class", "MetricValue")
        layout.addWidget(self.value_label)

        self.subtitle_label = None
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("MetricSubtitle")
            self.subtitle_label.setProperty("class", "MetricSubtitle")
            layout.addWidget(self.subtitle_label)

    def update_value(self, value: str, subtitle: str = "", status: str = "normal"):
        self.value_label.setText(value)
        if subtitle:
            if self.subtitle_label is None:
                self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setText(subtitle)
        self.setProperty("class", f"MetricCard {status}")
        self.style().unpolish(self)
        self.style().polish(self)

class UsuarioTab(QWidget):
    """Vista principal de gestión de usuarios (sin Login)"""

    data_updated = pyqtSignal()
    user_logged_in = pyqtSignal(dict)  # disponible si quisieras conectar señales externas

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Root")
        self.setStyleSheet(QSS)

        # Estado
        self.is_loading = False
        self.last_update = None
        self.current_user: dict | None = None
        self.selected_user_id = None

        self.init_ui()
        self.setup_connections()
        self.load_initial_data()

        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.refresh_user_metrics)
        self.auto_timer.start(300000)  # 5 min

    # ===== API pública para que Login/MainWindow seteen la sesión =====
    def set_current_user(self, user_info: dict | None):
        """
        Espera un dict como:
        {"id": int, "nombre_usuario": str, "rol_id": int}
        """
        self.current_user = user_info
        # actualizo UI
        if user_info:
            self.current_user_label.setText(f"Usuario: {user_info.get('nombre_usuario', '—')}")
            self.usuario_actual_card.update_value(
                user_info.get("nombre_usuario", "—"),
                f"ID: {user_info.get('id', '—')}",
                "success"
            )
            self.log_message(f"Sesión iniciada: {user_info.get('nombre_usuario')} (ID: {user_info.get('id')})")
        else:
            self.current_user_label.setText("Sin usuario logueado")
            self.usuario_actual_card.update_value("Sin login", "No hay sesión", "warning")
            self.log_message("Sesión finalizada")
        self.refresh_user_metrics()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        header = self.create_header()
        main_layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Vertical)

        metrics_panel = self.create_metrics_panel()
        splitter.addWidget(metrics_panel)

        tabs_panel = self.create_tabs_panel()
        splitter.addWidget(tabs_panel)

        splitter.setSizes([250, 550])
        main_layout.addWidget(splitter)

    def create_header(self):
        header = QFrame()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("👤 GESTIÓN DE USUARIOS")
        title.setObjectName("H1")
        title.setProperty("class", "H1")
        layout.addWidget(title)

        layout.addStretch()

        self.current_user_label = QLabel("Sin usuario logueado")
        self.current_user_label.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 14px; font-weight: 500;")
        layout.addWidget(self.current_user_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)

        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setObjectName("ActionBtn")
        self.refresh_btn.setProperty("class", "ActionBtn")
        layout.addWidget(self.refresh_btn)

        return header

    def create_metrics_panel(self):
        panel = QFrame()
        panel.setObjectName("MainFrame")
        panel.setProperty("class", "MainFrame")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        title = QLabel("ESTADÍSTICAS DE USUARIOS")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.total_usuarios_card = MetricCard("TOTAL USUARIOS", "0", "Usuarios registrados")
        cards_layout.addWidget(self.total_usuarios_card)

        self.usuario_actual_card = MetricCard("SESIÓN ACTUAL", "Sin login", "Usuario logueado")
        cards_layout.addWidget(self.usuario_actual_card)

        self.sistema_estado_card = MetricCard("ESTADO SISTEMA", "Activo", "Gestión de usuarios")
        cards_layout.addWidget(self.sistema_estado_card)

        self.ultima_actualizacion_card = MetricCard("ÚLTIMA ACTUALIZACIÓN", "Nunca", "Datos de usuarios")
        cards_layout.addWidget(self.ultima_actualizacion_card)

        layout.addLayout(cards_layout)
        return panel

    def create_tabs_panel(self):
        """
        0: Registro
        1: Usuarios
        2: Recuperar
        3: Administración
        4: Log
        """
        self.tabs = QTabWidget()

        register_tab = self.create_register_tab()
        self.tabs.addTab(register_tab, "📝 Registro")

        users_tab = self.create_users_tab()
        self.tabs.addTab(users_tab, "👥 Usuarios")

        recovery_tab = self.create_recovery_tab()
        self.tabs.addTab(recovery_tab, "🔑 Recuperar")

        admin_tab = self.create_admin_tab()
        self.tabs.addTab(admin_tab, "⚙️ Administración")

        log_tab = self.create_log_tab()
        self.tabs.addTab(log_tab, "📝 Log")

        return self.tabs

    # -------------------- TABS --------------------
    def create_register_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)

        register_group = QGroupBox("Registrar Nuevo Usuario")
        register_layout = QFormLayout(register_group)
        register_layout.setSpacing(12)

        self.register_usuario_input = QLineEdit()
        self.register_usuario_input.setPlaceholderText("Nombre de usuario único")
        register_layout.addRow("Usuario:", self.register_usuario_input)

        self.register_email_input = QLineEdit()
        self.register_email_input.setPlaceholderText("email@ejemplo.com")
        register_layout.addRow("Email:", self.register_email_input)

        self.register_password_input = QLineEdit()
        self.register_password_input.setPlaceholderText("Contraseña (mínimo 6 caracteres)")
        self.register_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addRow("Contraseña:", self.register_password_input)

        self.register_confirm_password_input = QLineEdit()
        self.register_confirm_password_input.setPlaceholderText("Repetir contraseña")
        self.register_confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        register_layout.addRow("Confirmar:", self.register_confirm_password_input)

        self.validation_label = QLabel("")
        self.validation_label.setStyleSheet("font-size: 12px; padding: 5px;")
        register_layout.addRow("", self.validation_label)

        buttons_layout = QHBoxLayout()

        self.register_btn = QPushButton("📝 Registrar Usuario")
        self.register_btn.setObjectName("ActionBtn")
        self.register_btn.setProperty("class", "ActionBtn success")
        self.register_btn.setEnabled(False)
        buttons_layout.addWidget(self.register_btn)

        self.clear_register_btn = QPushButton("🧹 Limpiar")
        self.clear_register_btn.setObjectName("ActionBtn")
        self.clear_register_btn.setProperty("class", "ActionBtn")
        buttons_layout.addWidget(self.clear_register_btn)

        buttons_layout.addStretch()
        register_layout.addRow(buttons_layout)

        layout.addWidget(register_group)
        layout.addStretch()
        return tab

    def create_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)

        controls_layout = QHBoxLayout()

        search_label = QLabel("Buscar:")
        controls_layout.addWidget(search_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre de usuario...")
        controls_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("🔍 Buscar")
        self.search_btn.setObjectName("ActionBtn")
        self.search_btn.setProperty("class", "ActionBtn")
        controls_layout.addWidget(self.search_btn)

        self.refresh_users_btn = QPushButton("🔄 Actualizar Lista")
        self.refresh_users_btn.setObjectName("ActionBtn")
        self.refresh_users_btn.setProperty("class", "ActionBtn")
        controls_layout.addWidget(self.refresh_users_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.users_table = QTableWidget()
        self.users_table.setObjectName("UsuariosTable")
        self.users_table.setProperty("class", "UsuariosTable")
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "ID", "Usuario", "Rol ID", "Seleccionar", "Acciones"
        ])

        header = self.users_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.users_table)
        return tab

    def create_recovery_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)

        layout.addStretch()

        recovery_group = QGroupBox("Recuperar Contraseña")
        recovery_layout = QFormLayout(recovery_group)
        recovery_layout.setSpacing(15)

        instructions = QLabel("Ingresa tu nombre de usuario para recibir tu contraseña actual por email.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet(f"color: {TEXT_MUTED}; font-style: italic; padding: 10px;")
        recovery_layout.addRow("", instructions)

        self.recovery_usuario_input = QLineEdit()
        self.recovery_usuario_input.setPlaceholderText("Nombre de usuario")
        self.recovery_usuario_input.setMinimumHeight(40)
        recovery_layout.addRow("Usuario:", self.recovery_usuario_input)

        buttons_layout = QHBoxLayout()

        self.recovery_btn = QPushButton("🔑 Enviar Contraseña")
        self.recovery_btn.setObjectName("ActionBtn")
        self.recovery_btn.setProperty("class", "ActionBtn warning")
        self.recovery_btn.setMinimumHeight(45)
        buttons_layout.addWidget(self.recovery_btn)

        self.clear_recovery_btn = QPushButton("🧹 Limpiar")
        self.clear_recovery_btn.setObjectName("ActionBtn")
        self.clear_recovery_btn.setProperty("class", "ActionBtn")
        self.clear_recovery_btn.setMinimumHeight(45)
        buttons_layout.addWidget(self.clear_recovery_btn)

        recovery_layout.addRow(buttons_layout)

        self.recovery_status_label = QLabel("")
        self.recovery_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.recovery_status_label.setStyleSheet("font-weight: bold; padding: 10px;")
        recovery_layout.addRow("", self.recovery_status_label)

        layout.addWidget(recovery_group)
        layout.addStretch()
        return tab

    def create_admin_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)

        edit_group = QGroupBox("Editar Usuario Seleccionado")
        edit_layout = QFormLayout(edit_group)

        info_label = QLabel("Selecciona un usuario en la tabla de la pestaña 'Usuarios' para editarlo aquí")
        info_label.setStyleSheet("color: #72767D; font-style: italic; padding: 10px;")
        edit_layout.addRow("", info_label)

        self.edit_user_id_label = QLabel("Ninguno seleccionado")
        self.edit_user_id_label.setStyleSheet("font-weight: bold;")
        edit_layout.addRow("ID Usuario:", self.edit_user_id_label)

        self.edit_current_user_label = QLabel("N/A")
        self.edit_current_user_label.setStyleSheet("font-weight: bold;")
        edit_layout.addRow("Usuario Actual:", self.edit_current_user_label)

        self.edit_usuario_input = QLineEdit()
        self.edit_usuario_input.setPlaceholderText("Nuevo nombre de usuario")
        self.edit_usuario_input.setEnabled(False)
        edit_layout.addRow("Nuevo Usuario:", self.edit_usuario_input)

        self.edit_password_input = QLineEdit()
        self.edit_password_input.setPlaceholderText("Nueva contraseña")
        self.edit_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_password_input.setEnabled(False)
        edit_layout.addRow("Nueva Contraseña:", self.edit_password_input)

        self.edit_email_input = QLineEdit()
        self.edit_email_input.setPlaceholderText("Nuevo email")
        self.edit_email_input.setEnabled(False)
        edit_layout.addRow("Nuevo Email:", self.edit_email_input)

        admin_buttons = QHBoxLayout()

        self.save_changes_btn = QPushButton("💾 Guardar Cambios")
        self.save_changes_btn.setObjectName("ActionBtn")
        self.save_changes_btn.setProperty("class", "ActionBtn warning")
        self.save_changes_btn.setEnabled(False)
        admin_buttons.addWidget(self.save_changes_btn)

        self.cancel_edit_btn = QPushButton("❌ Cancelar")
        self.cancel_edit_btn.setObjectName("ActionBtn")
        self.cancel_edit_btn.setProperty("class", "ActionBtn")
        self.cancel_edit_btn.setEnabled(False)
        admin_buttons.addWidget(self.cancel_edit_btn)

        admin_buttons.addStretch()
        edit_layout.addRow(admin_buttons)

        layout.addWidget(edit_group)

        info_group = QGroupBox("Información Detallada")
        info_layout = QVBoxLayout(info_group)

        self.user_info_text = QTextEdit()
        self.user_info_text.setMaximumHeight(200)
        self.user_info_text.setReadOnly(True)
        self.user_info_text.setPlainText("Selecciona un usuario para ver información detallada...")
        info_layout.addWidget(self.user_info_text)

        layout.addWidget(info_group)
        layout.addStretch()
        return tab

    def create_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)

        self.log_area = QTextEdit()
        self.log_area.setObjectName("LogArea")
        self.log_area.setProperty("class", "LogArea")
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        return tab

    # -------------------- CONEXIONES --------------------
    def setup_connections(self):
        self.refresh_btn.clicked.connect(self.refresh_all_data)

        # Registro
        self.register_btn.clicked.connect(self.register_user)
        self.clear_register_btn.clicked.connect(self.clear_register_form)
        self.register_password_input.textChanged.connect(self.validate_register_form)
        self.register_confirm_password_input.textChanged.connect(self.validate_register_form)
        self.register_email_input.textChanged.connect(self.validate_register_form)

        # Usuarios
        self.search_btn.clicked.connect(self.search_users)
        self.refresh_users_btn.clicked.connect(self.refresh_users_table)
        self.search_input.returnPressed.connect(self.search_users)

        # Recuperación
        self.recovery_btn.clicked.connect(self.recover_password)
        self.clear_recovery_btn.clicked.connect(self.clear_recovery_form)
        self.recovery_usuario_input.returnPressed.connect(self.recover_password)

        # Admin
        self.save_changes_btn.clicked.connect(self.save_user_changes)
        self.cancel_edit_btn.clicked.connect(self.cancel_user_edit)

    # -------------------- UTILIDAD --------------------
    def log_message(self, message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}"
        self.log_area.append(formatted_msg)
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)

    def set_loading(self, loading: bool):
        self.is_loading = loading
        self.progress_bar.setVisible(loading)
        self.refresh_btn.setEnabled(not loading)  # <- corregido

        if loading:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

    # -------------------- DATOS --------------------
    def load_initial_data(self):
        self.log_message("Iniciando sistema de gestión de usuarios...")
        self.refresh_all_data()

    def refresh_all_data(self):
        if self.is_loading:
            return
        self.set_loading(True)
        self.log_message("Actualizando datos del sistema...")

        try:
            self.refresh_user_metrics()
            self.refresh_users_table()
            self.last_update = datetime.now()
            self.log_message("Datos actualizados exitosamente")
            self.data_updated.emit()
        except Exception as e:
            self.log_message(f"Error actualizando datos: {str(e)}", "ERROR")
            QMessageBox.warning(self, "Error", f"Error al actualizar datos:\n{str(e)}")
        finally:
            self.set_loading(False)

    def refresh_user_metrics(self):
        try:
            usuarios = controller.listar_usuarios_controller()

            if usuarios:
                total_usuarios = len(usuarios)
                self.total_usuarios_card.update_value(
                    str(total_usuarios),
                    f"{total_usuarios} {'usuario' if total_usuarios == 1 else 'usuarios'}",
                    "success" if total_usuarios > 0 else "normal"
                )
            else:
                self.total_usuarios_card.update_value("0", "Sin usuarios", "warning")

            # sesión actual
            if self.current_user:
                self.usuario_actual_card.update_value(
                    self.current_user.get("nombre_usuario", "—"),
                    f"ID: {self.current_user.get('id', '—')}",
                    "success"
                )
                self.current_user_label.setText(f"Usuario: {self.current_user.get('nombre_usuario', '—')}")
            else:
                self.usuario_actual_card.update_value("Sin login", "No hay sesión", "warning")
                self.current_user_label.setText("Sin usuario logueado")

            self.sistema_estado_card.update_value("Operativo", "Sistema funcionando", "success")

            if self.last_update:
                self.ultima_actualizacion_card.update_value(
                    self.last_update.strftime("%H:%M:%S"),
                    self.last_update.strftime("%Y-%m-%d"),
                    "info"
                )
            else:
                self.ultima_actualizacion_card.update_value("Nunca", "Sin actualizar", "normal")

        except Exception as e:
            self.log_message(f"Error actualizando métricas: {str(e)}", "ERROR")

    # -------------------- VALIDACIONES --------------------
    def validate_email(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_register_form(self):
        usuario = self.register_usuario_input.text().strip()
        email = self.register_email_input.text().strip()
        password = self.register_password_input.text()
        confirm_password = self.register_confirm_password_input.text()

        errors = []
        if usuario and len(usuario) < 3:
            errors.append("Usuario debe tener al menos 3 caracteres")
        if email and not self.validate_email(email):
            errors.append("Email inválido")
        if password and len(password) < 6:
            errors.append("Contraseña debe tener al menos 6 caracteres")
        if password and confirm_password and password != confirm_password:
            errors.append("Las contraseñas no coinciden")

        if errors:
            self.validation_label.setText("❌ " + " | ".join(errors))
            self.validation_label.setStyleSheet("color: #F44336; font-size: 12px; padding: 5px;")
            self.register_btn.setEnabled(False)
        else:
            if usuario and email and password and confirm_password:
                self.validation_label.setText("✅ Formulario válido")
                self.validation_label.setStyleSheet("color: #4CAF50; font-size: 12px; padding: 5px;")
                self.register_btn.setEnabled(True)
            else:
                self.validation_label.setText("")
                self.register_btn.setEnabled(False)

    # -------------------- ACCIONES --------------------
    def register_user(self):
        try:
            usuario = self.register_usuario_input.text().strip()
            email = self.register_email_input.text().strip()
            password = self.register_password_input.text()
            confirm_password = self.register_confirm_password_input.text()

            if not all([usuario, email, password, confirm_password]):
                QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
                return
            if len(usuario) < 3:
                QMessageBox.warning(self, "Error", "El usuario debe tener al menos 3 caracteres")
                return
            if not self.validate_email(email):
                QMessageBox.warning(self, "Error", "Email inválido")
                return
            if len(password) < 6:
                QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres")
                return
            if password != confirm_password:
                QMessageBox.warning(self, "Error", "Las contraseñas no coinciden")
                return

            registrado = controller.registrar_usuario_controller(usuario, password, email)
            if registrado:
                self.log_message(f"Usuario registrado exitosamente: {usuario}")
                QMessageBox.information(self, "Éxito",
                                        f"Usuario '{usuario}' registrado exitosamente!\n\nYa puedes asignarle permisos.")
                self.clear_register_form()
                self.refresh_all_data()
                if hasattr(self, "tabs"):
                    self.tabs.setCurrentIndex(1)  # Usuarios
            else:
                self.log_message(f"Error registrando usuario: {usuario}", "ERROR")
                QMessageBox.warning(
                    self, "Error",
                    f"No se pudo registrar el usuario '{usuario}'.\n\nPosibles causas:\n• El usuario ya existe\n• Error en la base de datos"
                )

        except Exception as e:
            self.log_message(f"Error en registro: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error durante el registro:\n{str(e)}")

    def refresh_users_table(self):
        try:
            usuarios = controller.listar_usuarios_controller()
            if usuarios:
                self.users_table.setRowCount(len(usuarios))
                for row, usuario in enumerate(usuarios):
                    self.users_table.setItem(row, 0, QTableWidgetItem(str(usuario.id)))
                    self.users_table.setItem(row, 1, QTableWidgetItem(usuario.nombre_usuario))
                    self.users_table.setItem(row, 2, QTableWidgetItem(str(usuario.rol_id)))

                    select_btn = QPushButton("👆 Seleccionar")
                    select_btn.setMaximumHeight(30)
                    select_btn.clicked.connect(lambda checked, u_id=usuario.id: self.select_user_for_edit(u_id))
                    self.users_table.setCellWidget(row, 3, select_btn)

                    details_btn = QPushButton("👁️ Ver")
                    details_btn.setMaximumHeight(30)
                    details_btn.clicked.connect(lambda checked, u_id=usuario.id: self.view_user_details(u_id))
                    self.users_table.setCellWidget(row, 4, details_btn)
                self.log_message(f"Tabla de usuarios actualizada: {len(usuarios)} usuarios")
            else:
                self.users_table.setRowCount(0)
                self.log_message("No hay usuarios registrados")
        except Exception as e:
            self.log_message(f"Error actualizando tabla de usuarios: {str(e)}", "ERROR")

    def search_users(self):
        try:
            search_term = self.search_input.text().strip().lower()
            if not search_term:
                self.refresh_users_table()
                return

            usuarios = controller.listar_usuarios_controller()
            if not usuarios:
                self.users_table.setRowCount(0)
                return

            filtered_users = [u for u in usuarios if search_term in u.nombre_usuario.lower()]
            self.users_table.setRowCount(len(filtered_users))

            for row, usuario in enumerate(filtered_users):
                self.users_table.setItem(row, 0, QTableWidgetItem(str(usuario.id)))
                username_item = QTableWidgetItem(usuario.nombre_usuario)
                if search_term in usuario.nombre_usuario.lower():
                    username_item.setBackground(Qt.GlobalColor.yellow)
                self.users_table.setItem(row, 1, username_item)
                self.users_table.setItem(row, 2, QTableWidgetItem(str(usuario.rol_id)))

                select_btn = QPushButton("👆 Seleccionar")
                select_btn.setMaximumHeight(30)
                select_btn.clicked.connect(lambda checked, u_id=usuario.id: self.select_user_for_edit(u_id))
                self.users_table.setCellWidget(row, 3, select_btn)

                details_btn = QPushButton("👁️ Ver")
                details_btn.setMaximumHeight(30)
                details_btn.clicked.connect(lambda checked, u_id=usuario.id: self.view_user_details(u_id))
                self.users_table.setCellWidget(row, 4, details_btn)

            self.log_message(f"Búsqueda completada: {len(filtered_users)} usuarios encontrados para '{search_term}'")
        except Exception as e:
            self.log_message(f"Error en búsqueda: {str(e)}", "ERROR")

    def select_user_for_edit(self, user_id: int):
        try:
            user_obj = controller.obtener_usuario_controller(user_id)
            if user_obj:
                self.selected_user_id = user_id
                self.edit_user_id_label.setText(str(user_obj.id))
                self.edit_current_user_label.setText(user_obj.nombre_usuario)

                self.edit_usuario_input.setEnabled(True)
                self.edit_password_input.setEnabled(True)
                self.edit_email_input.setEnabled(True)
                self.save_changes_btn.setEnabled(True)
                self.cancel_edit_btn.setEnabled(True)

                if hasattr(self, "tabs"):
                    self.tabs.setCurrentIndex(3)  # Administración
                self.log_message(f"Usuario seleccionado para edición: {user_obj.nombre_usuario} (ID: {user_id})")
            else:
                QMessageBox.warning(self, "Error", "No se encontró el usuario")
        except Exception as e:
            self.log_message(f"Error seleccionando usuario: {str(e)}", "ERROR")

    def view_user_details(self, user_id: int):
        try:
            user_obj = controller.obtener_usuario_controller(user_id)
            if user_obj:
                details = f"""
INFORMACIÓN DEL USUARIO
========================

ID: {user_obj.id}
Nombre de Usuario: {user_obj.nombre_usuario}
Rol ID: {user_obj.rol_id}

Estado: Activo
Fecha de consulta: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Nota: Para obtener información adicional como email y teléfono,
se requiere acceso a la tabla de perfiles de usuario.
                """.strip()

                self.user_info_text.setPlainText(details)
                if hasattr(self, "tabs"):
                    self.tabs.setCurrentIndex(3)  # Administración
                self.log_message(f"Consultando detalles de usuario: {user_obj.nombre_usuario}")
            else:
                QMessageBox.warning(self, "Error", "No se encontró el usuario")
        except Exception as e:
            self.log_message(f"Error obteniendo detalles: {str(e)}", "ERROR")

    def save_user_changes(self):
        try:
            if not self.selected_user_id:
                QMessageBox.warning(self, "Error", "No hay usuario seleccionado")
                return

            nuevos_datos = {}
            nuevo_usuario = self.edit_usuario_input.text().strip()
            if nuevo_usuario:
                nuevos_datos["nombre_usuario"] = nuevo_usuario
            nuevo_password = self.edit_password_input.text()
            if nuevo_password:
                nuevos_datos["password"] = nuevo_password
            nuevo_email = self.edit_email_input.text().strip()
            if nuevo_email:
                if not self.validate_email(nuevo_email):
                    QMessageBox.warning(self, "Error", "Email inválido")
                    return
                nuevos_datos["email"] = nuevo_email

            if not nuevos_datos:
                QMessageBox.information(self, "Info", "No hay cambios para guardar")
                return

            changes_text = "\n".join([f"• {key}: {value}" for key, value in nuevos_datos.items()])
            reply = QMessageBox.question(
                self, "Confirmar cambios",
                f"¿Guardar los siguientes cambios?\n\n{changes_text}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                usuario_actualizado = controller.editar_usuario_controller(self.selected_user_id, nuevos_datos)
                if usuario_actualizado:
                    self.log_message(f"Usuario actualizado exitosamente: ID {self.selected_user_id}")
                    QMessageBox.information(self, "Éxito", "Usuario actualizado exitosamente!")
                    self.cancel_user_edit()
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el usuario")

        except Exception as e:
            self.log_message(f"Error guardando cambios: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error guardando cambios:\n{str(e)}")

    def cancel_user_edit(self):
        self.selected_user_id = None
        self.edit_user_id_label.setText("Ninguno seleccionado")
        self.edit_current_user_label.setText("N/A")
        self.edit_usuario_input.clear()
        self.edit_password_input.clear()
        self.edit_email_input.clear()
        self.edit_usuario_input.setEnabled(False)
        self.edit_password_input.setEnabled(False)
        self.edit_email_input.setEnabled(False)
        self.save_changes_btn.setEnabled(False)
        self.cancel_edit_btn.setEnabled(False)
        self.user_info_text.setPlainText("Selecciona un usuario para ver información detallada...")

    def recover_password(self):
        try:
            usuario = self.recovery_usuario_input.text().strip()
            if not usuario:
                self.recovery_status_label.setText("❌ Ingrese un nombre de usuario")
                self.recovery_status_label.setStyleSheet("color: #F44336; font-weight: bold; padding: 10px;")
                return

            exito = controller.recuperar_password_controller(usuario)
            if exito:
                self.recovery_status_label.setText("✅ Contraseña enviada por email")
                self.recovery_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 10px;")
                self.log_message(f"Recuperación de contraseña exitosa para: {usuario}")
                self.clear_recovery_form()
            else:
                self.recovery_status_label.setText("❌ Usuario no encontrado o sin email")
                self.recovery_status_label.setStyleSheet("color: #F44336; font-weight: bold; padding: 10px;")
                self.log_message(f"Recuperación fallida para usuario: {usuario}", "WARNING")

        except Exception as e:
            self.log_message(f"Error en recuperación: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error durante la recuperación:\n{str(e)}")

    # -------------------- LIMPIEZA FORMULARIOS --------------------
    def clear_register_form(self):
        self.register_usuario_input.clear()
        self.register_email_input.clear()
        self.register_password_input.clear()
        self.register_confirm_password_input.clear()
        self.validation_label.clear()
        self.register_btn.setEnabled(False)

    def clear_recovery_form(self):
        self.recovery_usuario_input.clear()
        self.recovery_status_label.clear()


# ===== Demo =====
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = UsuarioTab()
    w.resize(1400, 900)
    w.show()
    sys.exit(app.exec())
