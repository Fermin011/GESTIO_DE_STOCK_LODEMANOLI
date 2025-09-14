# aplicacion/frontend/caja.py
from __future__ import annotations
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
    QProgressBar, QTabWidget, QTextEdit, QSplitter, QScrollArea, QLineEdit,
    QDateEdit, QSpinBox, QDoubleSpinBox, QFormLayout, QGroupBox, QGridLayout
)
from datetime import date, datetime, timedelta
import calendar

# Importar el controller del backend
from aplicacion.backend.caja import controller

# Importar el sistema de permisos
from aplicacion.backend.usuarios.roles.permisos_manager import PermisosManager

# ====== Paleta y estilos ======
BG_DARK = "#2B2D31"
FRAME_BG = "#36393F"
CARD_BG = "#FFFFFF"
CARD_SUCCESS = "#E8F5E8"
CARD_WARNING = "#FFF3E0"
CARD_ERROR = "#FFEBEE"
TEXT_WHITE = "#FFFFFF"
TEXT_DARK = "#2C2C2C"
TEXT_MUTED = "#72767D"
TEXT_SUCCESS = "#4CAF50"
TEXT_WARNING = "#FF9800"
TEXT_ERROR = "#F44336"
ACCENT_BLUE = "#5865F2"
ACCENT_GREEN = "#57F287"

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

QLabel.H2 {{
    color: {TEXT_WHITE};
    font-size: 20px;
    font-weight: 600;
    margin: 6px 0px;
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

QLabel.MetricValue {{
    color: {TEXT_DARK};
    font-size: 24px;
    font-weight: 700;
}}

QLabel.MetricLabel {{
    color: {TEXT_MUTED};
    font-size: 12px;
    font-weight: 500;
    text-transform: uppercase;
}}

QLabel.MetricSubtitle {{
    color: {TEXT_MUTED};
    font-size: 11px;
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

QPushButton.ActionBtn:disabled {{
    background: #666666;
    color: #999999;
}}

QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
    color: {TEXT_DARK};
}}

QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QDateEdit:focus {{
    border-color: {ACCENT_BLUE};
}}

QLineEdit:disabled, QDoubleSpinBox:disabled, QSpinBox:disabled, QDateEdit:disabled {{
    background: #f0f0f0;
    color: #888888;
}}

QComboBox.Selector {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
    color: {TEXT_DARK};
    min-width: 120px;
}}

QTableWidget#CajaTable {{
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

QTableWidget::item {{
    padding: 6px;
    color: {TEXT_DARK};
}}

QTableWidget::item:selected {{
    background: #E3F2FD;
}}

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

QTabBar::tab:selected {{
    background: {ACCENT_BLUE};
}}

QTabBar::tab:disabled {{
    background: #666666;
    color: #999999;
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

QLabel.AccessDenied {{
    color: {TEXT_ERROR};
    font-size: 18px;
    font-weight: 600;
    text-align: center;
    padding: 40px;
    background: {CARD_ERROR};
    border: 2px solid {TEXT_ERROR};
    border-radius: 12px;
    margin: 20px;
}}
"""

class MetricCard(QFrame):
    """Tarjeta de métrica personalizada para caja"""
    
    def __init__(self, title: str, value: str = "N/A", subtitle: str = "", status: str = "normal"):
        super().__init__()
        self.setObjectName("MetricCard")
        self.setProperty("class", f"MetricCard {status}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)
        
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

class CajaTab(QWidget):
    """Vista principal de gestión de caja con sistema de permisos"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Root")
        self.setStyleSheet(QSS)
        
        # Variables de estado
        self.is_loading = False
        self.last_update = None
        self.current_user_id = 1  # Debería venir del sistema de login
        
        # Sistema de permisos
        self.permisos_manager: PermisosManager = None
        
        self.init_ui()
        self.setup_connections()
        
        # Timer para actualizaciones automáticas
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.refresh_today_metrics)
        self.auto_timer.start(300000)  # Cada 5 minutos
    
    def set_permisos_manager(self, permisos_manager: PermisosManager):
        """Configurar el manager de permisos y aplicar restricciones"""
        self.permisos_manager = permisos_manager
        self.current_user_id = permisos_manager.usuario_id
        
        # Aplicar control de acceso después de configurar permisos
        if hasattr(self, 'tabs_widget'):
            self._setup_access_control()
        
        # Cargar datos iniciales solo después de configurar permisos
        self.load_initial_data()
    
    def _setup_access_control(self):
        """Configurar control de acceso basado en permisos"""
        if not self.permisos_manager:
            return
        
        # Control de botones del header
        can_update = self.permisos_manager.puede_ver_movimientos_caja()
        can_register = self.permisos_manager.puede_abrir_caja()
        
        self.refresh_btn.setEnabled(can_update)
        self.register_today_btn.setEnabled(can_register)
        
        if not can_update:
            self.refresh_btn.setToolTip("Sin permisos para actualizar datos")
        if not can_register:
            self.register_today_btn.setToolTip("Sin permisos para registrar caja")
        
        # Control de tabs
        can_view_consultations = self.permisos_manager.puede_cerrar_caja()  # Consultas requiere cerrar
        can_admin = self.permisos_manager.puede_editar_montos_caja()  # Administración requiere editar montos
        can_view_log = self.permisos_manager.is_admin  # Log solo para admins
        
        # Deshabilitar tabs según permisos
        # Tab 0: Registro Diario - todos los que pueden abrir caja
        # Tab 1: Consultas - solo si pueden cerrar caja
        # Tab 2: Administración - solo si pueden editar montos
        # Tab 3: Log - solo admins
        
        if not can_view_consultations:
            self.tabs_widget.setTabEnabled(1, False)
            self.tabs_widget.setTabText(1, "🔒 Consultas (Sin permisos)")
        
        if not can_admin:
            self.tabs_widget.setTabEnabled(2, False)
            self.tabs_widget.setTabText(2, "🔒 Administración (Sin permisos)")
        
        if not can_view_log:
            self.tabs_widget.setTabEnabled(3, False)
            self.tabs_widget.setTabText(3, "🔒 Log (Solo Admin)")
        
        # Reemplazar contenido de tabs restringidos con mensaje
        if not can_view_consultations:
            self._replace_tab_with_message(1, "CONSULTAS", "Se requiere permiso 'cerrar caja'")
        
        if not can_admin:
            self._replace_tab_with_message(2, "ADMINISTRACIÓN", "Se requiere permiso 'editar montos'")
        
        if not can_view_log:
            self._replace_tab_with_message(3, "LOG", "Solo disponible para administradores")
        
        # Asegurar que esté en un tab permitido
        if self.tabs_widget.currentIndex() > 0:
            if not self.tabs_widget.isTabEnabled(self.tabs_widget.currentIndex()):
                self.tabs_widget.setCurrentIndex(0)  # Volver a Registro Diario
    
    def _replace_tab_with_message(self, tab_index: int, section_name: str, reason: str):
        """Reemplazar contenido de tab con mensaje de acceso denegado"""
        message_widget = QWidget()
        layout = QVBoxLayout(message_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Mensaje principal
        access_denied = QLabel(f"🔒 ACCESO DENEGADO\n\nSección: {section_name}")
        access_denied.setObjectName("AccessDenied")
        access_denied.setProperty("class", "AccessDenied")
        access_denied.setAlignment(Qt.AlignmentFlag.AlignCenter)
        access_denied.setWordWrap(True)
        layout.addWidget(access_denied)
        
        # Razón
        reason_label = QLabel(reason)
        reason_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reason_label.setStyleSheet("color: #888888; font-size: 14px; margin-top: 10px;")
        reason_label.setWordWrap(True)
        layout.addWidget(reason_label)
        
        # Información del usuario
        if self.permisos_manager:
            user_info = QLabel(f"Usuario: {self.permisos_manager.user_info.get('nombre_usuario')}\nRol: {'Administrador' if self.permisos_manager.is_admin else 'Empleado'}")
            user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            user_info.setStyleSheet("color: #666666; font-size: 12px; margin-top: 20px;")
            layout.addWidget(user_info)
        
        layout.addStretch()
        
        # Reemplazar el contenido del tab
        self.tabs_widget.removeTab(tab_index)
        self.tabs_widget.insertTab(tab_index, message_widget, f"🔒 {section_name}")
        self.tabs_widget.setTabEnabled(tab_index, False)
    
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Header con título y controles
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Contenido principal con splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Panel superior: métricas principales
        metrics_panel = self.create_metrics_panel()
        splitter.addWidget(metrics_panel)
        
        # Panel inferior: tabs con funcionalidades
        tabs_panel = self.create_tabs_panel()
        splitter.addWidget(tabs_panel)
        
        splitter.setSizes([350, 450])
        main_layout.addWidget(splitter)
    
    def create_header(self):
        """Crear header con título y controles"""
        header = QFrame()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("💰 GESTIÓN DE CAJA")
        title.setObjectName("H1")
        title.setProperty("class", "H1")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Barra de progreso para loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        layout.addWidget(self.progress_bar)
        
        # Botón actualizar
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setObjectName("ActionBtn")
        self.refresh_btn.setProperty("class", "ActionBtn")
        layout.addWidget(self.refresh_btn)
        
        # Botón registrar hoy
        self.register_today_btn = QPushButton("💾 Registrar Hoy")
        self.register_today_btn.setObjectName("ActionBtn")
        self.register_today_btn.setProperty("class", "ActionBtn success")
        layout.addWidget(self.register_today_btn)
        
        return header
    
    def create_metrics_panel(self):
        """Crear panel principal de métricas"""
        panel = QFrame()
        panel.setObjectName("MainFrame")
        panel.setProperty("class", "MainFrame")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)
        
        # Métricas de HOY
        today_section = self.create_today_section()
        layout.addWidget(today_section)
        
        # Métricas de PERÍODO
        period_section = self.create_period_section()
        layout.addWidget(period_section)
        
        return panel
    
    def create_today_section(self):
        """Crear sección de métricas de hoy"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("CIERRE DE HOY")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Grid de tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # Estado del día
        self.today_status_card = MetricCard(
            "ESTADO", 
            "Sin registrar", 
            "Estado del cierre"
        )
        cards_layout.addWidget(self.today_status_card)
        
        # Efectivo
        self.today_efectivo_card = MetricCard(
            "EFECTIVO", 
            "$0", 
            "Dinero en caja"
        )
        cards_layout.addWidget(self.today_efectivo_card)
        
        # Transferencias
        self.today_transfer_card = MetricCard(
            "TRANSFERENCIAS", 
            "$0", 
            "Cobros digitales"
        )
        cards_layout.addWidget(self.today_transfer_card)
        
        # Total
        self.today_total_card = MetricCard(
            "TOTAL HOY", 
            "$0", 
            "Efectivo + Transferencias"
        )
        cards_layout.addWidget(self.today_total_card)
        
        layout.addLayout(cards_layout)
        
        return section
    
    def create_period_section(self):
        """Crear sección de métricas por período"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("RESÚMENES")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Grid de períodos
        periods_layout = QHBoxLayout()
        periods_layout.setSpacing(16)
        
        # Semana
        self.week_card = MetricCard(
            "ESTA SEMANA", 
            "$0", 
            "Últimos 7 días"
        )
        periods_layout.addWidget(self.week_card)
        
        # Mes actual
        self.month_card = MetricCard(
            "ESTE MES", 
            "$0", 
            date.today().strftime("%B %Y")
        )
        periods_layout.addWidget(self.month_card)
        
        # Promedio diario
        self.average_card = MetricCard(
            "PROMEDIO DIARIO", 
            "$0", 
            "Del mes actual"
        )
        periods_layout.addWidget(self.average_card)
        
        layout.addLayout(periods_layout)
        
        return section
    
    def create_tabs_panel(self):
        """Crear panel de tabs con funcionalidades"""
        self.tabs_widget = QTabWidget()
        
        # Tab 1: Registro diario - PERMITIDO para empleados
        daily_tab = self.create_daily_tab()
        self.tabs_widget.addTab(daily_tab, "📅 Registro Diario")
        
        # Tab 2: Consultas y reportes - RESTRINGIDO (necesita cerrar caja)
        reports_tab = self.create_reports_tab()
        self.tabs_widget.addTab(reports_tab, "📊 Consultas")
        
        # Tab 3: Administración - RESTRINGIDO (necesita editar montos)
        admin_tab = self.create_admin_tab()
        self.tabs_widget.addTab(admin_tab, "⚙️ Administración")
        
        # Tab 4: Log de actividad - RESTRINGIDO (solo admin)
        log_tab = self.create_log_tab()
        self.tabs_widget.addTab(log_tab, "📋 Log")
        
        return self.tabs_widget
    
    def create_daily_tab(self):
        """Crear tab de registro diario - Permitido para empleados"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Formulario de registro
        form_group = QGroupBox("Registrar Cierre de Caja")
        form_layout = QFormLayout(form_group)
        
        # Fecha
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        form_layout.addRow("Fecha:", self.date_edit)
        
        # Monto efectivo
        self.efectivo_input = QDoubleSpinBox()
        self.efectivo_input.setMaximum(999999.99)
        self.efectivo_input.setPrefix("$")
        self.efectivo_input.setDecimals(2)
        form_layout.addRow("Efectivo:", self.efectivo_input)
        
        # Monto transferencia
        self.transfer_input = QDoubleSpinBox()
        self.transfer_input.setMaximum(999999.99)
        self.transfer_input.setPrefix("$")
        self.transfer_input.setDecimals(2)
        form_layout.addRow("Transferencias:", self.transfer_input)
        
        # Observaciones
        self.observaciones_input = QLineEdit()
        self.observaciones_input.setPlaceholderText("Observaciones opcionales...")
        form_layout.addRow("Observaciones:", self.observaciones_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.register_btn = QPushButton("💾 Registrar")
        self.register_btn.setObjectName("ActionBtn")
        self.register_btn.setProperty("class", "ActionBtn success")
        buttons_layout.addWidget(self.register_btn)
        
        self.clear_form_btn = QPushButton("🧹 Limpiar")
        self.clear_form_btn.setObjectName("ActionBtn")
        self.clear_form_btn.setProperty("class", "ActionBtn")
        buttons_layout.addWidget(self.clear_form_btn)
        
        buttons_layout.addStretch()
        form_layout.addRow(buttons_layout)
        
        layout.addWidget(form_group)
        layout.addStretch()
        
        return tab
    
    def create_reports_tab(self):
        """Crear tab de consultas y reportes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Controles de filtro
        filter_group = QGroupBox("Filtros de Consulta")
        filter_layout = QHBoxLayout(filter_group)
        
        filter_layout.addWidget(QLabel("Desde:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)
        
        self.search_btn = QPushButton("🔍 Buscar")
        self.search_btn.setObjectName("ActionBtn")
        self.search_btn.setProperty("class", "ActionBtn")
        filter_layout.addWidget(self.search_btn)
        
        filter_layout.addStretch()
        layout.addWidget(filter_group)
        
        # Tabla de resultados
        self.results_table = QTableWidget()
        self.results_table.setObjectName("CajaTable")
        self.results_table.setProperty("class", "CajaTable")
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "Fecha", "Efectivo", "Transferencias", "Total", "Usuario", "Hora", "Observaciones"
        ])
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.results_table)
        
        return tab
    
    def create_admin_tab(self):
        """Crear tab de administración"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Sección de actualización
        update_group = QGroupBox("Actualizar Registro")
        update_layout = QFormLayout(update_group)
        
        self.update_date = QDateEdit()
        self.update_date.setDate(QDate.currentDate())
        self.update_date.setCalendarPopup(True)
        update_layout.addRow("Fecha:", self.update_date)
        
        update_buttons = QHBoxLayout()
        self.load_update_btn = QPushButton("📥 Cargar Datos")
        self.load_update_btn.setObjectName("ActionBtn")
        self.load_update_btn.setProperty("class", "ActionBtn")
        update_buttons.addWidget(self.load_update_btn)
        
        self.save_update_btn = QPushButton("💾 Guardar Cambios")
        self.save_update_btn.setObjectName("ActionBtn")
        self.save_update_btn.setProperty("class", "ActionBtn warning")
        self.save_update_btn.setEnabled(False)
        update_buttons.addWidget(self.save_update_btn)
        
        update_buttons.addStretch()
        update_layout.addRow(update_buttons)
        
        self.update_efectivo = QDoubleSpinBox()
        self.update_efectivo.setMaximum(999999.99)
        self.update_efectivo.setPrefix("$")
        self.update_efectivo.setDecimals(2)
        self.update_efectivo.setEnabled(False)
        update_layout.addRow("Nuevo Efectivo:", self.update_efectivo)
        
        self.update_transfer = QDoubleSpinBox()
        self.update_transfer.setMaximum(999999.99)
        self.update_transfer.setPrefix("$")
        self.update_transfer.setDecimals(2)
        self.update_transfer.setEnabled(False)
        update_layout.addRow("Nuevas Transferencias:", self.update_transfer)
        
        self.update_observaciones = QLineEdit()
        self.update_observaciones.setEnabled(False)
        update_layout.addRow("Nuevas Observaciones:", self.update_observaciones)
        
        layout.addWidget(update_group)
        
        # Sección de eliminación
        delete_group = QGroupBox("Eliminar Registro")
        delete_layout = QFormLayout(delete_group)
        
        self.delete_date = QDateEdit()
        self.delete_date.setDate(QDate.currentDate())
        self.delete_date.setCalendarPopup(True)
        delete_layout.addRow("Fecha:", self.delete_date)
        
        self.delete_motivo = QLineEdit()
        self.delete_motivo.setPlaceholderText("Motivo de eliminación...")
        delete_layout.addRow("Motivo:", self.delete_motivo)
        
        self.delete_btn = QPushButton("🗑️ Eliminar Registro")
        self.delete_btn.setObjectName("ActionBtn")
        self.delete_btn.setProperty("class", "ActionBtn error")
        delete_layout.addRow(self.delete_btn)
        
        layout.addWidget(delete_group)
        
        # Sección de limpieza
        clean_group = QGroupBox("Limpieza de Base de Datos")
        clean_layout = QVBoxLayout(clean_group)
        
        self.count_deleted_btn = QPushButton("📊 Contar Eliminados")
        self.count_deleted_btn.setObjectName("ActionBtn")
        self.count_deleted_btn.setProperty("class", "ActionBtn")
        clean_layout.addWidget(self.count_deleted_btn)
        
        self.clean_deleted_btn = QPushButton("🧹 Limpiar Eliminados")
        self.clean_deleted_btn.setObjectName("ActionBtn")
        self.clean_deleted_btn.setProperty("class", "ActionBtn error")
        clean_layout.addWidget(self.clean_deleted_btn)
        
        layout.addWidget(clean_group)
        layout.addStretch()
        
        return tab
    
    def create_log_tab(self):
        """Crear tab de log de actividad"""
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
        # Header buttons
        self.refresh_btn.clicked.connect(self.refresh_all_data)
        self.register_today_btn.clicked.connect(self.quick_register_today)
        
        # Daily tab
        self.register_btn.clicked.connect(self.register_daily_closing)
        self.clear_form_btn.clicked.connect(self.clear_form)
        
        # Reports tab (solo si tienen permisos)
        self.search_btn.clicked.connect(self.search_closings)
        
        # Admin tab (solo si tienen permisos)
        self.load_update_btn.clicked.connect(self.load_update_data)
        self.save_update_btn.clicked.connect(self.save_update_data)
        self.delete_btn.clicked.connect(self.delete_closing)
        self.count_deleted_btn.clicked.connect(self.count_deleted_records)
        self.clean_deleted_btn.clicked.connect(self.clean_deleted_records)
    
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
        """Cargar datos iniciales - solo si hay permisos configurados"""
        if not self.permisos_manager:
            return
        
        self.log_message("Iniciando carga de datos de caja...")
        self.refresh_all_data()
    
    def refresh_all_data(self):
        """Actualizar todos los datos"""
        if not self.permisos_manager or not self.permisos_manager.puede_ver_movimientos_caja():
            self.log_message("Sin permisos para actualizar datos", "WARNING")
            return
        
        if self.is_loading:
            return
        
        self.set_loading(True)
        self.log_message("Actualizando todos los datos...")
        
        try:
            self.refresh_today_metrics()
            self.refresh_period_metrics()
            
            self.last_update = datetime.now()
            self.log_message("Datos actualizados exitosamente")
            self.data_updated.emit()
            
        except Exception as e:
            self.log_message(f"Error actualizando datos: {str(e)}", "ERROR")
            if self.permisos_manager and self.permisos_manager.puede_ver_movimientos_caja():
                QMessageBox.warning(self, "Error", f"Error al actualizar datos:\n{str(e)}")
        
        finally:
            self.set_loading(False)
    
    def refresh_today_metrics(self):
        """Actualizar métricas de hoy"""
        if not self.permisos_manager or not self.permisos_manager.puede_ver_movimientos_caja():
            return
        
        try:
            # Consultar cierre de hoy
            today_result = controller.consultar_caja_hoy_controller()
            
            if today_result["success"]:
                data = today_result["data"]
                
                # Hay cierre registrado
                self.today_status_card.update_value(
                    "✅ Registrado",
                    f"Hora: {data['hora_cierre'][:5]}",
                    "success"
                )
                
                self.today_efectivo_card.update_value(
                    f"${data['monto_efectivo']:,.2f}",
                    "Dinero en caja",
                    "success" if data['monto_efectivo'] > 0 else "normal"
                )
                
                self.today_transfer_card.update_value(
                    f"${data['monto_transferencia']:,.2f}",
                    "Cobros digitales",
                    "success" if data['monto_transferencia'] > 0 else "normal"
                )
                
                self.today_total_card.update_value(
                    f"${data['monto_total']:,.2f}",
                    "Total del día",
                    "success" if data['monto_total'] > 0 else "warning"
                )
                
                # Actualizar formulario con datos actuales (solo si pueden registrar)
                if self.permisos_manager.puede_abrir_caja():
                    fecha_obj = datetime.strptime(data['fecha'], "%Y-%m-%d").date()
                    self.date_edit.setDate(QDate(fecha_obj))
                    self.efectivo_input.setValue(data['monto_efectivo'])
                    self.transfer_input.setValue(data['monto_transferencia'])
                    self.observaciones_input.setText(data['observaciones'] or "")
                
            else:
                # No hay cierre registrado para hoy
                self.today_status_card.update_value(
                    "⏳ Pendiente",
                    "Sin registrar",
                    "warning"
                )
                
                self.today_efectivo_card.update_value("$0", "Sin registrar", "normal")
                self.today_transfer_card.update_value("$0", "Sin registrar", "normal")
                self.today_total_card.update_value("$0", "Sin registrar", "normal")
                
        except Exception as e:
            self.log_message(f"Error actualizando métricas de hoy: {str(e)}", "ERROR")
    
    def refresh_period_metrics(self):
        """Actualizar métricas por período"""
        if not self.permisos_manager or not self.permisos_manager.puede_ver_movimientos_caja():
            return
        
        try:
            # Semana
            week_result = controller.listar_cierres_semana_controller()
            if week_result["success"] and week_result["data"]["cierres"]:
                week_total = week_result["data"]["resumen"]["total_general"]
                week_days = week_result["data"]["resumen"]["cantidad_cierres"]
                self.week_card.update_value(
                    f"${week_total:,.0f}",
                    f"{week_days} días registrados",
                    "success" if week_total > 0 else "normal"
                )
            else:
                self.week_card.update_value("$0", "Sin registros", "normal")
            
            # Mes actual
            month_result = controller.listar_cierres_mes_actual_controller()
            if month_result["success"] and month_result["data"]["cierres"]:
                month_total = month_result["data"]["resumen"]["total_general"]
                month_days = month_result["data"]["resumen"]["cantidad_cierres"]
                month_avg = month_result["data"]["resumen"]["promedio_diario"]
                
                self.month_card.update_value(
                    f"${month_total:,.0f}",
                    f"{month_days} días trabajados",
                    "success" if month_total > 0 else "normal"
                )
                
                self.average_card.update_value(
                    f"${month_avg:,.0f}",
                    "Promedio diario",
                    "success" if month_avg > 0 else "normal"
                )
            else:
                self.month_card.update_value("$0", "Sin registros", "normal")
                self.average_card.update_value("$0", "Sin datos", "normal")
                
        except Exception as e:
            self.log_message(f"Error actualizando métricas de período: {str(e)}", "ERROR")
    
    def quick_register_today(self):
        """Registro rápido del día actual"""
        if not self.permisos_manager or not self.permisos_manager.puede_abrir_caja():
            QMessageBox.warning(self, "Sin permisos", "No tiene permisos para registrar caja")
            return
        
        # Cambiar a la pestaña de registro diario
        self.tabs_widget.setCurrentIndex(0)
    
    def register_daily_closing(self):
        """Registrar cierre diario"""
        if not self.permisos_manager or not self.permisos_manager.puede_abrir_caja():
            QMessageBox.warning(self, "Sin permisos", "No tiene permisos para registrar caja")
            return
        
        try:
            fecha = self.date_edit.date().toString("yyyy-MM-dd")
            efectivo = self.efectivo_input.value()
            transferencia = self.transfer_input.value()
            observaciones = self.observaciones_input.text().strip()
            
            if efectivo == 0 and transferencia == 0:
                reply = QMessageBox.question(
                    self, "Confirmar",
                    "¿Registrar cierre con $0 en ambos montos?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Validar si ya existe
            validacion = controller.validar_puede_registrar_caja_controller(fecha)
            
            if not validacion["puede_registrar"]:
                reply = QMessageBox.question(
                    self, "Ya existe",
                    f"Ya existe un cierre para {fecha}.\n¿Actualizar en su lugar?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # Obtener ID del registro existente
                    consulta = controller.consultar_caja_por_fecha_controller(fecha)
                    if consulta["success"]:
                        cierre_id = consulta["data"]["id"]
                        resultado = controller.actualizar_caja_controller(
                            cierre_id=cierre_id,
                            monto_efectivo=efectivo,
                            monto_transferencia=transferencia,
                            observaciones=observaciones
                        )
                        
                        if resultado["success"]:
                            self.log_message(f"Cierre actualizado para {fecha}: ${resultado['data']['monto_total']:,.2f}")
                            QMessageBox.information(self, "Éxito", "Cierre actualizado exitosamente!")
                            self.refresh_all_data()
                        else:
                            QMessageBox.warning(self, "Error", f"Error al actualizar:\n{resultado['message']}")
                return
            
            # Registrar nuevo
            resultado = controller.registrar_caja_diaria_controller(
                fecha=fecha,
                monto_efectivo=efectivo,
                monto_transferencia=transferencia,
                usuario_id=self.current_user_id,
                observaciones=observaciones
            )
            
            if resultado["success"]:
                data = resultado["data"]
                self.log_message(f"Cierre registrado para {fecha}: ${data['monto_total']:,.2f}")
                QMessageBox.information(
                    self, "Éxito",
                    f"Cierre registrado exitosamente!\nTotal: ${data['monto_total']:,.2f}"
                )
                self.refresh_all_data()
            else:
                QMessageBox.warning(self, "Error", f"Error al registrar:\n{resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error en registro: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")
    
    def clear_form(self):
        """Limpiar formulario"""
        if not self.permisos_manager or not self.permisos_manager.puede_abrir_caja():
            return
        
        self.date_edit.setDate(QDate.currentDate())
        self.efectivo_input.setValue(0)
        self.transfer_input.setValue(0)
        self.observaciones_input.clear()
    
    # Métodos que requieren permisos especiales
    def search_closings(self):
        """Buscar cierres en rango de fechas - Requiere cerrar caja"""
        if not self.permisos_manager or not self.permisos_manager.puede_cerrar_caja():
            QMessageBox.warning(self, "Sin permisos", "No tiene permisos para consultar registros")
            return
        
        # Implementar búsqueda...
        pass
    
    def load_update_data(self):
        """Cargar datos para actualización - Requiere editar montos"""
        if not self.permisos_manager or not self.permisos_manager.puede_editar_montos_caja():
            QMessageBox.warning(self, "Sin permisos", "No tiene permisos para editar registros")
            return
        
        # Implementar carga...
        pass
    
    def save_update_data(self):
        """Guardar datos actualizados - Requiere editar montos"""
        if not self.permisos_manager or not self.permisos_manager.puede_editar_montos_caja():
            QMessageBox.warning(self, "Sin permisos", "No tiene permisos para editar registros")
            return
        
        # Implementar guardado...
        pass
    
    def delete_closing(self):
        """Eliminar cierre - Requiere editar montos"""
        if not self.permisos_manager or not self.permisos_manager.puede_editar_montos_caja():
            QMessageBox.warning(self, "Sin permisos", "No tiene permisos para eliminar registros")
            return
        
        # Implementar eliminación...
        pass
    
    def count_deleted_records(self):
        """Contar registros eliminados - Solo admin"""
        if not self.permisos_manager or not self.permisos_manager.is_admin:
            QMessageBox.warning(self, "Sin permisos", "Solo administradores pueden ver registros eliminados")
            return
        
        # Implementar conteo...
        pass
    
    def clean_deleted_records(self):
        """Limpiar registros eliminados permanentemente - Solo admin"""
        if not self.permisos_manager or not self.permisos_manager.is_admin:
            QMessageBox.warning(self, "Sin permisos", "Solo administradores pueden limpiar registros eliminados")
            return
        
        # Implementar limpieza...
        pass

# ===== Demo =====
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = CajaTab()
    w.resize(1400, 900)
    w.show()
    sys.exit(app.exec())