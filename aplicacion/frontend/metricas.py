# aplicacion/frontend/metricas.py
from __future__ import annotations
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QPushButton,
    QProgressBar, QTabWidget, QTextEdit, QSplitter, QScrollArea
)
from datetime import date, datetime, timedelta
import calendar

# Importar el controller
from aplicacion.backend.metricas.ganancias import controller

# ====== Paleta y estilos mejorados ======
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

QComboBox.Selector {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 6px 10px;
    font-weight: 500;
    color: {TEXT_DARK};
    min-width: 120px;
}}

QTableWidget#MetricsTable {{
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
"""

class MetricCard(QFrame):
    """Tarjeta de métrica personalizada"""
    
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

class MetricasTab(QWidget):
    """Vista principal de métricas mejorada"""
    
    data_updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Root")
        self.setStyleSheet(QSS)
        
        # Variables de estado
        self.is_loading = False
        self.last_update = None
        
        self.init_ui()
        self.setup_connections()
        self.load_initial_data()
        
        # Timer para actualizaciones automáticas
        #self.auto_timer = QTimer()
        #self.auto_timer.timeout.connect(self.refresh_today_metrics)
        #self.auto_timer.start(60000)  # Cada minuto / esto se comento para que la tabla no se ejecute cada minuto busquedas ansiosas
    
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
        
        # Panel inferior: tabs con detalles
        details_panel = self.create_details_panel()
        splitter.addWidget(details_panel)
        
        splitter.setSizes([400, 300])
        main_layout.addWidget(splitter)
    
    def create_header(self):
        """Crear header con título y controles"""
        header = QFrame()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        title = QLabel("Métricas de Ganancias")
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
        self.refresh_btn = QPushButton("Actualizar")
        self.refresh_btn.setObjectName("ActionBtn")
        self.refresh_btn.setProperty("class", "ActionBtn")
        layout.addWidget(self.refresh_btn)
        
        # Botón registrar hoy
        self.register_btn = QPushButton("Registrar Hoy")
        self.register_btn.setObjectName("ActionBtn")
        self.register_btn.setProperty("class", "ActionBtn success")
        layout.addWidget(self.register_btn)
        
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
        title = QLabel("MÉTRICAS DE HOY")
        title.setObjectName("Section")
        title.setProperty("class", "Section")
        layout.addWidget(title)
        
        # Grid de tarjetas
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # Ganancia Simple (solo productos)
        self.today_simple_card = MetricCard(
            "GANANCIA SIMPLE", 
            "$0", 
            "Solo productos vendidos"
        )
        cards_layout.addWidget(self.today_simple_card)
        
        # Ganancia Completa (con costos)
        self.today_complete_card = MetricCard(
            "GANANCIA COMPLETA", 
            "$0", 
            "Con costos e impuestos"
        )
        cards_layout.addWidget(self.today_complete_card)
        
        # Eficiencia
        self.today_efficiency_card = MetricCard(
            "EFICIENCIA", 
            "0%", 
            "Neta / Bruta"
        )
        cards_layout.addWidget(self.today_efficiency_card)
        
        # Comparación vs ayer
        self.today_comparison_card = MetricCard(
            "VS AYER", 
            "N/A", 
            "Tendencia diaria"
        )
        cards_layout.addWidget(self.today_comparison_card)
        
        layout.addLayout(cards_layout)
        
        return section
    
    def create_period_section(self):
        """Crear sección de métricas por período"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setSpacing(12)
        
        # Título
        title = QLabel("MÉTRICAS POR PERÍODO")
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
        
        # Año actual
        self.year_card = MetricCard(
            "ESTE AÑO", 
            "$0", 
            str(date.today().year)
        )
        periods_layout.addWidget(self.year_card)
        
        layout.addLayout(periods_layout)
        
        return section
    
    def create_details_panel(self):
        """Crear panel de detalles con tabs"""
        tabs = QTabWidget()
        
        # Tab 1: Tabla mensual
        monthly_tab = self.create_monthly_tab()
        tabs.addTab(monthly_tab, "Vista Mensual")
        
        # Tab 2: Log de actividad
        log_tab = self.create_log_tab()
        tabs.addTab(log_tab, "Log de Actividad")
        
        return tabs
    
    def create_monthly_tab(self):
        """Crear tab de vista mensual"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Selectores de fecha
        controls = QHBoxLayout()
        
        controls.addWidget(QLabel("Mes:"))
        self.month_combo = QComboBox()
        self.month_combo.setObjectName("Selector")
        self.month_combo.setProperty("class", "Selector")
        self.month_combo.addItems([
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        self.month_combo.setCurrentIndex(date.today().month - 1)
        controls.addWidget(self.month_combo)
        
        controls.addWidget(QLabel("Año:"))
        self.year_combo = QComboBox()
        self.year_combo.setObjectName("Selector")
        self.year_combo.setProperty("class", "Selector")
        for year in range(2020, 2031):
            self.year_combo.addItem(str(year))
        self.year_combo.setCurrentText(str(date.today().year))
        controls.addWidget(self.year_combo)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # Tabla
        self.monthly_table = QTableWidget()
        self.monthly_table.setObjectName("MetricsTable")
        self.monthly_table.setProperty("class", "MetricsTable")
        self.monthly_table.setColumnCount(6)
        self.monthly_table.setHorizontalHeaderLabels([
            "Día", "Ganancia Neta", "Ganancia Bruta", "Eficiencia", "Estado", "Ventas"
        ])
        
        header = self.monthly_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        layout.addWidget(self.monthly_table)
        
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
        self.log_area.setMaximumHeight(200)
        layout.addWidget(self.log_area)
        
        return tab
    
    def setup_connections(self):
        """Configurar conexiones de eventos"""
        self.refresh_btn.clicked.connect(self.refresh_all_data)
        self.register_btn.clicked.connect(self.register_today_earnings)
        self.month_combo.currentIndexChanged.connect(self.refresh_monthly_table)
        self.year_combo.currentIndexChanged.connect(self.refresh_monthly_table)
    
    def log_message(self, message: str, level: str = "INFO"):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}"
        self.log_area.append(formatted_msg)
        
        # Auto-scroll al final
        cursor = self.log_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_area.setTextCursor(cursor)
    
    def check_daily_auto_register(self):
        """Verificar si es hora de registrar automáticamente (23:59)"""
        now = datetime.now()
        current_date = now.date()
        
        # Verificar si son las 23:59
        if now.hour == 23 and now.minute == 59:
            # Verificar que no hayamos registrado ya hoy
            if self.last_auto_register_date != current_date:
                self.auto_register_today()
                self.last_auto_register_date = current_date
    
    def auto_register_today(self):
        """Registrar automáticamente las ganancias del día"""
        try:
            self.log_message("Iniciando registro automático diario...", "INFO")
            
            # Verificar si hay ventas para hoy
            calc_result = controller.calcular_ganancias_hoy_controller()
            
            if not calc_result["success"]:
                self.log_message(f"Error calculando ganancias para auto-registro: {calc_result['message']}", "ERROR")
                return
            
            data = calc_result["data"]
            
            if data["cantidad_ventas"] == 0:
                self.log_message("No hay ventas hoy. Auto-registro omitido.", "INFO")
                return
            
            # Registrar las ganancias (sobrescribir si ya existe)
            register_result = controller.registrar_ganancias_hoy_controller(sobrescribir=True)
            
            if register_result["success"]:
                reg_data = register_result["data"]
                self.log_message(
                    f"AUTO-REGISTRO EXITOSO: {reg_data['fecha']} - "
                    f"Neta: ${reg_data['ganancia_neta']:,.2f}, "
                    f"Bruta: ${reg_data['ganancia_bruta']:,.2f}",
                    "INFO"
                )
                
                # Actualizar métricas después del registro
                self.refresh_period_metrics()
                self.refresh_monthly_table()
                
            else:
                self.log_message(f"Error en auto-registro: {register_result['message']}", "ERROR")
                
        except Exception as e:
            self.log_message(f"Error crítico en auto-registro: {str(e)}", "ERROR")
    
    def manual_register_missing_days(self):
        """Registrar manualmente días faltantes (para recuperación)"""
        try:
            self.log_message("Verificando días con ventas sin registrar...", "INFO")
            
            # Verificar últimos 30 días
            today = date.today()
            
            missing_days = []
            for i in range(30):
                check_date = today - timedelta(days=i)
                fecha_str = check_date.isoformat()
                
                # Verificar si ya está registrado
                consulta_result = controller.consultar_ganancia_fecha_controller(fecha_str)
                
                if not consulta_result["success"]:
                    # No está registrado, verificar si hay ventas
                    calc_result = controller.calcular_ganancias_fecha_controller(fecha_str)
                    
                    if calc_result["success"] and calc_result["data"]["cantidad_ventas"] > 0:
                        missing_days.append(fecha_str)
            
            if missing_days:
                self.log_message(f"Encontrados {len(missing_days)} días con ventas sin registrar", "INFO")
                
                for fecha in missing_days:
                    register_result = controller.registrar_ganancias_fecha_controller(fecha)
                    if register_result["success"]:
                        self.log_message(f"Registrado retroactivamente: {fecha}", "INFO")
                    else:
                        self.log_message(f"Error registrando {fecha}: {register_result['message']}", "ERROR")
                
                # Actualizar interfaz
                self.refresh_all_data()
            else:
                self.log_message("No hay días faltantes por registrar", "INFO")
                
        except Exception as e:
            self.log_message(f"Error en registro manual de días faltantes: {str(e)}", "ERROR")
    
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
        """Cargar datos iniciales y recuperar días faltantes"""
        self.log_message("Iniciando carga de datos...")
        
        # Ejecutar recuperación automática al inicio (en background)
        self.log_message("Verificando días faltantes al inicio...")
        self.manual_register_missing_days()
        
        # Cargar datos normalmente
        self.refresh_all_data()
    
    def refresh_all_data(self):
        """Actualizar todos los datos"""
        if self.is_loading:
            return
        
        self.set_loading(True)
        self.log_message("Actualizando todos los datos...")
        
        try:
            self.refresh_today_metrics()
            self.refresh_period_metrics()
            self.refresh_monthly_table()
            
            self.last_update = datetime.now()
            self.log_message("Datos actualizados exitosamente")
            self.data_updated.emit()
            
        except Exception as e:
            self.log_message(f"Error actualizando datos: {str(e)}", "ERROR")
            QMessageBox.warning(self, "Error", f"Error al actualizar datos:\n{str(e)}")
        
        finally:
            self.set_loading(False)
    
    def refresh_today_metrics(self):
        """Actualizar métricas de hoy"""
        try:
            # Ganancia simple
            simple_result = controller.calcular_ganancia_neta_simple_hoy_controller()
            if simple_result["success"]:
                data = simple_result["data"]
                if data["cantidad_ventas"] > 0:
                    simple_value = f"${data['ganancia_neta_simple']:,.0f}"
                    simple_subtitle = f"{data['cantidad_ventas']} ventas"
                    simple_status = "success" if data['ganancia_neta_simple'] > 0 else "warning"
                else:
                    simple_value = "$0"
                    simple_subtitle = "Sin ventas hoy"
                    simple_status = "normal"
            else:
                simple_value = "Error"
                simple_subtitle = "No disponible"
                simple_status = "error"
            
            self.today_simple_card.update_value(simple_value, simple_subtitle, simple_status)
            
            # Ganancia completa
            complete_result = controller.calcular_ganancias_hoy_controller()
            if complete_result["success"]:
                data = complete_result["data"]
                if data["cantidad_ventas"] > 0:
                    complete_value = f"${data['ganancia_neta']:,.0f}"
                    complete_subtitle = f"Bruta: ${data['ganancia_bruta']:,.0f}"
                    complete_status = "success" if data['ganancia_neta'] > 0 else "warning"
                    
                    # Calcular eficiencia
                    if data['ganancia_bruta'] > 0:
                        efficiency = (data['ganancia_neta'] / data['ganancia_bruta']) * 100
                        efficiency_value = f"{efficiency:.1f}%"
                        efficiency_status = "success" if efficiency > 50 else ("warning" if efficiency > 20 else "error")
                    else:
                        efficiency_value = "0%"
                        efficiency_status = "normal"
                else:
                    complete_value = "$0"
                    complete_subtitle = "Sin ventas hoy"
                    complete_status = "normal"
                    efficiency_value = "0%"
                    efficiency_status = "normal"
            else:
                complete_value = "Error"
                complete_subtitle = "No disponible"
                complete_status = "error"
                efficiency_value = "Error"
                efficiency_status = "error"
            
            self.today_complete_card.update_value(complete_value, complete_subtitle, complete_status)
            self.today_efficiency_card.update_value(efficiency_value, "Neta / Bruta", efficiency_status)
            
            # Comparación vs ayer
            comparison_result = controller.comparar_ganancia_hoy_vs_ayer_controller()
            if comparison_result["success"]:
                data = comparison_result["data"]
                if data is None:
                    comparison_value = "N/A"
                    comparison_subtitle = "Sin ventas hoy"
                    comparison_status = "normal"
                elif data is False:
                    comparison_value = "N/A"
                    comparison_subtitle = "Sin datos de ayer"
                    comparison_status = "normal"
                else:
                    diff = data['diferencia']
                    if diff > 0:
                        comparison_value = f"+${diff:,.0f}"
                        comparison_subtitle = f"+{data['porcentaje_cambio']:.1f}%"
                        comparison_status = "success"
                    elif diff < 0:
                        comparison_value = f"-${abs(diff):,.0f}"
                        comparison_subtitle = f"{data['porcentaje_cambio']:.1f}%"
                        comparison_status = "error"
                    else:
                        comparison_value = "$0"
                        comparison_subtitle = "Sin cambios"
                        comparison_status = "normal"
            else:
                comparison_value = "Error"
                comparison_subtitle = "No disponible"
                comparison_status = "error"
            
            self.today_comparison_card.update_value(comparison_value, comparison_subtitle, comparison_status)
            
        except Exception as e:
            self.log_message(f"Error actualizando métricas de hoy: {str(e)}", "ERROR")
    
    def refresh_period_metrics(self):
        """Actualizar métricas por período"""
        try:
            # Semana
            week_result = controller.listar_ganancias_semana_controller()
            if week_result["success"] and week_result["data"]["ganancias"]:
                week_total = week_result["data"]["resumen"]["total_neta"]
                week_days = week_result["data"]["resumen"]["cantidad_dias"]
                self.week_card.update_value(
                    f"${week_total:,.0f}",
                    f"{week_days} días registrados",
                    "success" if week_total > 0 else "normal"
                )
            else:
                self.week_card.update_value("$0", "Sin registros", "normal")
            
            # Mes actual
            month_result = controller.obtener_resumen_mes_actual_controller()
            if month_result["success"] and month_result["data"]["ganancias"]:
                month_total = month_result["data"]["resumen"]["total_neta"]
                month_days = month_result["data"]["resumen"]["cantidad_dias"]
                month_avg = month_result["data"]["resumen"]["promedio_neta"]
                self.month_card.update_value(
                    f"${month_total:,.0f}",
                    f"Promedio: ${month_avg:,.0f}/día",
                    "success" if month_total > 0 else "normal"
                )
            else:
                self.month_card.update_value("$0", "Sin registros", "normal")
            
            # Año actual
            year = date.today().year
            year_result = controller.listar_ganancias_rango_controller(
                f"{year}-01-01", f"{year}-12-31"
            )
            if year_result["success"] and year_result["data"]["ganancias"]:
                year_total = year_result["data"]["resumen"]["total_neta"]
                year_days = year_result["data"]["resumen"]["cantidad_dias"]
                self.year_card.update_value(
                    f"${year_total:,.0f}",
                    f"{year_days} días registrados",
                    "success" if year_total > 0 else "normal"
                )
            else:
                self.year_card.update_value("$0", "Sin registros", "normal")
                
        except Exception as e:
            self.log_message(f"Error actualizando métricas de período: {str(e)}", "ERROR")
    
    def refresh_monthly_table(self):
        """Actualizar tabla mensual con datos calculados en tiempo real"""
        try:
            month = self.month_combo.currentIndex() + 1
            year = int(self.year_combo.currentText())
            
            # Primero intentar obtener datos registrados
            month_result = controller.listar_ganancias_mes_controller(year, month)
            
            # Crear diccionario de ganancias registradas por día
            registered_data = {}
            if month_result["success"] and month_result["data"]["ganancias"]:
                for ganancia in month_result["data"]["ganancias"]:
                    fecha_obj = datetime.strptime(ganancia["fecha"], "%Y-%m-%d").date()
                    day = fecha_obj.day
                    registered_data[day] = ganancia
            
            # Determinar días del mes
            days_in_month = calendar.monthrange(year, month)[1]
            
            # Llenar tabla
            self.monthly_table.setRowCount(days_in_month)
            
            for day in range(1, days_in_month + 1):
                row = day - 1
                fecha_dia = f"{year}-{month:02d}-{day:02d}"
                
                # Día
                self.monthly_table.setItem(row, 0, QTableWidgetItem(str(day)))
                
                if day in registered_data:
                    # Datos ya registrados
                    ganancia = registered_data[day]
                    neta = ganancia["ganancia_neta"]
                    bruta = ganancia["ganancia_bruta"]
                    efficiency = (neta / bruta * 100) if bruta > 0 else 0
                    
                    self.monthly_table.setItem(row, 1, QTableWidgetItem(f"${neta:,.0f}"))
                    self.monthly_table.setItem(row, 2, QTableWidgetItem(f"${bruta:,.0f}"))
                    self.monthly_table.setItem(row, 3, QTableWidgetItem(f"{efficiency:.1f}%"))
                    self.monthly_table.setItem(row, 4, QTableWidgetItem("✅ Registrado"))
                    self.monthly_table.setItem(row, 5, QTableWidgetItem("N/A"))
                else:
                    # Calcular datos en tiempo real para ver si hay ventas
                    calc_result = controller.calcular_ganancias_fecha_controller(fecha_dia)
                    
                    if calc_result["success"] and calc_result["data"]["cantidad_ventas"] > 0:
                        # Hay ventas pero no está registrado
                        data = calc_result["data"]
                        neta = data["ganancia_neta"]
                        bruta = data["ganancia_bruta"]
                        ventas = data["cantidad_ventas"]
                        efficiency = (neta / bruta * 100) if bruta > 0 else 0
                        
                        self.monthly_table.setItem(row, 1, QTableWidgetItem(f"${neta:,.0f}"))
                        self.monthly_table.setItem(row, 2, QTableWidgetItem(f"${bruta:,.0f}"))
                        self.monthly_table.setItem(row, 3, QTableWidgetItem(f"{efficiency:.1f}%"))
                        self.monthly_table.setItem(row, 4, QTableWidgetItem("⚠️ Calculado"))
                        self.monthly_table.setItem(row, 5, QTableWidgetItem(str(ventas)))
                    else:
                        # Sin ventas
                        self.monthly_table.setItem(row, 1, QTableWidgetItem("$0"))
                        self.monthly_table.setItem(row, 2, QTableWidgetItem("$0"))
                        self.monthly_table.setItem(row, 3, QTableWidgetItem("0%"))
                        self.monthly_table.setItem(row, 4, QTableWidgetItem("Sin ventas"))
                        self.monthly_table.setItem(row, 5, QTableWidgetItem("0"))
            
            registered_count = len(registered_data)
            self.log_message(f"Tabla actualizada para {month:02d}/{year} - {registered_count} días registrados")
            
        except Exception as e:
            self.log_message(f"Error actualizando tabla mensual: {str(e)}", "ERROR")
    
    def register_today_earnings(self):
        """Registrar ganancias de hoy"""
        try:
            # Primero calcular para mostrar preview
            calc_result = controller.calcular_ganancias_hoy_controller()
            
            if not calc_result["success"]:
                QMessageBox.warning(self, "Error", f"Error al calcular ganancias:\n{calc_result['message']}")
                return
            
            data = calc_result["data"]
            
            if data["cantidad_ventas"] == 0:
                QMessageBox.information(self, "Sin ventas", "No hay ventas registradas para hoy.")
                return
            
            # Mostrar confirmación
            msg = f"""¿Registrar las ganancias de hoy?

Ganancia Bruta: ${data['ganancia_bruta']:,.2f}
Ganancia Neta: ${data['ganancia_neta']:,.2f}
Basado en {data['cantidad_ventas']} ventas

{('⚠️ Ya existe un registro para hoy. Se sobrescribirá.' if data['ya_calculado'] else '')}"""
            
            reply = QMessageBox.question(
                self, "Confirmar Registro", msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Registrar
                register_result = controller.registrar_ganancias_hoy_controller(
                    sobrescribir=data['ya_calculado']
                )
                
                if register_result["success"]:
                    reg_data = register_result["data"]
                    self.log_message(f"Ganancias {reg_data['accion']} para hoy: ${reg_data['ganancia_neta']:,.2f}")
                    QMessageBox.information(
                        self, "Éxito", 
                        f"Ganancias {reg_data['accion']} exitosamente!\nGanancia neta: ${reg_data['ganancia_neta']:,.2f}"
                    )
                    self.refresh_all_data()
                else:
                    QMessageBox.warning(self, "Error", f"Error al registrar:\n{register_result['message']}")
                    
        except Exception as e:
            self.log_message(f"Error registrando ganancias: {str(e)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Error inesperado:\n{str(e)}")

# ===== Main Demo =====
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = MetricasTab()
    w.resize(1400, 900)
    w.show()
    sys.exit(app.exec())