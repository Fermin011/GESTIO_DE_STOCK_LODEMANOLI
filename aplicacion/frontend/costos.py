# aplicacion/frontend/costos.py
from __future__ import annotations
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
    QProgressBar, QTabWidget, QTextEdit, QSplitter, QScrollArea, QLineEdit,
    QDateEdit, QSpinBox, QDoubleSpinBox, QFormLayout, QGroupBox, QGridLayout,
    QCheckBox, QRadioButton, QButtonGroup
)
from datetime import date, datetime, timedelta
import calendar

# Importar el controller del backend
from aplicacion.backend.costos import controller

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

QFrame.MetricCard.info {{
    background: {CARD_INFO};
    border-color: {TEXT_INFO};
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

QPushButton.ActionBtn.purple {{
    background: {ACCENT_PURPLE};
}}

QPushButton.ActionBtn.purple:hover {{
    background: #7B1FA2;
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

QComboBox, QCheckBox, QRadioButton {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
    color: {TEXT_DARK};
}}

QComboBox:focus {{
    border-color: {ACCENT_BLUE};
}}

QTableWidget#CostosTable {{
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
"""

class MetricCard(QFrame):
    """Tarjeta de métrica personalizada para costos"""
    
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

class CostosTab(QWidget):
    """Vista principal de gestión de costos e impuestos"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Root")
        self.setStyleSheet(QSS)
        
        # Variables de estado
        self.is_loading = False
        self.last_update = None
        self.selected_costo_id = None
        self.selected_impuesto_id = None
        
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
        # Timer para actualizaciones automáticas
        self.auto_timer = QTimer()
        self.auto_timer.timeout.connect(self.refresh_summary_metrics)
        self.auto_timer.start(600000)  # Cada 10 minutos
    
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
        
        splitter.setSizes([300, 500])
        main_layout.addWidget(splitter)
    
    def create_header(self):
        """Crear header con título y controles"""
        header = QFrame()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("💸 GESTIÓN DE COSTOS E IMPUESTOS")
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
        
        return header
    
    def create_metrics_panel(self):
        """Crear panel principal de métricas"""
        panel = QFrame()
        panel.setObjectName("MainFrame")
        panel.setProperty("class", "MainFrame")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)
        
        # Métricas de COSTOS OPERATIVOS
        costos_section = self.create_costos_section()
        layout.addWidget(costos_section)
        
        # Métricas de IMPUESTOS
        impuestos_section = self.create_impuestos_section()
        layout.addWidget(impuestos_section)
        
        return panel
    
    def create_costos_section(self):
        """Crear sección de métricas de costos operativos"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("COSTOS OPERATIVOS")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Grid de tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # Total de costos
        self.costos_total_card = MetricCard(
            "TOTAL COSTOS", 
            "$0", 
            "Costos activos"
        )
        cards_layout.addWidget(self.costos_total_card)
        
        # Costos recurrentes
        self.costos_recurrentes_card = MetricCard(
            "RECURRENTES", 
            "$0", 
            "Gastos mensuales"
        )
        cards_layout.addWidget(self.costos_recurrentes_card)
        
        # Costos una vez
        self.costos_una_vez_card = MetricCard(
            "UNA VEZ", 
            "$0", 
            "Gastos puntuales"
        )
        cards_layout.addWidget(self.costos_una_vez_card)
        
        # Cantidad de costos
        self.costos_cantidad_card = MetricCard(
            "CANTIDAD", 
            "0", 
            "Costos registrados"
        )
        cards_layout.addWidget(self.costos_cantidad_card)
        
        layout.addLayout(cards_layout)
        
        return section
    
    def create_impuestos_section(self):
        """Crear sección de métricas de impuestos"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("IMPUESTOS")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Grid de tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # Impuestos fijos
        self.impuestos_fijos_card = MetricCard(
            "IMPUESTOS FIJOS", 
            "$0", 
            "Montos fijos"
        )
        cards_layout.addWidget(self.impuestos_fijos_card)
        
        # Impuestos porcentuales
        self.impuestos_porcentaje_card = MetricCard(
            "PORCENTAJES", 
            "0%", 
            "Impuestos variables"
        )
        cards_layout.addWidget(self.impuestos_porcentaje_card)
        
        # Total general
        self.total_general_card = MetricCard(
            "TOTAL GENERAL", 
            "$0", 
            "Costos + Imp. Fijos"
        )
        cards_layout.addWidget(self.total_general_card)
        
        # Cantidad impuestos
        self.impuestos_cantidad_card = MetricCard(
            "CANTIDAD", 
            "0", 
            "Impuestos activos"
        )
        cards_layout.addWidget(self.impuestos_cantidad_card)
        
        layout.addLayout(cards_layout)
        
        return section
    
    def create_tabs_panel(self):
        """Crear panel de tabs con funcionalidades"""
        tabs = QTabWidget()
        
        # Tab 1: Costos Operativos
        costos_tab = self.create_costos_tab()
        tabs.addTab(costos_tab, "💼 Costos Operativos")
        
        # Tab 2: Impuestos
        impuestos_tab = self.create_impuestos_tab()
        tabs.addTab(impuestos_tab, "💰 Impuestos")
        
        # Tab 3: Resumen General
        resumen_tab = self.create_resumen_tab()
        tabs.addTab(resumen_tab, "📊 Resumen")
        
        # Tab 4: Administración
        admin_tab = self.create_admin_tab()
        tabs.addTab(admin_tab, "⚙️ Administración")
        
        # Tab 5: Log
        log_tab = self.create_log_tab()
        tabs.addTab(log_tab, "📝 Log")
        
        return tabs
    
    def create_costos_tab(self):
        """Crear tab de costos operativos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Formulario de creación
        form_group = QGroupBox("Crear Nuevo Costo Operativo")
        form_layout = QFormLayout(form_group)
        
        self.costo_nombre_input = QLineEdit()
        self.costo_nombre_input.setPlaceholderText("Ej: Alquiler, Servicios, etc...")
        form_layout.addRow("Nombre:", self.costo_nombre_input)
        
        self.costo_monto_input = QDoubleSpinBox()
        self.costo_monto_input.setMaximum(999999.99)
        self.costo_monto_input.setPrefix("$")
        self.costo_monto_input.setDecimals(2)
        form_layout.addRow("Monto:", self.costo_monto_input)
        
        self.costo_fecha_input = QDateEdit()
        self.costo_fecha_input.setDate(QDate.currentDate())
        self.costo_fecha_input.setCalendarPopup(True)
        form_layout.addRow("Fecha Inicio:", self.costo_fecha_input)
        
        self.costo_recurrente_input = QCheckBox("Es un costo recurrente (mensual)")
        form_layout.addRow("", self.costo_recurrente_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.crear_costo_btn = QPushButton("💾 Crear Costo")
        self.crear_costo_btn.setObjectName("ActionBtn")
        self.crear_costo_btn.setProperty("class", "ActionBtn success")
        buttons_layout.addWidget(self.crear_costo_btn)
        
        self.limpiar_costo_btn = QPushButton("🧹 Limpiar")
        self.limpiar_costo_btn.setObjectName("ActionBtn")
        self.limpiar_costo_btn.setProperty("class", "ActionBtn")
        buttons_layout.addWidget(self.limpiar_costo_btn)
        
        buttons_layout.addStretch()
        form_layout.addRow(buttons_layout)
        
        layout.addWidget(form_group)
        
        # Tabla de costos operativos
        table_group = QGroupBox("Costos Operativos Existentes")
        table_layout = QVBoxLayout(table_group)
        
        # Filtros
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Mostrar:"))
        
        self.costos_filter_combo = QComboBox()
        self.costos_filter_combo.addItems(["Solo activos", "Todos", "Solo inactivos"])
        filter_layout.addWidget(self.costos_filter_combo)
        
        self.refresh_costos_btn = QPushButton("🔄 Actualizar")
        self.refresh_costos_btn.setObjectName("ActionBtn")
        self.refresh_costos_btn.setProperty("class", "ActionBtn")
        filter_layout.addWidget(self.refresh_costos_btn)
        
        filter_layout.addStretch()
        table_layout.addLayout(filter_layout)
        
        # Tabla
        self.costos_table = QTableWidget()
        self.costos_table.setObjectName("CostosTable")
        self.costos_table.setProperty("class", "CostosTable")
        self.costos_table.setColumnCount(7)
        self.costos_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Monto", "Fecha Inicio", "Recurrente", "Estado", "Acciones"
        ])
        
        header = self.costos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        
        table_layout.addWidget(self.costos_table)
        layout.addWidget(table_group)
        
        return tab
    
    def create_impuestos_tab(self):
        """Crear tab de impuestos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Formulario de creación
        form_group = QGroupBox("Crear Nuevo Impuesto")
        form_layout = QFormLayout(form_group)
        
        self.impuesto_nombre_input = QLineEdit()
        self.impuesto_nombre_input.setPlaceholderText("Ej: IVA, Ingresos Brutos, etc...")
        form_layout.addRow("Nombre:", self.impuesto_nombre_input)
        
        # Tipo de impuesto
        tipo_layout = QHBoxLayout()
        self.tipo_grupo = QButtonGroup()
        
        self.tipo_porcentaje_radio = QRadioButton("Porcentaje (%)")
        self.tipo_porcentaje_radio.setChecked(True)
        self.tipo_grupo.addButton(self.tipo_porcentaje_radio, 0)
        tipo_layout.addWidget(self.tipo_porcentaje_radio)
        
        self.tipo_fijo_radio = QRadioButton("Monto Fijo ($)")
        self.tipo_grupo.addButton(self.tipo_fijo_radio, 1)
        tipo_layout.addWidget(self.tipo_fijo_radio)
        
        tipo_layout.addStretch()
        form_layout.addRow("Tipo:", tipo_layout)
        
        self.impuesto_valor_input = QDoubleSpinBox()
        self.impuesto_valor_input.setMaximum(999999.99)
        self.impuesto_valor_input.setDecimals(2)
        self.impuesto_valor_input.setSuffix("%")
        form_layout.addRow("Valor:", self.impuesto_valor_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        self.crear_impuesto_btn = QPushButton("💾 Crear Impuesto")
        self.crear_impuesto_btn.setObjectName("ActionBtn")
        self.crear_impuesto_btn.setProperty("class", "ActionBtn success")
        buttons_layout.addWidget(self.crear_impuesto_btn)
        
        self.limpiar_impuesto_btn = QPushButton("🧹 Limpiar")
        self.limpiar_impuesto_btn.setObjectName("ActionBtn")
        self.limpiar_impuesto_btn.setProperty("class", "ActionBtn")
        buttons_layout.addWidget(self.limpiar_impuesto_btn)
        
        buttons_layout.addStretch()
        form_layout.addRow(buttons_layout)
        
        layout.addWidget(form_group)
        
        # Tabla de impuestos
        table_group = QGroupBox("Impuestos Existentes")
        table_layout = QVBoxLayout(table_group)
        
        # Filtros
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Mostrar:"))
        
        self.impuestos_filter_combo = QComboBox()
        self.impuestos_filter_combo.addItems(["Solo activos", "Todos", "Solo inactivos"])
        filter_layout.addWidget(self.impuestos_filter_combo)
        
        self.refresh_impuestos_btn = QPushButton("🔄 Actualizar")
        self.refresh_impuestos_btn.setObjectName("ActionBtn")
        self.refresh_impuestos_btn.setProperty("class", "ActionBtn")
        filter_layout.addWidget(self.refresh_impuestos_btn)
        
        filter_layout.addStretch()
        table_layout.addLayout(filter_layout)
        
        # Tabla
        self.impuestos_table = QTableWidget()
        self.impuestos_table.setObjectName("CostosTable")
        self.impuestos_table.setProperty("class", "CostosTable")
        self.impuestos_table.setColumnCount(6)
        self.impuestos_table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Tipo", "Valor", "Estado", "Acciones"
        ])
        
        header = self.impuestos_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        table_layout.addWidget(self.impuestos_table)
        layout.addWidget(table_group)
        
        return tab
    
    def create_resumen_tab(self):
        """Crear tab de resumen general"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Calculadora de impacto
        calc_group = QGroupBox("Calculadora de Impacto")
        calc_layout = QFormLayout(calc_group)
        
        self.venta_ejemplo_input = QDoubleSpinBox()
        self.venta_ejemplo_input.setMaximum(999999.99)
        self.venta_ejemplo_input.setPrefix("$")
        self.venta_ejemplo_input.setValue(1000)
        self.venta_ejemplo_input.setDecimals(2)
        calc_layout.addRow("Venta de ejemplo:", self.venta_ejemplo_input)
        
        self.calcular_impacto_btn = QPushButton("🧮 Calcular Impacto")
        self.calcular_impacto_btn.setObjectName("ActionBtn")
        self.calcular_impacto_btn.setProperty("class", "ActionBtn purple")
        calc_layout.addRow("", self.calcular_impacto_btn)
        
        # Resultados
        self.resultado_bruto_label = QLabel("Venta: $0")
        self.resultado_bruto_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        calc_layout.addRow("", self.resultado_bruto_label)
        
        self.resultado_impuestos_label = QLabel("Impuestos: $0")
        self.resultado_impuestos_label.setStyleSheet("font-size: 14px; color: #FF9800;")
        calc_layout.addRow("", self.resultado_impuestos_label)
        
        self.resultado_neto_label = QLabel("Neto: $0")
        self.resultado_neto_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        calc_layout.addRow("", self.resultado_neto_label)
        
        layout.addWidget(calc_group)
        
        # Resumen detallado
        detalle_group = QGroupBox("Resumen Detallado")
        self.resumen_text = QTextEdit()
        self.resumen_text.setMaximumHeight(300)
        detalle_layout = QVBoxLayout(detalle_group)
        detalle_layout.addWidget(self.resumen_text)
        
        layout.addWidget(detalle_group)
        layout.addStretch()
        
        return tab
    
    def create_admin_tab(self):
        """Crear tab de administración"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Sección de edición
        edit_group = QGroupBox("Editar Registros")
        edit_layout = QVBoxLayout(edit_group)
        
        edit_info = QLabel("Selecciona un elemento en las tablas de las otras pestañas para editarlo aquí")
        edit_info.setStyleSheet("color: #72767D; font-style: italic;")
        edit_layout.addWidget(edit_info)
        
        # Formulario de edición (se habilita cuando se selecciona algo)
        self.edit_form_group = QGroupBox("Datos del Registro")
        self.edit_form_group.setEnabled(False)
        edit_form_layout = QFormLayout(self.edit_form_group)
        
        self.edit_nombre_input = QLineEdit()
        edit_form_layout.addRow("Nombre:", self.edit_nombre_input)
        
        self.edit_valor_input = QDoubleSpinBox()
        self.edit_valor_input.setMaximum(999999.99)
        self.edit_valor_input.setDecimals(2)
        edit_form_layout.addRow("Valor/Monto:", self.edit_valor_input)
        
        self.edit_activo_check = QCheckBox("Registro activo")
        edit_form_layout.addRow("", self.edit_activo_check)
        
        edit_buttons = QHBoxLayout()
        self.guardar_cambios_btn = QPushButton("💾 Guardar Cambios")
        self.guardar_cambios_btn.setObjectName("ActionBtn")
        self.guardar_cambios_btn.setProperty("class", "ActionBtn warning")
        edit_buttons.addWidget(self.guardar_cambios_btn)
        
        self.cancelar_edit_btn = QPushButton("❌ Cancelar")
        self.cancelar_edit_btn.setObjectName("ActionBtn")
        self.cancelar_edit_btn.setProperty("class", "ActionBtn")
        edit_buttons.addWidget(self.cancelar_edit_btn)
        
        edit_buttons.addStretch()
        edit_form_layout.addRow(edit_buttons)
        
        edit_layout.addWidget(self.edit_form_group)
        layout.addWidget(edit_group)
        
        # Sección de eliminación masiva
        delete_group = QGroupBox("Limpieza de Base de Datos")
        delete_layout = QVBoxLayout(delete_group)
        
        self.count_deleted_btn = QPushButton("📊 Contar Eliminados")
        self.count_deleted_btn.setObjectName("ActionBtn")
        self.count_deleted_btn.setProperty("class", "ActionBtn")
        delete_layout.addWidget(self.count_deleted_btn)
        
        self.clean_costos_btn = QPushButton("🧹 Limpiar Solo Costos")
        self.clean_costos_btn.setObjectName("ActionBtn")
        self.clean_costos_btn.setProperty("class", "ActionBtn warning")
        delete_layout.addWidget(self.clean_costos_btn)
        
        self.clean_impuestos_btn = QPushButton("🧹 Limpiar Solo Impuestos")
        self.clean_impuestos_btn.setObjectName("ActionBtn")
        self.clean_impuestos_btn.setProperty("class", "ActionBtn warning")
        delete_layout.addWidget(self.clean_impuestos_btn)
        
        self.clean_all_btn = QPushButton("🗑️ Limpiar TODO")
        self.clean_all_btn.setObjectName("ActionBtn")
        self.clean_all_btn.setProperty("class", "ActionBtn error")
        delete_layout.addWidget(self.clean_all_btn)
        
        layout.addWidget(delete_group)
        layout.addStretch()
        
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
        
        # Costos operativos
        self.crear_costo_btn.clicked.connect(self.crear_costo_operativo)
        self.limpiar_costo_btn.clicked.connect(self.limpiar_form_costo)
        self.refresh_costos_btn.clicked.connect(self.refresh_costos_table)
        self.costos_filter_combo.currentTextChanged.connect(self.refresh_costos_table)
        self.tipo_porcentaje_radio.toggled.connect(self.update_valor_input_suffix)
        
        # Impuestos
        self.crear_impuesto_btn.clicked.connect(self.crear_impuesto)
        self.limpiar_impuesto_btn.clicked.connect(self.limpiar_form_impuesto)
        self.refresh_impuestos_btn.clicked.connect(self.refresh_impuestos_table)
        self.impuestos_filter_combo.currentTextChanged.connect(self.refresh_impuestos_table)
        
        # Resumen
        self.calcular_impacto_btn.clicked.connect(self.calcular_impacto_venta)
        
        # Admin
        self.guardar_cambios_btn.clicked.connect(self.guardar_cambios_registro)
        self.cancelar_edit_btn.clicked.connect(self.cancelar_edicion)
        self.count_deleted_btn.clicked.connect(self.contar_eliminados)
        self.clean_costos_btn.clicked.connect(self.limpiar_costos_eliminados)
        self.clean_impuestos_btn.clicked.connect(self.limpiar_impuestos_eliminados)
        self.clean_all_btn.clicked.connect(self.limpiar_todos_eliminados)
    
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
        self.log_message("Iniciando carga de datos de costos e impuestos...")
        self.refresh_all_data()
    
    def refresh_all_data(self):
        """Actualizar todos los datos"""
        if self.is_loading:
            return
        
        self.set_loading(True)
        self.log_message("Actualizando todos los datos...")
        
        try:
            self.refresh_summary_metrics()
            self.refresh_costos_table()
            self.refresh_impuestos_table()
            self.update_resumen_detallado()
            
            self.last_update = datetime.now()
            self.log_message("Datos actualizados exitosamente")
            self.data_updated.emit()
            
        except Exception as e:
            self.log_message(f"Error actualizando datos: {str(e)}", "ERROR")
            QMessageBox.warning(self, "Error", f"Error al actualizar datos:\n{str(e)}")
        
        finally:
            self.set_loading(False)
    
    def refresh_summary_metrics(self):
        """Actualizar métricas del resumen"""
        try:
            resultado = controller.obtener_resumen_completo_controller()
            
            if resultado["success"]:
                data = resultado["data"]
                costos = data["costos_operativos"]
                impuestos = data["impuestos"]
                general = data["resumen_general"]
                
                # Actualizar tarjetas de costos
                self.costos_total_card.update_value(
                    f"${costos['total']:,.0f}",
                    "Costos operativos",
                    "success" if costos['total'] > 0 else "normal"
                )
                
                self.costos_recurrentes_card.update_value(
                    f"${costos['recurrentes']:,.0f}",
                    "Gastos mensuales",
                    "info" if costos['recurrentes'] > 0 else "normal"
                )
                
                self.costos_una_vez_card.update_value(
                    f"${costos['una_vez']:,.0f}",
                    "Gastos puntuales",
                    "warning" if costos['una_vez'] > 0 else "normal"
                )
                
                self.costos_cantidad_card.update_value(
                    str(costos['cantidad']),
                    "Costos activos",
                    "success" if costos['cantidad'] > 0 else "normal"
                )
                
                # Actualizar tarjetas de impuestos
                self.impuestos_fijos_card.update_value(
                    f"${impuestos['total_fijo']:,.0f}",
                    f"{impuestos['cantidad_fijo']} impuestos",
                    "info" if impuestos['total_fijo'] > 0 else "normal"
                )
                
                self.impuestos_porcentaje_card.update_value(
                    f"{impuestos['total_porcentaje']:.1f}%",
                    f"{impuestos['cantidad_porcentaje']} impuestos",
                    "warning" if impuestos['total_porcentaje'] > 0 else "normal"
                )
                
                self.total_general_card.update_value(
                    f"${general['total_costos_fijos']:,.0f}",
                    "Costos + Imp. Fijos",
                    "success" if general['total_costos_fijos'] > 0 else "normal"
                )
                
                self.impuestos_cantidad_card.update_value(
                    str(impuestos['cantidad']),
                    "Impuestos activos",
                    "success" if impuestos['cantidad'] > 0 else "normal"
                )
                
            else:
                self.log_message(f"Error obteniendo resumen: {resultado['message']}", "ERROR")
                
        except Exception as e:
            self.log_message(f"Error actualizando métricas: {str(e)}", "ERROR")
    
    def refresh_costos_table(self):
        """Actualizar tabla de costos operativos"""
        try:
            filtro = self.costos_filter_combo.currentText()
            solo_activos = filtro == "Solo activos"
            
            if filtro == "Solo inactivos":
                # Para mostrar solo inactivos, obtenemos todos y filtramos
                resultado = controller.listar_costos_operativos_controller(solo_activos=False)
            else:
                resultado = controller.listar_costos_operativos_controller(solo_activos=solo_activos)
            
            if resultado["success"]:
                costos = resultado["data"]["costos"]
                
                # Filtrar inactivos si es necesario
                if filtro == "Solo inactivos":
                    costos = [c for c in costos if not c["activo"]]
                
                self.costos_table.setRowCount(len(costos))
                
                for row, costo in enumerate(costos):
                    # ID
                    self.costos_table.setItem(row, 0, QTableWidgetItem(str(costo["id"])))
                    
                    # Nombre
                    self.costos_table.setItem(row, 1, QTableWidgetItem(costo["nombre"]))
                    
                    # Monto
                    self.costos_table.setItem(row, 2, QTableWidgetItem(f"${costo['monto']:,.2f}"))
                    
                    # Fecha inicio
                    self.costos_table.setItem(row, 3, QTableWidgetItem(costo["fecha_inicio"]))
                    
                    # Recurrente
                    recurrente_text = "Sí" if costo["recurrente"] else "No"
                    self.costos_table.setItem(row, 4, QTableWidgetItem(recurrente_text))
                    
                    # Estado
                    estado_text = "Activo" if costo["activo"] else "Inactivo"
                    self.costos_table.setItem(row, 5, QTableWidgetItem(estado_text))
                    
                    # Botones de acción
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(5, 2, 5, 2)
                    
                    edit_btn = QPushButton("✏️")
                    edit_btn.setMaximumSize(30, 25)
                    edit_btn.clicked.connect(lambda checked, c_id=costo["id"]: self.editar_costo(c_id))
                    actions_layout.addWidget(edit_btn)
                    
                    if costo["activo"]:
                        delete_btn = QPushButton("🗑️")
                        delete_btn.setMaximumSize(30, 25)
                        delete_btn.clicked.connect(lambda checked, c_id=costo["id"]: self.eliminar_costo(c_id))
                        actions_layout.addWidget(delete_btn)
                    
                    actions_layout.addStretch()
                    self.costos_table.setCellWidget(row, 6, actions_widget)
                
                self.log_message(f"Tabla de costos actualizada: {len(costos)} registros")
            else:
                self.log_message(f"Error cargando costos: {resultado['message']}", "ERROR")
                
        except Exception as e:
            self.log_message(f"Error actualizando tabla de costos: {str(e)}", "ERROR")
    
    def refresh_impuestos_table(self):
        """Actualizar tabla de impuestos"""
        try:
            filtro = self.impuestos_filter_combo.currentText()
            solo_activos = filtro == "Solo activos"
            
            if filtro == "Solo inactivos":
                resultado = controller.listar_impuestos_controller(solo_activos=False)
            else:
                resultado = controller.listar_impuestos_controller(solo_activos=solo_activos)
            
            if resultado["success"]:
                impuestos = resultado["data"]["impuestos"]
                
                # Filtrar inactivos si es necesario
                if filtro == "Solo inactivos":
                    impuestos = [i for i in impuestos if not i["activo"]]
                
                self.impuestos_table.setRowCount(len(impuestos))
                
                for row, impuesto in enumerate(impuestos):
                    # ID
                    self.impuestos_table.setItem(row, 0, QTableWidgetItem(str(impuesto["id"])))
                    
                    # Nombre
                    self.impuestos_table.setItem(row, 1, QTableWidgetItem(impuesto["nombre"]))
                    
                    # Tipo
                    self.impuestos_table.setItem(row, 2, QTableWidgetItem(impuesto["tipo"].title()))
                    
                    # Valor
                    if impuesto["tipo"] == "porcentaje":
                        valor_text = f"{impuesto['valor']:.1f}%"
                    else:
                        valor_text = f"${impuesto['valor']:,.2f}"
                    self.impuestos_table.setItem(row, 3, QTableWidgetItem(valor_text))
                    
                    # Estado
                    estado_text = "Activo" if impuesto["activo"] else "Inactivo"
                    self.impuestos_table.setItem(row, 4, QTableWidgetItem(estado_text))
                    
                    # Botones de acción
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout(actions_widget)
                    actions_layout.setContentsMargins(5, 2, 5, 2)
                    
                    edit_btn = QPushButton("✏️")
                    edit_btn.setMaximumSize(30, 25)
                    edit_btn.clicked.connect(lambda checked, i_id=impuesto["id"]: self.editar_impuesto(i_id))
                    actions_layout.addWidget(edit_btn)
                    
                    if impuesto["activo"]:
                        delete_btn = QPushButton("🗑️")
                        delete_btn.setMaximumSize(30, 25)
                        delete_btn.clicked.connect(lambda checked, i_id=impuesto["id"]: self.eliminar_impuesto(i_id))
                        actions_layout.addWidget(delete_btn)
                    
                    actions_layout.addStretch()
                    self.impuestos_table.setCellWidget(row, 5, actions_widget)
                
                self.log_message(f"Tabla de impuestos actualizada: {len(impuestos)} registros")
            else:
                self.log_message(f"Error cargando impuestos: {resultado['message']}", "ERROR")
                
        except Exception as e:
            self.log_message(f"Error actualizando tabla de impuestos: {str(e)}", "ERROR")
    
    def update_valor_input_suffix(self):
        """Actualizar sufijo del input de valor según el tipo"""
        if self.tipo_porcentaje_radio.isChecked():
            self.impuesto_valor_input.setSuffix("%")
            self.impuesto_valor_input.setMaximum(100)
        else:
            self.impuesto_valor_input.setSuffix("")
            self.impuesto_valor_input.setPrefix("$")
            self.impuesto_valor_input.setMaximum(999999.99)
    
    def crear_costo_operativo(self):
        """Crear nuevo costo operativo"""
        try:
            nombre = self.costo_nombre_input.text().strip()
            if not nombre:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                return
            
            monto = self.costo_monto_input.value()
            fecha_inicio = self.costo_fecha_input.date().toString("yyyy-MM-dd")
            recurrente = self.costo_recurrente_input.isChecked()
            
            resultado = controller.crear_costo_operativo_controller(
                nombre=nombre,
                monto=monto,
                fecha_inicio=fecha_inicio,
                recurrente=recurrente
            )
            
            if resultado["success"]:
                data = resultado["data"]
                self.log_message(f"Costo creado: {data['nombre']} - ${data['monto']:,.2f}")
                QMessageBox.information(self, "Éxito", f"Costo operativo '{data['nombre']}' creado exitosamente!")
                self.limpiar_form_costo()
                self.refresh_all_data()
            else:
                QMessageBox.warning(self, "Error", f"Error al crear costo:\n{resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error creando costo: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")
    
    def crear_impuesto(self):
        """Crear nuevo impuesto"""
        try:
            nombre = self.impuesto_nombre_input.text().strip()
            if not nombre:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                return
            
            tipo = "porcentaje" if self.tipo_porcentaje_radio.isChecked() else "fijo"
            valor = self.impuesto_valor_input.value()
            
            # Validar valor según tipo
            if tipo == "porcentaje" and (valor < 0 or valor > 100):
                QMessageBox.warning(self, "Error", "El porcentaje debe estar entre 0 y 100")
                return
            
            if tipo == "fijo" and valor < 0:
                QMessageBox.warning(self, "Error", "El monto fijo no puede ser negativo")
                return
            
            resultado = controller.crear_impuesto_controller(
                nombre=nombre,
                tipo=tipo,
                valor=valor
            )
            
            if resultado["success"]:
                data = resultado["data"]
                valor_text = f"{data['valor']:.1f}%" if data['tipo'] == 'porcentaje' else f"${data['valor']:,.2f}"
                self.log_message(f"Impuesto creado: {data['nombre']} - {valor_text}")
                QMessageBox.information(self, "Éxito", f"Impuesto '{data['nombre']}' creado exitosamente!")
                self.limpiar_form_impuesto()
                self.refresh_all_data()
            else:
                QMessageBox.warning(self, "Error", f"Error al crear impuesto:\n{resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error creando impuesto: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")
    
    def limpiar_form_costo(self):
        """Limpiar formulario de costo"""
        self.costo_nombre_input.clear()
        self.costo_monto_input.setValue(0)
        self.costo_fecha_input.setDate(QDate.currentDate())
        self.costo_recurrente_input.setChecked(False)
    
    def limpiar_form_impuesto(self):
        """Limpiar formulario de impuesto"""
        self.impuesto_nombre_input.clear()
        self.impuesto_valor_input.setValue(0)
        self.tipo_porcentaje_radio.setChecked(True)
        self.update_valor_input_suffix()
    
    def editar_costo(self, costo_id: int):
        """Iniciar edición de costo operativo"""
        self.selected_costo_id = costo_id
        self.selected_impuesto_id = None
        
        # Cargar datos del costo
        try:
            resultado = controller.listar_costos_operativos_controller(solo_activos=False)
            if resultado["success"]:
                costos = resultado["data"]["costos"]
                costo = next((c for c in costos if c["id"] == costo_id), None)
                
                if costo:
                    self.edit_nombre_input.setText(costo["nombre"])
                    self.edit_valor_input.setValue(costo["monto"])
                    self.edit_activo_check.setChecked(costo["activo"])
                    
                    self.edit_form_group.setEnabled(True)
                    self.edit_form_group.setTitle(f"Editando Costo: {costo['nombre']}")
                    
                    # Cambiar a la pestaña de administración
                    tabs_widget = self.findChild(QTabWidget)
                    if tabs_widget:
                        tabs_widget.setCurrentIndex(3)  # Tab de administración
                    
                    self.log_message(f"Iniciando edición de costo: {costo['nombre']}")
                else:
                    QMessageBox.warning(self, "Error", "No se encontró el costo")
            else:
                QMessageBox.warning(self, "Error", f"Error cargando datos: {resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error cargando costo para edición: {str(e)}", "ERROR")
    
    def editar_impuesto(self, impuesto_id: int):
        """Iniciar edición de impuesto"""
        self.selected_impuesto_id = impuesto_id
        self.selected_costo_id = None
        
        # Cargar datos del impuesto
        try:
            resultado = controller.listar_impuestos_controller(solo_activos=False)
            if resultado["success"]:
                impuestos = resultado["data"]["impuestos"]
                impuesto = next((i for i in impuestos if i["id"] == impuesto_id), None)
                
                if impuesto:
                    self.edit_nombre_input.setText(impuesto["nombre"])
                    self.edit_valor_input.setValue(impuesto["valor"])
                    self.edit_activo_check.setChecked(impuesto["activo"])
                    
                    self.edit_form_group.setEnabled(True)
                    self.edit_form_group.setTitle(f"Editando Impuesto: {impuesto['nombre']} ({impuesto['tipo']})")
                    
                    # Cambiar a la pestaña de administración
                    tabs_widget = self.findChild(QTabWidget)
                    if tabs_widget:
                        tabs_widget.setCurrentIndex(3)  # Tab de administración
                    
                    self.log_message(f"Iniciando edición de impuesto: {impuesto['nombre']}")
                else:
                    QMessageBox.warning(self, "Error", "No se encontró el impuesto")
            else:
                QMessageBox.warning(self, "Error", f"Error cargando datos: {resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error cargando impuesto para edición: {str(e)}", "ERROR")
    
    def guardar_cambios_registro(self):
        """Guardar cambios del registro en edición"""
        try:
            nombre = self.edit_nombre_input.text().strip()
            valor = self.edit_valor_input.value()
            activo = self.edit_activo_check.isChecked()
            
            if not nombre:
                QMessageBox.warning(self, "Error", "El nombre es obligatorio")
                return
            
            if self.selected_costo_id:
                # Actualizar costo operativo
                resultado = controller.actualizar_costo_operativo_controller(
                    costo_id=self.selected_costo_id,
                    nombre=nombre,
                    monto=valor,
                    activo=activo
                )
                
                if resultado["success"]:
                    self.log_message(f"Costo actualizado: {nombre}")
                    QMessageBox.information(self, "Éxito", "Costo operativo actualizado exitosamente!")
                    self.cancelar_edicion()
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error al actualizar:\n{resultado['message']}")
                    
            elif self.selected_impuesto_id:
                # Actualizar impuesto
                resultado = controller.actualizar_impuesto_controller(
                    impuesto_id=self.selected_impuesto_id,
                    nombre=nombre,
                    valor=valor,
                    activo=activo
                )
                
                if resultado["success"]:
                    self.log_message(f"Impuesto actualizado: {nombre}")
                    QMessageBox.information(self, "Éxito", "Impuesto actualizado exitosamente!")
                    self.cancelar_edicion()
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error al actualizar:\n{resultado['message']}")
            else:
                QMessageBox.warning(self, "Error", "No hay registro seleccionado para editar")
                
        except Exception as e:
            self.log_message(f"Error guardando cambios: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")
    
    def cancelar_edicion(self):
        """Cancelar edición actual"""
        self.selected_costo_id = None
        self.selected_impuesto_id = None
        self.edit_form_group.setEnabled(False)
        self.edit_form_group.setTitle("Datos del Registro")
        self.edit_nombre_input.clear()
        self.edit_valor_input.setValue(0)
        self.edit_activo_check.setChecked(True)
    
    def eliminar_costo(self, costo_id: int):
        """Eliminar (desactivar) costo operativo"""
        try:
            reply = QMessageBox.question(
                self, "Confirmar eliminación",
                "¿Está seguro de que desea eliminar este costo operativo?\n\n(Se marcará como inactivo)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                resultado = controller.eliminar_costo_operativo_controller(costo_id)
                
                if resultado["success"]:
                    data = resultado["data"]
                    self.log_message(f"Costo eliminado: {data['nombre']}")
                    QMessageBox.information(self, "Éxito", "Costo operativo eliminado exitosamente!")
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error al eliminar:\n{resultado['message']}")
                    
        except Exception as e:
            self.log_message(f"Error eliminando costo: {str(e)}", "ERROR")
    
    def eliminar_impuesto(self, impuesto_id: int):
        """Eliminar (desactivar) impuesto"""
        try:
            reply = QMessageBox.question(
                self, "Confirmar eliminación",
                "¿Está seguro de que desea eliminar este impuesto?\n\n(Se marcará como inactivo)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                resultado = controller.eliminar_impuesto_controller(impuesto_id)
                
                if resultado["success"]:
                    data = resultado["data"]
                    self.log_message(f"Impuesto eliminado: {data['nombre']}")
                    QMessageBox.information(self, "Éxito", "Impuesto eliminado exitosamente!")
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error al eliminar:\n{resultado['message']}")
                    
        except Exception as e:
            self.log_message(f"Error eliminando impuesto: {str(e)}", "ERROR")
    
    def calcular_impacto_venta(self):
        """Calcular impacto de impuestos en una venta"""
        try:
            venta_base = self.venta_ejemplo_input.value()
            
            # Obtener resumen de impuestos
            resultado = controller.obtener_resumen_completo_controller()
            
            if resultado["success"]:
                impuestos = resultado["data"]["impuestos"]
                
                # Calcular impuestos
                impuestos_fijos = impuestos["total_fijo"]
                porcentaje_total = impuestos["total_porcentaje"]
                
                impuestos_porcentuales = venta_base * (porcentaje_total / 100)
                total_impuestos = impuestos_fijos + impuestos_porcentuales
                venta_neta = venta_base - total_impuestos
                
                # Actualizar labels
                self.resultado_bruto_label.setText(f"Venta Bruta: ${venta_base:,.2f}")
                self.resultado_impuestos_label.setText(f"Impuestos: ${total_impuestos:,.2f} (Fijos: ${impuestos_fijos:,.2f} + {porcentaje_total:.1f}%: ${impuestos_porcentuales:,.2f})")
                self.resultado_neto_label.setText(f"Venta Neta: ${venta_neta:,.2f}")
                
                self.log_message(f"Impacto calculado para venta de ${venta_base:,.2f}: impuestos ${total_impuestos:,.2f}, neto ${venta_neta:,.2f}")
            else:
                QMessageBox.warning(self, "Error", f"Error obteniendo datos: {resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error calculando impacto: {str(e)}", "ERROR")
    
    def update_resumen_detallado(self):
        """Actualizar el resumen detallado"""
        try:
            resultado = controller.obtener_resumen_completo_controller()
            
            if resultado["success"]:
                data = resultado["data"]
                costos = data["costos_operativos"]
                impuestos = data["impuestos"]
                general = data["resumen_general"]
                
                texto = f"""
=== RESUMEN COMPLETO DE COSTOS E IMPUESTOS ===

📊 COSTOS OPERATIVOS:
• Cantidad total: {costos['cantidad']} costos
• Total mensual: ${costos['total']:,.2f}
• Costos recurrentes: ${costos['recurrentes']:,.2f}
• Costos una vez: ${costos['una_vez']:,.2f}

💰 IMPUESTOS:
• Cantidad total: {impuestos['cantidad']} impuestos
• Impuestos fijos: {impuestos['cantidad_fijo']} registros (${impuestos['total_fijo']:,.2f})
• Impuestos porcentaje: {impuestos['cantidad_porcentaje']} registros ({impuestos['total_porcentaje']:.1f}%)

🎯 RESUMEN GENERAL:
• Total costos fijos mensuales: ${general['total_costos_fijos']:,.2f}
• Porcentajes aplicables: {general['porcentajes_aplicables']:.1f}%

📈 EJEMPLO DE IMPACTO (en venta de $10,000):
• Impuestos fijos: ${impuestos['total_fijo']:,.2f}
• Impuestos porcentuales: ${10000 * (impuestos['total_porcentaje'] / 100):,.2f}
• Total impuestos: ${impuestos['total_fijo'] + (10000 * (impuestos['total_porcentaje'] / 100)):,.2f}
• Venta neta: ${10000 - (impuestos['total_fijo'] + (10000 * (impuestos['total_porcentaje'] / 100))):,.2f}

Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """
                
                self.resumen_text.setPlainText(texto)
            else:
                self.resumen_text.setPlainText(f"Error obteniendo resumen: {resultado['message']}")
                
        except Exception as e:
            self.log_message(f"Error actualizando resumen: {str(e)}", "ERROR")
    
    def contar_eliminados(self):
        """Contar registros eliminados"""
        try:
            resultado = controller.contar_registros_eliminados_controller()
            
            if resultado["success"]:
                data = resultado["data"]
                total = data["total"]
                costos_count = data["costos_eliminados"]
                impuestos_count = data["impuestos_eliminados"]
                
                if total == 0:
                    QMessageBox.information(self, "Sin registros", "No hay registros eliminados")
                else:
                    mensaje = f"Registros eliminados encontrados:\n\n"
                    mensaje += f"• Costos operativos: {costos_count}\n"
                    mensaje += f"• Impuestos: {impuestos_count}\n"
                    mensaje += f"• TOTAL: {total}\n\n"
                    mensaje += "Estos registros pueden ser eliminados permanentemente."
                    
                    QMessageBox.information(self, "Registros eliminados", mensaje)
                
                self.log_message(f"Conteo de eliminados: {total} registros ({costos_count} costos, {impuestos_count} impuestos)")
            else:
                QMessageBox.warning(self, "Error", resultado["message"])
                
        except Exception as e:
            self.log_message(f"Error contando eliminados: {str(e)}", "ERROR")
    
    def limpiar_costos_eliminados(self):
        """Limpiar costos operativos eliminados"""
        try:
            reply = QMessageBox.question(
                self, "Confirmar limpieza",
                "¿Eliminar PERMANENTEMENTE todos los costos operativos marcados como eliminados?\n\nEsta acción NO se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                resultado = controller.limpiar_costos_operativos_eliminados_controller()
                
                if resultado["success"]:
                    eliminados = resultado["data"]["registros_eliminados"]
                    QMessageBox.information(
                        self, "Limpieza exitosa",
                        f"Se eliminaron permanentemente {eliminados} costos operativos"
                    )
                    self.log_message(f"Limpieza de costos completada: {eliminados} registros eliminados")
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error en limpieza:\n{resultado['message']}")
                    
        except Exception as e:
            self.log_message(f"Error en limpieza de costos: {str(e)}", "ERROR")
    
    def limpiar_impuestos_eliminados(self):
        """Limpiar impuestos eliminados"""
        try:
            reply = QMessageBox.question(
                self, "Confirmar limpieza",
                "¿Eliminar PERMANENTEMENTE todos los impuestos marcados como eliminados?\n\nEsta acción NO se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                resultado = controller.limpiar_impuestos_eliminados_controller()
                
                if resultado["success"]:
                    eliminados = resultado["data"]["registros_eliminados"]
                    QMessageBox.information(
                        self, "Limpieza exitosa",
                        f"Se eliminaron permanentemente {eliminados} impuestos"
                    )
                    self.log_message(f"Limpieza de impuestos completada: {eliminados} registros eliminados")
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error en limpieza:\n{resultado['message']}")
                    
        except Exception as e:
            self.log_message(f"Error en limpieza de impuestos: {str(e)}", "ERROR")
    
    def limpiar_todos_eliminados(self):
        """Limpiar TODOS los registros eliminados"""
        try:
            reply = QMessageBox.question(
                self, "CONFIRMACIÓN CRÍTICA",
                "¿Eliminar PERMANENTEMENTE TODOS los registros eliminados?\n\n• Costos operativos eliminados\n• Impuestos eliminados\n\nEsta acción NO se puede deshacer JAMÁS.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Confirmación adicional
                reply2 = QMessageBox.question(
                    self, "ÚLTIMA CONFIRMACIÓN",
                    "¿Está COMPLETAMENTE SEGURO?\n\nSe eliminarán PERMANENTEMENTE todos los registros marcados como eliminados.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply2 == QMessageBox.StandardButton.Yes:
                    resultado = controller.limpiar_todos_los_eliminados_controller()
                    
                    if resultado["success"]:
                        data = resultado["data"]
                        total = data["total_eliminados"]
                        costos = data["costos_eliminados"]
                        impuestos = data["impuestos_eliminados"]
                        
                        QMessageBox.information(
                            self, "Limpieza completa exitosa",
                            f"Se eliminaron permanentemente {total} registros:\n• {costos} costos operativos\n• {impuestos} impuestos"
                        )
                        self.log_message(f"Limpieza completa: {total} registros eliminados ({costos} costos, {impuestos} impuestos)")
                        self.refresh_all_data()
                    else:
                        QMessageBox.warning(self, "Error", f"Error en limpieza:\n{resultado['message']}")
                        
        except Exception as e:
            self.log_message(f"Error en limpieza completa: {str(e)}", "ERROR")

# ===== Demo =====
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = CostosTab()
    w.resize(1400, 900)
    w.show()
    sys.exit(app.exec())