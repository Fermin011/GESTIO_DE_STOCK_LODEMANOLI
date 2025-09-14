# aplicacion/frontend/perfil.py
from __future__ import annotations
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
    QProgressBar, QTabWidget, QTextEdit, QSplitter, QScrollArea, QLineEdit,
    QFormLayout, QGroupBox, QGridLayout, QCheckBox, QSpacerItem, QSizePolicy
)
from datetime import datetime
import re

# Importar el controller del backend
from aplicacion.backend.usuarios.perfiles import controller

# ====== Paleta y estilos ======
BG_DARK = "#2B2D31"
FRAME_BG = "#36393F"
CARD_BG = "#FFFFFF"
CARD_SUCCESS = "#E8F5E8"
CARD_WARNING = "#FFF3E0"
CARD_ERROR = "#FFEBEE"
CARD_INFO = "#E3F2FD"
CARD_PROFILE = "#F3E5F5"
TEXT_WHITE = "#FFFFFF"
TEXT_DARK = "#2C2C2C"
TEXT_MUTED = "#72767D"
TEXT_SUCCESS = "#4CAF50"
TEXT_WARNING = "#FF9800"
TEXT_ERROR = "#F44336"
TEXT_INFO = "#2196F3"
TEXT_PROFILE = "#9C27B0"
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

QFrame#ProfileCard {{
    background: {CARD_PROFILE};
    border: 2px solid {TEXT_PROFILE};
    border-radius: 15px;
    padding: 20px;
}}

QLabel.H1 {{
    color: {TEXT_WHITE};
    font-size: 28px;
    font-weight: 700;
    margin: 8px 0px;
}}

QLabel.H2 {{
    color: {TEXT_WHITE};
    font-size: 20px;
    font-weight: 600;
    margin: 6px 0px;
}}

QLabel.ProfileTitle {{
    color: {TEXT_PROFILE};
    font-size: 24px;
    font-weight: 700;
    margin: 5px 0px;
}}

QLabel.ProfileValue {{
    color: {TEXT_DARK};
    font-size: 18px;
    font-weight: 600;
    margin: 2px 0px;
}}

QLabel.ProfileLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1px;
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

QFrame.MetricCard.success {{
    background: {CARD_SUCCESS};
    border-color: {TEXT_SUCCESS};
}}

QFrame.MetricCard.warning {{
    background: {CARD_WARNING};
    border-color: {TEXT_WARNING};
}}

QFrame.MetricCard.error {{
    background: {CARD_ERROR};
    border-color: {TEXT_ERROR};
}}

QFrame.MetricCard.info {{
    background: {CARD_INFO};
    border-color: {TEXT_INFO};
}}

QFrame.MetricCard.profile {{
    background: {CARD_PROFILE};
    border-color: {TEXT_PROFILE};
}}

QLabel.MetricValue {{
    color: {TEXT_DARK};
    font-size: 20px;
    font-weight: 700;
}}

QLabel.MetricLabel {{
    color: {TEXT_MUTED};
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
}}

QLabel.MetricSubtitle {{
    color: {TEXT_MUTED};
    font-size: 10px;
    font-style: italic;
}}

QPushButton.ActionBtn {{
    background: {ACCENT_BLUE};
    color: {TEXT_WHITE};
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton.ActionBtn:hover {{
    background: #4752C4;
}}

QPushButton.ActionBtn:pressed {{
    background: #3C45A3;
}}

QPushButton.ActionBtn.success {{
    background: {TEXT_SUCCESS};
}}

QPushButton.ActionBtn.success:hover {{
    background: #45A049;
}}

QPushButton.ActionBtn.warning {{
    background: {TEXT_WARNING};
}}

QPushButton.ActionBtn.warning:hover {{
    background: #E68900;
}}

QPushButton.ActionBtn.error {{
    background: {TEXT_ERROR};
}}

QPushButton.ActionBtn.error:hover {{
    background: #D32F2F;
}}

QPushButton.ActionBtn.purple {{
    background: {ACCENT_PURPLE};
}}

QPushButton.ActionBtn.purple:hover {{
    background: #7B1FA2;
}}

QPushButton.ActionBtn.large {{
    padding: 12px 24px;
    font-size: 14px;
    min-height: 45px;
}}

QLineEdit {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 10px 15px;
    font-weight: 500;
    color: {TEXT_DARK};
    font-size: 14px;
}}

QLineEdit:focus {{
    border-color: {ACCENT_PURPLE};
    border-width: 2px;
}}

QLineEdit.large {{
    padding: 15px 20px;
    font-size: 16px;
    min-height: 20px;
}}

QLineEdit.error {{
    border-color: {TEXT_ERROR};
    background: {CARD_ERROR};
}}

QLineEdit.success {{
    border-color: {TEXT_SUCCESS};
    background: {CARD_SUCCESS};
}}

QCheckBox {{
    color: {TEXT_WHITE};
    font-weight: 500;
}}

QComboBox {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 8px 12px;
    font-weight: 500;
    color: {TEXT_DARK};
}}

QTabWidget::pane {{
    border: 1px solid #4F545C;
    border-radius: 6px;
    background: {FRAME_BG};
    margin-top: 5px;
}}

QTabBar::tab {{
    background: #4F545C;
    color: {TEXT_WHITE};
    padding: 12px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}}

QTabBar::tab:selected {{
    background: {ACCENT_PURPLE};
}}

QTabBar::tab:hover {{
    background: #5F5F5F;
}}

QProgressBar {{
    border: 1px solid #D0D0D0;
    border-radius: 4px;
    text-align: center;
    font-weight: 600;
}}

QProgressBar::chunk {{
    background: {ACCENT_GREEN};
    border-radius: 3px;
}}

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

QTextEdit.LogArea {{
    background: {FRAME_BG};
    border: 1px solid #4F545C;
    border-radius: 6px;
    color: {TEXT_WHITE};
    font-family: 'Consolas', monospace;
    font-size: 11px;
}}

QLabel.AccessDenied {{
    color: {TEXT_ERROR};
    font-size: 16px;
    font-weight: 600;
    text-align: center;
    padding: 20px;
    background: {CARD_ERROR};
    border: 2px solid {TEXT_ERROR};
    border-radius: 8px;
}}
"""

class ProfileDisplayCard(QFrame):
    """Card grande para mostrar perfil actual"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("ProfileCard")
        self.setProperty("class", "ProfileCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        # Header del perfil
        header_layout = QHBoxLayout()
        
        # Icono de perfil
        profile_icon = QLabel("👤")
        profile_icon.setStyleSheet("font-size: 48px; margin-right: 15px;")
        header_layout.addWidget(profile_icon)
        
        # Info principal
        info_layout = QVBoxLayout()
        
        self.nombre_label = QLabel("Sin perfil seleccionado")
        self.nombre_label.setObjectName("ProfileTitle")
        self.nombre_label.setProperty("class", "ProfileTitle")
        info_layout.addWidget(self.nombre_label)
        
        self.usuario_id_label = QLabel("ID: N/A")
        self.usuario_id_label.setObjectName("ProfileLabel")
        self.usuario_id_label.setProperty("class", "ProfileLabel")
        info_layout.addWidget(self.usuario_id_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Datos del perfil en grid
        data_layout = QGridLayout()
        data_layout.setSpacing(20)
        
        # Email
        email_layout = QVBoxLayout()
        email_layout.setSpacing(5)
        email_label = QLabel("EMAIL")
        email_label.setObjectName("ProfileLabel")
        email_label.setProperty("class", "ProfileLabel")
        email_layout.addWidget(email_label)
        
        self.email_value = QLabel("No especificado")
        self.email_value.setObjectName("ProfileValue")
        self.email_value.setProperty("class", "ProfileValue")
        email_layout.addWidget(self.email_value)
        
        data_layout.addLayout(email_layout, 0, 0)
        
        # Teléfono
        telefono_layout = QVBoxLayout()
        telefono_layout.setSpacing(5)
        telefono_label = QLabel("TELÉFONO")
        telefono_label.setObjectName("ProfileLabel")
        telefono_label.setProperty("class", "ProfileLabel")
        telefono_layout.addWidget(telefono_label)
        
        self.telefono_value = QLabel("No especificado")
        self.telefono_value.setObjectName("ProfileValue")
        self.telefono_value.setProperty("class", "ProfileValue")
        telefono_layout.addWidget(self.telefono_value)
        
        data_layout.addLayout(telefono_layout, 0, 1)
        
        layout.addLayout(data_layout)
    
    def update_profile(self, perfil_data):
        """Actualizar la información del perfil"""
        if perfil_data:
            self.nombre_label.setText(perfil_data.get('nombre', 'Sin nombre'))
            self.usuario_id_label.setText(f"ID Usuario: {perfil_data.get('usuario_id', 'N/A')}")
            self.email_value.setText(perfil_data.get('email', 'No especificado'))
            self.telefono_value.setText(perfil_data.get('telefono', 'No especificado') if perfil_data.get('telefono') else 'No especificado')
        else:
            self.nombre_label.setText("Sin perfil seleccionado")
            self.usuario_id_label.setText("ID: N/A")
            self.email_value.setText("No especificado")
            self.telefono_value.setText("No especificado")

class MetricCard(QFrame):
    """Tarjeta de métrica personalizada"""
    
    def __init__(self, title: str, value: str = "N/A", subtitle: str = "", status: str = "normal"):
        super().__init__()
        self.setObjectName("MetricCard")
        self.setProperty("class", f"MetricCard {status}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)
        
        # Título
        self.title_label = QLabel(title)
        self.title_label.setObjectName("MetricLabel")
        self.title_label.setProperty("class", "MetricLabel")
        layout.addWidget(self.title_label)
        
        # Valor principal
        self.value_label = QLabel(value)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setProperty("class", "MetricValue")
        layout.addWidget(self.value_label)
        
        # Subtítulo
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            self.subtitle_label.setObjectName("MetricSubtitle")
            self.subtitle_label.setProperty("class", "MetricSubtitle")
            layout.addWidget(self.subtitle_label)
        else:
            self.subtitle_label = None
    
    def update_value(self, value: str, subtitle: str = "", status: str = "normal"):
        """Actualiza el valor y estado de la tarjeta"""
        self.value_label.setText(value)
        if self.subtitle_label and subtitle:
            self.subtitle_label.setText(subtitle)
        
        # Actualizar estilo según estado
        self.setProperty("class", f"MetricCard {status}")
        self.style().unpolish(self)
        self.style().polish(self)

class PerfilTab(QWidget):
    """Vista principal de gestión de perfiles con layout innovador"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, user_info=None, parent=None):
        super().__init__(parent)
        self.setObjectName("Root")
        self.setStyleSheet(QSS)
        
        # Variables de estado
        self.is_loading = False
        self.last_update = None
        self.current_profile = None
        self.current_user_id = None
        self.user_info = user_info  # Información del usuario logueado
        
        # Control de acceso basado en roles
        self.is_admin = self.user_info and self.user_info.get('rol_id') == 1
        self.logged_user_id = self.user_info.get('id') if self.user_info else None
        
        # Timer para validaciones (debe crearse antes de setup_connections)
        self.validation_timer = QTimer()
        self.validation_timer.setSingleShot(True)
        self.validation_timer.timeout.connect(self.validate_all_forms)
        
        self.init_ui()
        self.setup_connections()
        self.setup_access_control()
        self.load_initial_data()
    
    def setup_access_control(self):
        """Configurar controles de acceso basado en roles"""
        if not self.is_admin:
            # Ocultar/deshabilitar controles de búsqueda para usuarios no admin
            self.quick_search_input.setVisible(False)
            self.quick_search_btn.setVisible(False)
            
            # Deshabilitar tab de búsqueda
            if hasattr(self, 'tabs_widget'):
                search_tab_index = 0  # El tab de búsqueda es el primero
                self.tabs_widget.setTabEnabled(search_tab_index, False)
                self.tabs_widget.setTabText(search_tab_index, "🔒 Búsqueda (Solo Admin)")
    
    def init_ui(self):
        """Inicializar interfaz con layout innovador"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Layout principal en grid
        content_layout = QGridLayout()
        content_layout.setSpacing(20)
        
        # Columna izquierda: Card de perfil (2/3 del ancho)
        profile_section = self.create_profile_section()
        content_layout.addWidget(profile_section, 0, 0, 1, 2)
        
        # Columna derecha: Métricas pequeñas (1/3 del ancho)
        metrics_section = self.create_metrics_section()
        content_layout.addWidget(metrics_section, 0, 2, 1, 1)
        
        # Fila inferior: Tabs de gestión (ancho completo)
        tabs_section = self.create_tabs_section()
        content_layout.addWidget(tabs_section, 1, 0, 1, 3)
        
        # Configurar proporciones
        content_layout.setRowStretch(0, 1)
        content_layout.setRowStretch(1, 2)
        content_layout.setColumnStretch(0, 2)
        content_layout.setColumnStretch(1, 2)
        content_layout.setColumnStretch(2, 1)
        
        main_layout.addLayout(content_layout)
    
    def create_header(self):
        """Crear header con título y controles"""
        header = QFrame()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título con indicador de rol
        title_text = "🔧 GESTIÓN DE PERFILES"
        if not self.is_admin:
            title_text += " (MI PERFIL)"
        
        title = QLabel(title_text)
        title.setObjectName("H1")
        title.setProperty("class", "H1")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Búsqueda rápida (solo para admins)
        if self.is_admin:
            search_layout = QHBoxLayout()
            search_layout.setSpacing(10)
            
            search_label = QLabel("Buscar perfil:")
            search_label.setStyleSheet(f"color: {TEXT_WHITE}; font-weight: 500;")
            search_layout.addWidget(search_label)
            
            self.quick_search_input = QLineEdit()
            self.quick_search_input.setPlaceholderText("ID de usuario...")
            self.quick_search_input.setMaximumWidth(150)
            search_layout.addWidget(self.quick_search_input)
            
            self.quick_search_btn = QPushButton("🔍")
            self.quick_search_btn.setObjectName("ActionBtn")
            self.quick_search_btn.setProperty("class", "ActionBtn")
            self.quick_search_btn.setMaximumWidth(40)
            search_layout.addWidget(self.quick_search_btn)
            
            layout.addLayout(search_layout)
        else:
            # Crear controles invisibles para evitar errores
            self.quick_search_input = QLineEdit()
            self.quick_search_input.setVisible(False)
            self.quick_search_btn = QPushButton()
            self.quick_search_btn.setVisible(False)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)
        
        # Botón actualizar
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setObjectName("ActionBtn")
        self.refresh_btn.setProperty("class", "ActionBtn")
        layout.addWidget(self.refresh_btn)
        
        return header
    
    def create_profile_section(self):
        """Crear sección principal del perfil"""
        section = QFrame()
        section.setObjectName("MainFrame")
        section.setProperty("class", "MainFrame")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título de sección
        section_title = "MI PERFIL" if not self.is_admin else "PERFIL ACTUAL"
        title = QLabel(section_title)
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Card de perfil
        self.profile_card = ProfileDisplayCard()
        layout.addWidget(self.profile_card)
        
        # Botones de acción rápida
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        self.reload_profile_btn = QPushButton("🔄 Recargar Perfil")
        self.reload_profile_btn.setObjectName("ActionBtn")
        self.reload_profile_btn.setProperty("class", "ActionBtn large")
        self.reload_profile_btn.setEnabled(False)
        actions_layout.addWidget(self.reload_profile_btn)
        
        self.clear_profile_btn = QPushButton("🧹 Limpiar Vista")
        self.clear_profile_btn.setObjectName("ActionBtn")
        self.clear_profile_btn.setProperty("class", "ActionBtn large")
        # Solo admins pueden limpiar la vista (usuarios normales siempre ven su perfil)
        self.clear_profile_btn.setEnabled(self.is_admin)
        actions_layout.addWidget(self.clear_profile_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        return section
    
    def create_metrics_section(self):
        """Crear sección de métricas compactas"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(15)
        
        # Título
        title = QLabel("ESTADÍSTICAS")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Métricas apiladas verticalmente
        self.estado_card = MetricCard(
            "ESTADO", 
            "Listo", 
            "Sistema activo"
        )
        layout.addWidget(self.estado_card)
        
        # Métrica de rol
        rol_text = "Administrador" if self.is_admin else "Usuario"
        self.rol_card = MetricCard(
            "ROL ACTUAL",
            rol_text,
            "Permisos activos",
            "success" if self.is_admin else "info"
        )
        layout.addWidget(self.rol_card)
        
        self.perfil_actual_card = MetricCard(
            "PERFIL ACTIVO", 
            "Ninguno", 
            "Sin seleccionar"
        )
        layout.addWidget(self.perfil_actual_card)
        
        self.ultima_busqueda_card = MetricCard(
            "ÚLTIMA BÚSQUEDA", 
            "Nunca", 
            "Sin búsquedas"
        )
        layout.addWidget(self.ultima_busqueda_card)
        
        layout.addStretch()
        
        return section
    
    def create_tabs_section(self):
        """Crear sección de tabs para gestión"""
        self.tabs_widget = QTabWidget()
        
        # Tab 1: Búsqueda avanzada (solo para admins)
        search_tab = self.create_search_tab()
        self.tabs_widget.addTab(search_tab, "🔍 Búsqueda")
        
        # Tab 2: Edición de perfil
        edit_tab = self.create_edit_tab()
        self.tabs_widget.addTab(edit_tab, "✏️ Editar")
        
        # Tab 3: Log de actividades
        log_tab = self.create_log_tab()
        self.tabs_widget.addTab(log_tab, "📋 Actividad")
        
        return self.tabs_widget
    
    def create_search_tab(self):
        """Crear tab de búsqueda avanzada"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)
        
        if not self.is_admin:
            # Mostrar mensaje de acceso denegado para usuarios no admin
            access_denied = QLabel("🔒 ACCESO RESTRINGIDO\n\nSolo los administradores pueden buscar perfiles de otros usuarios.\nUsted puede ver y editar únicamente su propio perfil.")
            access_denied.setObjectName("AccessDenied")
            access_denied.setProperty("class", "AccessDenied")
            access_denied.setAlignment(Qt.AlignmentFlag.AlignCenter)
            access_denied.setWordWrap(True)
            layout.addWidget(access_denied)
            return tab
        
        # Layout para admins
        main_layout = QHBoxLayout()
        main_layout.setSpacing(30)
        
        # Columna izquierda: Formulario de búsqueda
        search_group = QGroupBox("Buscar Perfil")
        search_layout = QFormLayout(search_group)
        search_layout.setSpacing(15)
        
        # ID de usuario
        self.search_user_id_input = QLineEdit()
        self.search_user_id_input.setPlaceholderText("Ej: 1, 2, 3...")
        self.search_user_id_input.setProperty("class", "large")
        search_layout.addRow("ID Usuario:", self.search_user_id_input)
        
        # Botones de búsqueda
        search_buttons = QHBoxLayout()
        
        self.search_profile_btn = QPushButton("🔍 Buscar Perfil")
        self.search_profile_btn.setObjectName("ActionBtn")
        self.search_profile_btn.setProperty("class", "ActionBtn purple large")
        search_buttons.addWidget(self.search_profile_btn)
        
        self.clear_search_btn = QPushButton("🧹 Limpiar")
        self.clear_search_btn.setObjectName("ActionBtn")
        self.clear_search_btn.setProperty("class", "ActionBtn large")
        search_buttons.addWidget(self.clear_search_btn)
        
        search_layout.addRow(search_buttons)
        
        # Estado de búsqueda
        self.search_status_label = QLabel("")
        self.search_status_label.setStyleSheet("font-weight: bold; padding: 10px;")
        search_layout.addRow("", self.search_status_label)
        
        main_layout.addWidget(search_group)
        
        # Columna derecha: Información adicional
        info_group = QGroupBox("Información de Búsqueda")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(15)
        
        info_text = QLabel("""
💡 Consejos para la búsqueda:

• Ingresa el ID numérico del usuario
• Cada usuario puede tener un perfil asociado
• Si no existe perfil, se mostrará un mensaje
• Usa el botón 'Limpiar' para resetear la vista
• Solo administradores pueden buscar otros perfiles
        """)
        info_text.setWordWrap(True)
        info_text.setStyleSheet(f"color: {TEXT_WHITE}; line-height: 1.4; padding: 15px;")
        info_layout.addWidget(info_text)
        
        info_layout.addStretch()
        main_layout.addWidget(info_group)
        
        layout.addLayout(main_layout)
        return tab
    
    def create_edit_tab(self):
        """Crear tab de edición de perfil"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Información del perfil actual
        current_group = QGroupBox("Perfil Seleccionado")
        current_layout = QHBoxLayout(current_group)
        current_layout.setSpacing(20)
        
        self.edit_current_user_label = QLabel("Ningún perfil seleccionado")
        self.edit_current_user_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #9C27B0;")
        current_layout.addWidget(self.edit_current_user_label)
        
        current_layout.addStretch()
        layout.addWidget(current_group)
        
        # Formularios de edición en grid
        forms_layout = QGridLayout()
        forms_layout.setSpacing(25)
        
        # Formulario nombre
        nombre_group = QGroupBox("Actualizar Nombre")
        nombre_layout = QFormLayout(nombre_group)
        nombre_layout.setSpacing(10)
        
        self.edit_nombre_input = QLineEdit()
        self.edit_nombre_input.setPlaceholderText("Nuevo nombre completo...")
        self.edit_nombre_input.setProperty("class", "large")
        self.edit_nombre_input.setEnabled(False)
        nombre_layout.addRow("Nombre:", self.edit_nombre_input)
        
        self.save_nombre_btn = QPushButton("💾 Guardar Nombre")
        self.save_nombre_btn.setObjectName("ActionBtn")
        self.save_nombre_btn.setProperty("class", "ActionBtn success large")
        self.save_nombre_btn.setEnabled(False)
        nombre_layout.addRow("", self.save_nombre_btn)
        
        forms_layout.addWidget(nombre_group, 0, 0)
        
        # Formulario email
        email_group = QGroupBox("Actualizar Email")
        email_layout = QFormLayout(email_group)
        email_layout.setSpacing(10)
        
        self.edit_email_input = QLineEdit()
        self.edit_email_input.setPlaceholderText("nuevo@email.com")
        self.edit_email_input.setProperty("class", "large")
        self.edit_email_input.setEnabled(False)
        email_layout.addRow("Email:", self.edit_email_input)
        
        self.save_email_btn = QPushButton("💾 Guardar Email")
        self.save_email_btn.setObjectName("ActionBtn")
        self.save_email_btn.setProperty("class", "ActionBtn warning large")
        self.save_email_btn.setEnabled(False)
        email_layout.addRow("", self.save_email_btn)
        
        forms_layout.addWidget(email_group, 0, 1)
        
        # Formulario teléfono
        telefono_group = QGroupBox("Actualizar Teléfono")
        telefono_layout = QFormLayout(telefono_group)
        telefono_layout.setSpacing(10)
        
        self.edit_telefono_input = QLineEdit()
        self.edit_telefono_input.setPlaceholderText("+54 9 11 1234-5678")
        self.edit_telefono_input.setProperty("class", "large")
        self.edit_telefono_input.setEnabled(False)
        telefono_layout.addRow("Teléfono:", self.edit_telefono_input)
        
        self.save_telefono_btn = QPushButton("💾 Guardar Teléfono")
        self.save_telefono_btn.setObjectName("ActionBtn")
        self.save_telefono_btn.setProperty("class", "ActionBtn purple large")
        self.save_telefono_btn.setEnabled(False)
        telefono_layout.addRow("", self.save_telefono_btn)
        
        forms_layout.addWidget(telefono_group, 1, 0)
        
        # Controles generales
        controls_group = QGroupBox("Controles")
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(15)
        
        self.cancel_edit_btn = QPushButton("⌫ Cancelar Edición")
        self.cancel_edit_btn.setObjectName("ActionBtn")
        self.cancel_edit_btn.setProperty("class", "ActionBtn error large")
        self.cancel_edit_btn.setEnabled(False)
        controls_layout.addWidget(self.cancel_edit_btn)
        
        controls_layout.addStretch()
        forms_layout.addWidget(controls_group, 1, 1)
        
        layout.addLayout(forms_layout)
        
        return tab
    
    def create_log_tab(self):
        """Crear tab de log"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        self.log_area = QTextEdit()
        self.log_area.setObjectName("LogArea")
        self.log_area.setProperty("class", "LogArea")
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)
        
        return tab
    
    def setup_connections(self):
        """Configurar conexiones de eventos"""
        # Header
        self.refresh_btn.clicked.connect(self.refresh_all_data)
        if self.is_admin:
            self.quick_search_btn.clicked.connect(self.quick_search_profile)
            self.quick_search_input.returnPressed.connect(self.quick_search_profile)
        
        # Profile section
        self.reload_profile_btn.clicked.connect(self.reload_current_profile)
        if self.is_admin:
            self.clear_profile_btn.clicked.connect(self.clear_profile_view)
        
        # Search tab (solo para admins)
        if self.is_admin and hasattr(self, 'search_profile_btn'):
            self.search_profile_btn.clicked.connect(self.search_profile)
            self.clear_search_btn.clicked.connect(self.clear_search_form)
            self.search_user_id_input.returnPressed.connect(self.search_profile)
        
        # Edit tab
        self.save_nombre_btn.clicked.connect(self.save_nombre)
        self.save_email_btn.clicked.connect(self.save_email)
        self.save_telefono_btn.clicked.connect(self.save_telefono)
        self.cancel_edit_btn.clicked.connect(self.cancel_edit)
        
        # Validaciones en tiempo real
        self.edit_nombre_input.textChanged.connect(self.start_validation_timer)
        self.edit_email_input.textChanged.connect(self.start_validation_timer)
        self.edit_telefono_input.textChanged.connect(self.start_validation_timer)
    
    def log_message(self, message: str, level: str = "INFO"):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}"
        self.log_area.append(formatted_msg)
        
        # Auto-scroll al final
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
    
    def set_loading(self, loading: bool):
        """Activar/desactivar estado de carga"""
        self.is_loading = loading
        self.progress_bar.setVisible(loading)
        self.refresh_btn.setEnabled(not loading)
        
        if loading:
            self.progress_bar.setRange(0, 0)  # Indeterminado
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)
    
    def load_initial_data(self):
        """Cargar datos iniciales"""
        self.log_message("Iniciando sistema de gestión de perfiles...")
        
        # Para usuarios no admin, cargar automáticamente su propio perfil
        if not self.is_admin and self.logged_user_id:
            self.log_message(f"Cargando perfil del usuario logueado (ID: {self.logged_user_id})")
            self.load_logged_user_profile()
        
        self.refresh_all_data()
    
    def load_logged_user_profile(self):
        """Cargar automáticamente el perfil del usuario logueado"""
        try:
            if not self.logged_user_id:
                self.log_message("No hay ID de usuario logueado disponible", "WARNING")
                return
            
            # Buscar el perfil del usuario logueado
            perfil = controller.obtener_perfil_controller(self.logged_user_id)
            
            if perfil:
                # Perfil encontrado
                self.current_profile = {
                    'usuario_id': perfil.usuario_id,
                    'nombre': perfil.nombre,
                    'email': perfil.email,
                    'telefono': perfil.telefono
                }
                self.current_user_id = self.logged_user_id
                
                # Actualizar vista
                self.profile_card.update_profile(self.current_profile)
                self.enable_edit_forms()
                
                self.log_message(f"Perfil cargado automáticamente: {perfil.nombre}")
                
            else:
                # No tiene perfil creado
                self.log_message(f"El usuario logueado (ID: {self.logged_user_id}) no tiene perfil creado", "WARNING")
                
                # Crear un perfil vacío para mostrar información básica
                self.current_profile = {
                    'usuario_id': self.logged_user_id,
                    'nombre': 'Sin nombre configurado',
                    'email': 'No especificado',
                    'telefono': 'No especificado'
                }
                self.current_user_id = self.logged_user_id
                self.profile_card.update_profile(self.current_profile)
                
                # Habilitar formularios para que pueda crear su perfil
                self.enable_edit_forms()
                
        except Exception as e:
            self.log_message(f"Error cargando perfil del usuario logueado: {str(e)}", "ERROR")
    
    def refresh_all_data(self):
        """Actualizar todos los datos"""
        if self.is_loading:
            return
        
        self.set_loading(True)
        self.log_message("Actualizando datos del sistema...")
        
        try:
            self.refresh_metrics()
            
            self.last_update = datetime.now()
            self.log_message("Datos actualizados exitosamente")
            self.data_updated.emit()
            
        except Exception as e:
            self.log_message(f"Error actualizando datos: {str(e)}", "ERROR")
            QMessageBox.warning(self, "Error", f"Error al actualizar datos:\n{str(e)}")
        
        finally:
            self.set_loading(False)
    
    def refresh_metrics(self):
        """Actualizar métricas"""
        try:
            # Estado del sistema
            self.estado_card.update_value("Operativo", "Sistema activo", "success")
            
            # Perfil actual
            if self.current_profile:
                self.perfil_actual_card.update_value(
                    f"ID {self.current_user_id}",
                    self.current_profile.get('nombre', 'Sin nombre')[:15] + "...",
                    "profile"
                )
            else:
                self.perfil_actual_card.update_value("Ninguno", "Sin seleccionar", "normal")
            
            # Última búsqueda
            if self.last_update:
                self.ultima_busqueda_card.update_value(
                    self.last_update.strftime("%H:%M:%S"),
                    "Actualizado",
                    "info"
                )
            else:
                self.ultima_busqueda_card.update_value("Nunca", "Sin búsquedas", "normal")
                
        except Exception as e:
            self.log_message(f"Error actualizando métricas: {str(e)}", "ERROR")
    
    def validate_email(self, email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def start_validation_timer(self):
        """Iniciar timer de validación"""
        self.validation_timer.start(500)  # 500ms delay
    
    def validate_all_forms(self):
        """Validar todos los formularios de edición"""
        if not self.current_profile:
            return
        
        # Validar nombre
        nombre = self.edit_nombre_input.text().strip()
        if nombre and len(nombre) >= 2:
            self.edit_nombre_input.setProperty("class", "large success")
        elif nombre:
            self.edit_nombre_input.setProperty("class", "large error")
        else:
            self.edit_nombre_input.setProperty("class", "large")
        
        # Validar email
        email = self.edit_email_input.text().strip()
        if email and self.validate_email(email):
            self.edit_email_input.setProperty("class", "large success")
        elif email:
            self.edit_email_input.setProperty("class", "large error")
        else:
            self.edit_email_input.setProperty("class", "large")
        
        # Validar teléfono (cualquier texto es válido)
        telefono = self.edit_telefono_input.text().strip()
        if telefono:
            self.edit_telefono_input.setProperty("class", "large success")
        else:
            self.edit_telefono_input.setProperty("class", "large")
        
        # Refrescar estilos
        self.edit_nombre_input.style().unpolish(self.edit_nombre_input)
        self.edit_nombre_input.style().polish(self.edit_nombre_input)
        self.edit_email_input.style().unpolish(self.edit_email_input)
        self.edit_email_input.style().polish(self.edit_email_input)
        self.edit_telefono_input.style().unpolish(self.edit_telefono_input)
        self.edit_telefono_input.style().polish(self.edit_telefono_input)
    
    def quick_search_profile(self):
        """Búsqueda rápida desde el header (solo admins)"""
        if not self.is_admin:
            return
        
        user_id_text = self.quick_search_input.text().strip()
        if not user_id_text:
            return
        
        try:
            user_id = int(user_id_text)
            if hasattr(self, 'search_user_id_input'):
                self.search_user_id_input.setText(str(user_id))
                self.search_profile()
        except ValueError:
            QMessageBox.warning(self, "Error", "El ID debe ser un número")
    
    def search_profile(self):
        """Buscar perfil por ID de usuario (solo admins)"""
        if not self.is_admin:
            QMessageBox.warning(self, "Acceso Denegado", "Solo los administradores pueden buscar otros perfiles.")
            return
        
        try:
            user_id_text = self.search_user_id_input.text().strip()
            
            if not user_id_text:
                self.search_status_label.setText("⚠ Ingrese un ID de usuario")
                self.search_status_label.setStyleSheet("color: #F44336; font-weight: bold; padding: 10px;")
                return
            
            try:
                user_id = int(user_id_text)
            except ValueError:
                self.search_status_label.setText("⚠ El ID debe ser un número")
                self.search_status_label.setStyleSheet("color: #F44336; font-weight: bold; padding: 10px;")
                return
            
            # Buscar perfil
            perfil = controller.obtener_perfil_controller(user_id)
            
            if perfil:
                # Perfil encontrado
                self.current_profile = {
                    'usuario_id': perfil.usuario_id,
                    'nombre': perfil.nombre,
                    'email': perfil.email,
                    'telefono': perfil.telefono
                }
                self.current_user_id = user_id
                
                # Actualizar vista
                self.profile_card.update_profile(self.current_profile)
                self.enable_edit_forms()
                
                self.search_status_label.setText(f"✅ Perfil encontrado: {perfil.nombre}")
                self.search_status_label.setStyleSheet("color: #4CAF50; font-weight: bold; padding: 10px;")
                
                self.log_message(f"Perfil cargado: {perfil.nombre} (Usuario ID: {user_id})")
                
                # Actualizar métricas
                self.refresh_metrics()
                
            else:
                # Perfil no encontrado
                self.search_status_label.setText("⚠ No se encontró perfil para este usuario")
                self.search_status_label.setStyleSheet("color: #F44336; font-weight: bold; padding: 10px;")
                self.log_message(f"Perfil no encontrado para usuario ID: {user_id}", "WARNING")
                
        except Exception as e:
            self.log_message(f"Error en búsqueda: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error durante la búsqueda:\n{str(e)}")
    
    def enable_edit_forms(self):
        """Habilitar formularios de edición"""
        self.edit_current_user_label.setText(f"Usuario ID {self.current_user_id}: {self.current_profile['nombre']}")
        
        # Habilitar campos
        self.edit_nombre_input.setEnabled(True)
        self.edit_email_input.setEnabled(True)
        self.edit_telefono_input.setEnabled(True)
        
        # Habilitar botones
        self.save_nombre_btn.setEnabled(True)
        self.save_email_btn.setEnabled(True)
        self.save_telefono_btn.setEnabled(True)
        self.cancel_edit_btn.setEnabled(True)
        self.reload_profile_btn.setEnabled(True)
        
        # Precargar valores actuales
        self.edit_nombre_input.setText(self.current_profile['nombre'] or "")
        self.edit_email_input.setText(self.current_profile['email'] or "")
        self.edit_telefono_input.setText(self.current_profile['telefono'] or "")
    
    def disable_edit_forms(self):
        """Deshabilitar formularios de edición"""
        self.edit_current_user_label.setText("Ningún perfil seleccionado")
        
        # Deshabilitar campos
        self.edit_nombre_input.setEnabled(False)
        self.edit_email_input.setEnabled(False)
        self.edit_telefono_input.setEnabled(False)
        
        # Deshabilitar botones
        self.save_nombre_btn.setEnabled(False)
        self.save_email_btn.setEnabled(False)
        self.save_telefono_btn.setEnabled(False)
        self.cancel_edit_btn.setEnabled(False)
        self.reload_profile_btn.setEnabled(False)
        
        # Limpiar campos
        self.edit_nombre_input.clear()
        self.edit_email_input.clear()
        self.edit_telefono_input.clear()
    
    def save_nombre(self):
        """Guardar cambios de nombre"""
        try:
            if not self.current_user_id:
                QMessageBox.warning(self, "Error", "No hay perfil seleccionado")
                return
            
            # Verificar permisos: solo puede editar su propio perfil o ser admin
            if not self.is_admin and self.current_user_id != self.logged_user_id:
                QMessageBox.warning(self, "Acceso Denegado", "Solo puede editar su propio perfil.")
                return
            
            nuevo_nombre = self.edit_nombre_input.text().strip()
            
            if not nuevo_nombre:
                QMessageBox.warning(self, "Error", "El nombre no puede estar vacío")
                return
            
            if len(nuevo_nombre) < 2:
                QMessageBox.warning(self, "Error", "El nombre debe tener al menos 2 caracteres")
                return
            
            # Actualizar nombre
            success = controller.actualizar_nombre_perfil_controller(self.current_user_id, nuevo_nombre)
            
            if success:
                self.current_profile['nombre'] = nuevo_nombre
                self.profile_card.update_profile(self.current_profile)
                self.enable_edit_forms()  # Refrescar vista
                
                self.log_message(f"Nombre actualizado: {nuevo_nombre}")
                QMessageBox.information(self, "Éxito", f"Nombre actualizado a: {nuevo_nombre}")
                self.refresh_metrics()
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el nombre")
                
        except Exception as e:
            self.log_message(f"Error actualizando nombre: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error actualizando nombre:\n{str(e)}")
    
    def save_email(self):
        """Guardar cambios de email"""
        try:
            if not self.current_user_id:
                QMessageBox.warning(self, "Error", "No hay perfil seleccionado")
                return
            
            # Verificar permisos: solo puede editar su propio perfil o ser admin
            if not self.is_admin and self.current_user_id != self.logged_user_id:
                QMessageBox.warning(self, "Acceso Denegado", "Solo puede editar su propio perfil.")
                return
            
            nuevo_email = self.edit_email_input.text().strip()
            
            if not nuevo_email:
                QMessageBox.warning(self, "Error", "El email no puede estar vacío")
                return
            
            if not self.validate_email(nuevo_email):
                QMessageBox.warning(self, "Error", "Email inválido")
                return
            
            # Actualizar email
            success = controller.actualizar_email_perfil_controller(self.current_user_id, nuevo_email)
            
            if success:
                self.current_profile['email'] = nuevo_email
                self.profile_card.update_profile(self.current_profile)
                self.enable_edit_forms()  # Refrescar vista
                
                self.log_message(f"Email actualizado: {nuevo_email}")
                QMessageBox.information(self, "Éxito", f"Email actualizado a: {nuevo_email}")
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el email")
                
        except Exception as e:
            self.log_message(f"Error actualizando email: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error actualizando email:\n{str(e)}")
    
    def save_telefono(self):
        """Guardar cambios de teléfono"""
        try:
            if not self.current_user_id:
                QMessageBox.warning(self, "Error", "No hay perfil seleccionado")
                return
            
            # Verificar permisos: solo puede editar su propio perfil o ser admin
            if not self.is_admin and self.current_user_id != self.logged_user_id:
                QMessageBox.warning(self, "Acceso Denegado", "Solo puede editar su propio perfil.")
                return
            
            nuevo_telefono = self.edit_telefono_input.text().strip()
            
            if not nuevo_telefono:
                QMessageBox.warning(self, "Error", "El teléfono no puede estar vacío")
                return
            
            # Actualizar teléfono
            success = controller.actualizar_telefono_perfil_controller(self.current_user_id, nuevo_telefono)
            
            if success:
                self.current_profile['telefono'] = nuevo_telefono
                self.profile_card.update_profile(self.current_profile)
                self.enable_edit_forms()  # Refrescar vista
                
                self.log_message(f"Teléfono actualizado: {nuevo_telefono}")
                QMessageBox.information(self, "Éxito", f"Teléfono actualizado a: {nuevo_telefono}")
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el teléfono")
                
        except Exception as e:
            self.log_message(f"Error actualizando teléfono: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error actualizando teléfono:\n{str(e)}")
    
    def reload_current_profile(self):
        """Recargar perfil actual"""
        if self.current_user_id:
            if self.is_admin and hasattr(self, 'search_user_id_input'):
                self.search_user_id_input.setText(str(self.current_user_id))
                self.search_profile()
            else:
                # Para usuarios no admin, recargar su propio perfil
                self.load_logged_user_profile()
    
    def clear_profile_view(self):
        """Limpiar vista de perfil (solo admins)"""
        if not self.is_admin:
            return
        
        self.current_profile = None
        self.current_user_id = None
        self.profile_card.update_profile(None)
        self.disable_edit_forms()
        if hasattr(self, 'search_status_label'):
            self.search_status_label.clear()
        self.log_message("Vista de perfil limpiada")
        self.refresh_metrics()
    
    def clear_search_form(self):
        """Limpiar formulario de búsqueda (solo admins)"""
        if not self.is_admin:
            return
        
        if hasattr(self, 'search_user_id_input'):
            self.search_user_id_input.clear()
        self.quick_search_input.clear()
        if hasattr(self, 'search_status_label'):
            self.search_status_label.clear()
    
    def cancel_edit(self):
        """Cancelar edición"""
        if self.current_profile:
            # Restaurar valores originales
            self.edit_nombre_input.setText(self.current_profile['nombre'] or "")
            self.edit_email_input.setText(self.current_profile['email'] or "")
            self.edit_telefono_input.setText(self.current_profile['telefono'] or "")
            self.log_message("Edición cancelada, valores restaurados")
        else:
            if self.is_admin:
                self.clear_profile_view()
            else:
                # Para usuarios no admin, recargar su perfil
                self.load_logged_user_profile()

# ===== Demo =====
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Simular user_info para testing
    user_info_admin = {"id": 1, "nombre_usuario": "admin", "rol_id": 1}
    user_info_user = {"id": 2, "nombre_usuario": "usuario", "rol_id": 2}
    
    w = PerfilTab(user_info=user_info_user)  # Cambiar a user_info_admin para probar como admin
    w.resize(1400, 900)
    w.show()
    sys.exit(app.exec())