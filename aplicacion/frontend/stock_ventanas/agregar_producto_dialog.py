# stock_ventanas/agregar_producto_dialog.py
from __future__ import annotations

from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIntValidator, QDoubleValidator, QValidator
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QFrame, QStackedWidget, QRadioButton, QButtonGroup, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QSpinBox,
    QProgressBar, QProgressDialog, QApplication
)

import random
import time
import calendar
import uuid
import re
from datetime import datetime

# Imports para integración con backend
from aplicacion.backend.stock import controller
from aplicacion.backend.stock.utils import fecha_actual_iso, generar_codigo_barras


# ===== WIDGET DE AUTO-FORMATO DE FECHA =====
class DateValidator(QValidator):
    """Validador personalizado para fechas"""
    
    def validate(self, input_str, pos):
        # Permitir texto vacío
        if not input_str:
            return QValidator.State.Acceptable, input_str, pos
            
        # Permitir números y separadores comunes
        if re.match(r'^[\d\-/\s]*$', input_str):
            return QValidator.State.Acceptable, input_str, pos
        
        return QValidator.State.Invalid, input_str, pos


class AutoFormatDateEdit(QLineEdit):
    """QLineEdit que auto-formatea fechas en tiempo real"""
    
    dateFormatted = pyqtSignal(str)  # Señal cuando se formatea una fecha válida
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setPlaceholderText("20250215, 15/02/2025, 2025-02-15")
        self.setValidator(DateValidator())
        
        # Conectar señales
        self.textChanged.connect(self._on_text_changed)
        self.editingFinished.connect(self._on_editing_finished)
        
        # Estado interno
        self._is_formatting = False
        self._last_valid_date = ""
        
        self.setStyleSheet("""
            QLineEdit {
                background:#ffffff; color:#111;
                border:1px solid #dcdcdc; border-radius:6px; padding:4px;
                font-family: monospace;
            }
            QLineEdit:focus { border-color:#21AFBD; }
        """)
        
        # Tooltip con ejemplos
        self.setToolTip(
            "Formatos aceptados:\n"
            "• 20250215 → 2025-02-15\n" 
            "• 15/02/2025 → 2025-02-15\n"
            "• 15/02/25 → 2025-02-15\n"
            "• 2025-02-15 (ya correcto)\n"
            "Se formatea automáticamente"
        )
    
    def _on_text_changed(self, text):
        """Se ejecuta mientras el usuario escribe"""
        if self._is_formatting:
            return
            
        # Solo intentar formatear si parece una fecha completa
        cleaned = re.sub(r'[^\d]', '', text)
        
        # Auto-formatear YYYYMMDD mientras escribe
        if len(cleaned) == 8 and cleaned.isdigit():
            formatted = self._format_yyyymmdd(cleaned)
            if formatted:
                self._set_formatted_text(formatted)
                return
        
        # Actualizar estilo según validez
        self._update_style()
    
    def _on_editing_finished(self):
        """Se ejecuta al salir del campo (Tab, Enter, click fuera)"""
        if self._is_formatting:
            return
            
        text = self.text().strip()
        if not text:
            self._update_style(valid=None)
            return
        
        # Intentar formatear cualquier entrada
        formatted = self._parse_and_format(text)
        if formatted:
            self._set_formatted_text(formatted)
        else:
            self._update_style(valid=False)
    
    def _set_formatted_text(self, formatted_text):
        """Establece texto formateado sin disparar eventos"""
        self._is_formatting = True
        cursor_pos = self.cursorPosition()
        
        self.setText(formatted_text)
        self._last_valid_date = formatted_text
        
        # Restaurar cursor al final
        self.setCursorPosition(len(formatted_text))
        
        self._update_style(valid=True)
        self.dateFormatted.emit(formatted_text)
        self._is_formatting = False
    
    def _format_yyyymmdd(self, digits):
        """Formatea YYYYMMDD específicamente"""
        if len(digits) != 8:
            return None
            
        year = digits[:4]
        month = digits[4:6] 
        day = digits[6:8]
        
        formatted = f"{year}-{month}-{day}"
        return formatted if self._validate_date(formatted) else None
    
    def _parse_and_format(self, text):
        """Intenta parsear y formatear diferentes formatos"""
        # Limpiar texto
        text = text.strip()
        
        # Si ya está en formato correcto
        if re.match(r'^\d{4}-\d{2}-\d{2}$', text):
            return text if self._validate_date(text) else None
        
        # Remover espacios y caracteres especiales, mantener números y separadores
        cleaned = re.sub(r'[^\d/-]', '', text)
        
        patterns = [
            # YYYYMMDD
            (r'^(\d{4})(\d{2})(\d{2})$', lambda m: f"{m.group(1)}-{m.group(2)}-{m.group(3)}"),
            
            # DD/MM/YYYY o DD/MM/YY
            (r'^(\d{1,2})/(\d{1,2})/(\d{2,4})$', self._format_dmy),
            
            # MM/DD/YYYY (formato americano) - menos común, evaluar último
            (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', self._format_mdy_if_ambiguous),
            
            # YYYY-MM-DD con números de 1 dígito
            (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', lambda m: f"{m.group(1)}-{m.group(2):0>2}-{m.group(3):0>2}"),
            
            # YYYY/MM/DD
            (r'^(\d{4})/(\d{1,2})/(\d{1,2})$', lambda m: f"{m.group(1)}-{m.group(2):0>2}-{m.group(3):0>2}"),
        ]
        
        for pattern, formatter in patterns:
            match = re.match(pattern, cleaned)
            if match:
                try:
                    result = formatter(match)
                    if result and self._validate_date(result):
                        return result
                except:
                    continue
        
        return None
    
    def _format_dmy(self, match):
        """Formatea DD/MM/YYYY o DD/MM/YY"""
        day = int(match.group(1))
        month = int(match.group(2))
        year_str = match.group(3)
        
        # Manejar años de 2 dígitos
        if len(year_str) == 2:
            year = int(year_str)
            # Asumir que 00-30 = 2000-2030, 31-99 = 1931-1999
            if year <= 30:
                year += 2000
            else:
                year += 1900
        else:
            year = int(year_str)
        
        return f"{year:04d}-{month:02d}-{day:02d}"
    
    def _format_mdy_if_ambiguous(self, match):
        """Formatea MM/DD/YYYY solo si no es ambiguo"""
        month = int(match.group(1))
        day = int(match.group(2))
        year = int(match.group(3))
        
        # Si month > 12, claramente es DD/MM/YYYY
        if month > 12:
            return f"{year:04d}-{day:02d}-{month:02d}"
        
        # Si day > 12, claramente es MM/DD/YYYY  
        if day > 12:
            return f"{year:04d}-{month:02d}-{day:02d}"
        
        # Ambiguo: preferir DD/MM/YYYY (formato más común internacionalmente)
        return f"{year:04d}-{day:02d}-{month:02d}"
    
    def _validate_date(self, date_str):
        """Valida que la fecha sea real"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def _update_style(self, valid=None):
        """Actualiza el estilo según validez"""
        if valid is None:  # Campo vacío
            border_color = "#dcdcdc"
            bg_color = "#ffffff"
        elif valid:  # Fecha válida
            border_color = "#22C55E"
            bg_color = "#f0fff0"
        else:  # Fecha inválida
            border_color = "#EF4444"
            bg_color = "#fff5f5"
        
        self.setStyleSheet(f"""
            QLineEdit {{
                background:{bg_color}; color:#111;
                border:1px solid {border_color}; border-radius:6px; padding:4px;
                font-family: monospace;
            }}
            QLineEdit:focus {{ border-color:{border_color}; }}
        """)
    
    def date_iso(self):
        """Retorna la fecha en formato ISO o cadena vacía"""
        text = self.text().strip()
        if text and self._validate_date(text):
            return text
        return ""
    
    def set_date_iso(self, date_iso):
        """Establece una fecha en formato ISO"""
        if date_iso and self._validate_date(date_iso):
            self._set_formatted_text(date_iso)
        else:
            self.clear()
    
    def keyPressEvent(self, event):
        """Manejo especial de teclas"""
        # Permitir Ctrl+A para seleccionar todo
        if event.key() == Qt.Key.Key_A and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.selectAll()
            return
        
        # Tab para auto-formatear inmediatamente
        if event.key() == Qt.Key.Key_Tab:
            self._on_editing_finished()
        
        super().keyPressEvent(event)


# ===== THREAD PARA GENERACIÓN DE CÓDIGOS =====
class CodigoGeneratorThread(QThread):
    """Thread para generar códigos de barras en background"""
    progress = pyqtSignal(int)  # progreso
    finished_batch = pyqtSignal(list)  # batch de códigos generados
    
    def __init__(self, cantidad, batch_size=100):
        super().__init__()
        self.cantidad = cantidad
        self.batch_size = batch_size
        self.codigos = []
        
    def run(self):
        """Genera códigos en batches para no bloquear UI"""
        for i in range(0, self.cantidad, self.batch_size):
            batch = []
            end_idx = min(i + self.batch_size, self.cantidad)
            
            for j in range(i, end_idx):
                # Usar la función del backend para generar códigos únicos
                codigo = generar_codigo_barras()  # Cada llamada genera un código único
                batch.append(codigo)
            
            self.finished_batch.emit(batch)
            self.progress.emit(end_idx)
            
            # Pequeña pausa para no saturar
            self.msleep(1)


# ===== TABLA OPTIMIZADA =====
class OptimizedTableWidget(QTableWidget):
    """Tabla optimizada con paginación virtual"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_cache = []  # Cache de datos
        self.page_size = 100  # Mostrar solo 100 filas a la vez
        self.current_page = 0
        self.total_items = 0
        
    def set_data(self, data_list):
        """Establece los datos sin crear todos los widgets"""
        self.data_cache = data_list
        self.total_items = len(data_list)
        self.load_current_page()
        
    def load_current_page(self):
        """Carga solo la página actual"""
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, self.total_items)
        
        # Limpiar tabla actual
        self.setRowCount(0)
        
        # Cargar solo items visibles
        for i in range(start_idx, end_idx):
            if i < len(self.data_cache):
                self.add_row_optimized(self.data_cache[i], i)
    
    def add_row_optimized(self, data, global_idx):
        """Agrega una fila de forma optimizada con auto-formato de fecha"""
        r = self.rowCount()
        self.insertRow(r)
        
        # Código de barras
        code_item = QTableWidgetItem(data.get('codigo', ''))
        code_item.setData(Qt.ItemDataRole.UserRole, global_idx)  # Guardar índice global
        code_item.setFlags(code_item.flags() | Qt.ItemFlag.ItemIsEditable)
        self.setItem(r, 0, code_item)
        
        # Widget de fecha con auto-formato
        fecha_edit = AutoFormatDateEdit()
        if data.get('fecha'):
            fecha_edit.set_date_iso(data['fecha'])
        
        self.setCellWidget(r, 1, fecha_edit)


# ===== DIÁLOGO PRINCIPAL OPTIMIZADO =====
class AgregarProductoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AGREGAR PRODUCTO")
        self.setModal(True)
        self.setMinimumSize(720, 560)

        self.datos_producto: dict | None = None
        self.unidades_temp: list[dict] = []
        self._autogenerar_cb = True
        self.codigo_thread = None
        self.codigos_generados = []

        self._build_ui()

    # ===========================
    # UI
    # ===========================
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("AGREGAR PRODUCTO")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #22C55E;")
        root.addWidget(title)

        frame = QFrame()
        frame.setObjectName("panel")
        frame.setStyleSheet("""
            QFrame#panel {
                background:#3f3f3f; border:2px solid #5a5a5a; border-radius:10px;
            }
        """)
        root.addWidget(frame, 1)

        frame_l = QVBoxLayout(frame)
        frame_l.setContentsMargins(18, 18, 18, 18)
        frame_l.setSpacing(12)

        self.stack = QStackedWidget()
        frame_l.addWidget(self.stack, 1)

        self.footer = QHBoxLayout()
        self.footer.addStretch()

        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setFixedHeight(44)
        self.btn_cancelar.setStyleSheet("QPushButton{background:#EF4444;color:white;border:none;border-radius:22px;padding:0 24px;font-weight:bold;} QPushButton:hover{background:#DC2626;}")
        # Cambiar la conexión para que también muestre confirmación
        self.btn_cancelar.clicked.connect(self._confirmar_cancelar)

        self.btn_guardar = QPushButton("GUARDAR")
        self.btn_guardar.setFixedHeight(44)
        self.btn_guardar.setStyleSheet("QPushButton{background:#22C55E;color:white;border:none;border-radius:22px;padding:0 24px;font-weight:bold;} QPushButton:hover{background:#16A34A;}")

        self.footer.addWidget(self.btn_cancelar)
        self.footer.addWidget(self.btn_guardar)
        frame_l.addLayout(self.footer)

        self._page_formulario()
        self._page_codigos()

        self.btn_guardar.clicked.connect(self._on_guardar_clicked)
        self._set_footer_mode(step=1)

    def _confirmar_cancelar(self):
        """Muestra confirmación antes de cancelar"""
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Icon.Question)
        reply.setWindowTitle("Confirmar cancelación")
        
        # Mensaje diferente según el paso
        if self.stack.currentIndex() == 0:
            reply.setText("¿Estás seguro que querés cancelar el nuevo producto?")
            reply.setInformativeText("Se perderán todos los datos ingresados.")
        else:
            reply.setText("¿Estás seguro que querés cancelar?")
            reply.setInformativeText("Se perderán todos los datos del producto y códigos generados.")
        
        # Aplicar estilo claro al mensaje de confirmación
        reply.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        reply.setStyleSheet("""
            QMessageBox { 
                background: #ffffff; 
            }
            QMessageBox QLabel { 
                color: #111111; 
                font-size: 12pt;
            }
            QMessageBox QFrame { 
                background: #ffffff; 
                border: 1px solid #dcdcdc; 
            }
            QMessageBox QPushButton {
                color: #111111;
                background: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 80px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover { 
                background: #e9e9e9; 
            }
            QMessageBox QPushButton:pressed { 
                background: #d9d9d9; 
            }
        """)
        
        # Configurar botones personalizados
        si_button = reply.addButton("Sí, cancelar", QMessageBox.ButtonRole.YesRole)
        no_button = reply.addButton("No, continuar", QMessageBox.ButtonRole.NoRole)
        
        # Establecer el botón "No" como predeterminado (más seguro)
        reply.setDefaultButton(no_button)
        
        # Ejecutar el diálogo y verificar la respuesta
        reply.exec()
        
        if reply.clickedButton() == si_button:
            # Usuario confirmó la cancelación
            print("🚪 Usuario canceló la creación del producto")
            self.reject()  # Cerrar diálogo
        else:
            # Usuario decidió continuar
            print("📝 Usuario continúa con el producto")

    # ---------- Página 1: formulario ----------
    def _page_formulario(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)

        box = QFrame()
        box.setObjectName("box1")
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setStyleSheet("""
            QFrame#box1 { background: white; border-radius: 14px; }

            /* Todas las labels del formulario se ven SIEMPRE claras */
            #box1 QLabel[role="formLabel"] {
                color: #111;
                background: #E9E9E9;
                border-radius: 8px;
                padding: 6px 10px;
            }

            #box1 QLabel { color: #111; }

            #box1 QLineEdit, #box1 QComboBox, #box1 QSpinBox {
                background: #ffffff; color: #111;
                border:2px solid #d6d6d6; border-radius:8px; padding:6px;
            }
            #box1 QLineEdit:focus, #box1 QComboBox:focus, #box1 QSpinBox:focus {
                border-color:#21AFBD;
            }
            #box1 QRadioButton { color:#111; }
        """)
        lay.addWidget(box, 1)

        gl = QVBoxLayout(box)
        gl.setContentsMargins(22, 22, 22, 22)
        gl.setSpacing(12)

        # Nombre
        gl.addLayout(self._row_label_input("Nombre:", 'nombre', width=420))

        # Costo
        self.edit_costo = QLineEdit()
        self.edit_costo.setPlaceholderText("0.00")
        self.edit_costo.setValidator(QDoubleValidator(0.0, 1e12, 2))
        gl.addLayout(self._row_custom("COSTO:", self.edit_costo, w=140))

        # Cantidad - OPTIMIZACIÓN: Límite máximo con advertencia
        self.edit_cantidad = QSpinBox()
        self.edit_cantidad.setRange(0, 5000)
        self.edit_cantidad.setSpecialValueText(" ")
        gl.addLayout(self._row_custom("CANTIDAD:", self.edit_cantidad, w=140, hint="en unidades o kilos según corresponda"))

        # Categoría - cargar desde base de datos
        self.combo_categoria = QComboBox()
        try:
            categorias = controller.listar_clasificaciones_controller()
            self.combo_categoria.addItem("sin categoría", None)
            for cat in categorias:
                self.combo_categoria.addItem(cat.nombre, cat.id)
        except Exception as e:
            self.combo_categoria.addItem("sin categoría", None)
            print(f"Error cargando categorías: {e}")
        gl.addLayout(self._row_custom("Categoria:", self.combo_categoria, w=220))

        # Tipo de unidad
        self.combo_unidad = QComboBox()
        self.combo_unidad.addItems(["unidades", "kilogramos"])
        gl.addLayout(self._row_custom("Tipo de unidad:", self.combo_unidad, w=220))

        # Margen / Precio directo
        self.radio_margen = QRadioButton()
        self.radio_precio = QRadioButton()
        self.radio_margen.setChecked(True)

        self.group_precio = QButtonGroup(self)
        self.group_precio.addButton(self.radio_margen)
        self.group_precio.addButton(self.radio_precio)

        self.edit_margen = QLineEdit()
        self.edit_margen.setPlaceholderText("10  (porcentaje)")
        self.edit_margen.setValidator(QDoubleValidator(0.0, 1000.0, 2))
        self.edit_margen.setFixedWidth(100)

        self.edit_precio_venta = QLineEdit()
        self.edit_precio_venta.setPlaceholderText("0.00")
        self.edit_precio_venta.setValidator(QDoubleValidator(0.0, 1e12, 2))
        self.edit_precio_venta.setEnabled(False)
        self.edit_precio_venta.setFixedWidth(140)

        # fila margen
        fila_m = QHBoxLayout()
        fila_m.setSpacing(8)

        lbl_m = QLabel("Margen de ganancia:")
        lbl_m.setProperty("role", "formLabel")
        fila_m.addWidget(lbl_m)

        fila_m.addWidget(self.radio_margen)

        # ⬅️ el input va donde estaba el pill
        fila_m.addWidget(self.edit_margen)

        fila_m.addSpacing(6)

        # ➡️ el pill "10%" pasa a la derecha del input (como marcaste en verde)
        pill = QLabel("Ingrese porcentaje ejemp: 10%")
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setStyleSheet("""
            color: #777; 
            background: #f0f0f0; 
            padding: 4px 8px; 
            border-radius: 6px;
        """)
        fila_m.addWidget(pill)

        # empuja todo hacia la izquierda
        fila_m.addStretch()

        gl.addLayout(fila_m)



        # fila precio directo
        fila_p = QHBoxLayout()
        fila_p.setSpacing(8)
        lbl_p = QLabel("Precio de venta:")
        lbl_p.setProperty("role", "formLabel")
        fila_p.addWidget(lbl_p)
        fila_p.addWidget(self.radio_precio)
        fila_p.addWidget(self.edit_precio_venta)
        fila_p.addStretch()
        gl.addLayout(fila_p)

        self.radio_margen.toggled.connect(self._toggle_margen_precio)

        # Proveedor - cargar desde base de datos  
        self.combo_proveedor = QComboBox()
        try:
            proveedores = controller.listar_proveedores_controller()
            self.combo_proveedor.addItem("sin proveedor", None)
            for prov in proveedores:
                self.combo_proveedor.addItem(prov.nombre, prov.id)
        except Exception as e:
            self.combo_proveedor.addItem("sin proveedor", None)
            print(f"Error cargando proveedores: {e}")
        gl.addLayout(self._row_custom("Proveedor", self.combo_proveedor, w=240))

        # Auto generar códigos de barras (SI/NO)
        caja_auto = QFrame()
        caja_auto.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        caja_auto.setStyleSheet("QFrame{background:#F5F5F5;border:2px solid #dcdcdc;border-radius:12px;}")
        caja_l = QHBoxLayout(caja_auto)
        caja_l.setContentsMargins(12, 10, 12, 10)
        caja_l.setSpacing(16)

        mini = QVBoxLayout()
        t1 = QLabel("AUTO GENERAR\nCÓDIGO DE BARRAS")
        t1.setObjectName("autoGenTitle")
        t1.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        t1.setStyleSheet("background: transparent; font-size:11px; color:#444;")
        mini.addWidget(t1)
        mini.addStretch()
        caja_l.addLayout(mini)

        self.radio_auto_si = QRadioButton("SI")
        self.radio_auto_no = QRadioButton("NO")
        self.radio_auto_si.setChecked(True)

        bg = QButtonGroup(self)
        bg.addButton(self.radio_auto_si)
        bg.addButton(self.radio_auto_no)

        caja_l.addStretch()
        caja_l.addWidget(self.radio_auto_si)
        caja_l.addWidget(self.radio_auto_no)

        gl.addWidget(caja_auto)

        self.stack.addWidget(w)

    def _row_label_input(self, label_text: str, attr_name: str, width: int = 260):
        lbl = QLabel(label_text)
        lbl.setProperty("role", "formLabel")
        edit = QLineEdit()
        edit.setFixedWidth(width)
        setattr(self, f"edit_{attr_name}", edit)

        row = QHBoxLayout()
        row.addWidget(lbl)
        row.addWidget(edit)
        row.addStretch()
        return row

    def _row_custom(self, label_text: str, widget, w: int | None = None, hint: str | None = None):
        lbl = QLabel(label_text)
        lbl.setProperty("role", "formLabel")
        if isinstance(widget, (QLineEdit, QComboBox)) and w:
            widget.setFixedWidth(w)
        row = QHBoxLayout()
        row.addWidget(lbl)
        row.addWidget(widget)
        if hint:
            tip = QLabel(hint)
            tip.setStyleSheet("color:#777; background:#f0f0f0; padding:4px 8px; border-radius:6px;")
            row.addSpacing(8)
            row.addWidget(tip)
        row.addStretch()
        return row

    def _toggle_margen_precio(self, use_margen: bool):
        self.edit_margen.setEnabled(use_margen)
        self.edit_precio_venta.setEnabled(not use_margen)

    # ---------- Página 2: tabla de códigos OPTIMIZADA ----------
    def _page_codigos(self):
        """Página optimizada con progress bar y paginación"""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)

        box = QFrame()
        box.setObjectName("box2")
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setStyleSheet("""
            QFrame#box2 { background: white; border-radius: 14px; }

            #box2 QTableWidget {
                background:white; color:#111;
                gridline-color:#e0e0e0;
                selection-background-color:#E3F2FD; selection-color:#111;
                border:1px solid #dcdcdc; border-radius:8px;
            }
            #box2 QHeaderView::section { background:#e7eefc; font-weight:bold; color:#111; }

            #box2 QProgressBar {
                border: 1px solid #dcdcdc;
                border-radius: 6px;
                text-align: center;
                background: #f0f0f0;
            }
            #box2 QProgressBar::chunk {
                background: #22C55E;
                border-radius: 5px;
            }
        """)
        lay.addWidget(box, 1)

        gl = QVBoxLayout(box)
        gl.setContentsMargins(16, 16, 16, 16)
        gl.setSpacing(8)

        subt = QLabel("CÓDIGOS DE BARRAS DEL PRODUCTO")
        subt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subt.setStyleSheet("color:#444;font-weight:bold;")
        gl.addWidget(subt)

        # Progress bar para carga
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        gl.addWidget(self.progress_bar)

        # Info de paginación
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color:#666; font-size:12px;")
        gl.addWidget(self.info_label)

        # Tabla optimizada
        self.table = OptimizedTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Código de barras", "Vencimiento (opcional)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        gl.addWidget(self.table, 1)

        # Controles de paginación
        pagination = QHBoxLayout()
        self.btn_prev_page = QPushButton("← Anterior")
        self.btn_next_page = QPushButton("Siguiente →")
        self.btn_prev_page.clicked.connect(self._prev_page)
        self.btn_next_page.clicked.connect(self._next_page)
        
        pagination.addWidget(self.btn_prev_page)
        pagination.addStretch()
        self.page_info = QLabel("Página 1")
        self.page_info.setStyleSheet("color:#666; font-weight:bold;")
        pagination.addWidget(self.page_info)
        pagination.addStretch()
        pagination.addWidget(self.btn_next_page)
        gl.addLayout(pagination)

        # Botones de acción
        act = QHBoxLayout()
        self.btn_agregar_fila = QPushButton("Agregar fila")
        self.btn_quitar_fila = QPushButton("Quitar fila")
        act.addStretch()
        act.addWidget(self.btn_agregar_fila)
        act.addWidget(self.btn_quitar_fila)
        gl.addLayout(act)

        self.btn_agregar_fila.clicked.connect(self._add_table_row)
        self.btn_quitar_fila.clicked.connect(self._remove_table_row)

        self.stack.addWidget(w)

    # ===========================
    # Lógica OPTIMIZADA
    # ===========================
    def _set_footer_mode(self, step: int):
        self.btn_guardar.setText("GUARDAR" if step == 1 else "CONFIRMAR")

    def _on_guardar_clicked(self):
        if self.stack.currentIndex() == 0:
            if not self._validar_paso1():
                return
            
            # OPTIMIZACIÓN: Validación de cantidad
            cantidad = self.edit_cantidad.value()
            if cantidad > 1000:
                reply = QMessageBox.question(
                    self, 
                    "Cantidad muy alta", 
                    f"Vas a crear {cantidad} unidades. Esto puede tomar unos segundos y afectar el rendimiento.\n"
                    f"Para cantidades muy altas considera usar productos por kilogramos.\n\n¿Continuar?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                    
            self._armar_datos_producto()
            self._preparar_paso2()
            self.stack.setCurrentIndex(1)
            self._set_footer_mode(step=2)
        else:
            if not self._recolectar_unidades():
                return
            self.accept()

    # ----- Paso 1 -----
    def _validar_paso1(self) -> bool:
        nombre = self.edit_nombre.text().strip()
        if not nombre:
            return self._warn("El nombre es obligatorio.")

        if self.edit_costo.text().strip() == "":
            return self._warn("El costo es obligatorio.")
        _ = float(self.edit_costo.text())

        cant = self.edit_cantidad.value()
        if cant <= 0:
            return self._warn("La cantidad debe ser mayor a 0.")

        if self.radio_margen.isChecked():
            if self.edit_margen.text().strip() == "":
                return self._warn("Ingresá un margen de ganancia (en %).")
        else:
            if self.edit_precio_venta.text().strip() == "":
                return self._warn("Ingresá el precio de venta.")

        return True

    def _armar_datos_producto(self):
        nombre = self.edit_nombre.text().strip()
        costo = float(self.edit_costo.text())
        cantidad = int(self.edit_cantidad.value())
        unidad = self.combo_unidad.currentText()

        if self.radio_margen.isChecked():
            margen = float(self.edit_margen.text()) / 100.0  # Convertir porcentaje a decimal
            precio_venta = None
        else:
            margen = None
            precio_venta = float(self.edit_precio_venta.text())

        # Obtener IDs reales de los ComboBox
        categoria_id = self.combo_categoria.currentData()
        proveedor_id = self.combo_proveedor.currentData()

        self._autogenerar_cb = self.radio_auto_si.isChecked()

        self.datos_producto = {
            "nombre": nombre,
            "unidad_medida": unidad,
            "cantidad": float(cantidad),  # Controller espera float
            "costo_unitario": costo,
            "usa_redondeo": True,  # Siempre True según test_stock.py
            "proveedor_id": proveedor_id,
            "categoria_id": categoria_id,
        }
        
        # Agregar margen o precio según corresponda
        if margen is not None:
            self.datos_producto["margen_ganancia"] = margen
        if precio_venta is not None:
            self.datos_producto["precio_venta"] = precio_venta
            self.datos_producto["precio_redondeado"] = precio_venta

    def _preparar_paso2(self):
        """Preparación optimizada con threading"""
        cant = int(self.datos_producto["cantidad"])
        
        self.codigos_generados = []
        
        if self._autogenerar_cb:
            self._generar_codigos_directo(cant)
        else:
            # Crear datos vacíos
            self.codigos_generados = [{"codigo": "", "fecha": ""} for _ in range(cant)]
            self._actualizar_tabla()

    def _generar_codigos_directo(self, cantidad):
        """Genera códigos directamente usando la función del backend"""
        for i in range(cantidad):
            codigo = generar_codigo_barras()  # Cada llamada genera un código único
            self.codigos_generados.append({"codigo": codigo, "fecha": ""})
        
        self._actualizar_tabla()

    def _actualizar_tabla(self):
        """Actualiza la tabla con los datos generados"""
        self.table.set_data(self.codigos_generados)
        self._update_pagination_info()

    def _update_pagination_info(self):
        """Actualiza la información de paginación"""
        total = len(self.codigos_generados)
        if total == 0:
            self.info_label.setText("Sin datos")
            self.page_info.setText("Página 0")
            self.btn_prev_page.setEnabled(False)
            self.btn_next_page.setEnabled(False)
            return
            
        start = self.table.current_page * self.table.page_size + 1
        end = min((self.table.current_page + 1) * self.table.page_size, total)
        max_page = (total - 1) // self.table.page_size + 1
        
        self.info_label.setText(f"Mostrando {start}-{end} de {total} unidades")
        self.page_info.setText(f"Página {self.table.current_page + 1} de {max_page}")
        
        self.btn_prev_page.setEnabled(self.table.current_page > 0)
        self.btn_next_page.setEnabled(end < total)

    def _prev_page(self):
        """Página anterior"""
        if self.table.current_page > 0:
            self._save_current_page_data()  # Guardar datos antes de cambiar
            self.table.current_page -= 1
            self.table.load_current_page()
            self._update_pagination_info()

    def _next_page(self):
        """Página siguiente"""
        max_page = (len(self.codigos_generados) - 1) // self.table.page_size
        if self.table.current_page < max_page:
            self._save_current_page_data()  # Guardar datos antes de cambiar
            self.table.current_page += 1
            self.table.load_current_page()
            self._update_pagination_info()

    # ----- Tabla OPTIMIZADA -----
    def _add_table_row(self):
        """Agregar fila optimizada"""
        if len(self.codigos_generados) >= 10000:
            self._warn("Límite máximo de 10,000 unidades alcanzado.")
            return
            
        # Agregar al cache
        self.codigos_generados.append({"codigo": "", "fecha": ""})
        
        # Si estamos en la última página, agregar visualmente
        total = len(self.codigos_generados)
        last_page = (total - 1) // self.table.page_size
        
        if self.table.current_page == last_page:
            self.table.add_row_optimized({"codigo": "", "fecha": ""}, total - 1)
        
        self._update_pagination_info()

    def _remove_table_row(self):
        """Quitar fila optimizada"""
        if not self.codigos_generados:
            return
            
        current_row = self.table.currentRow()
        if current_row < 0:
            return
            
        # Calcular índice global
        global_idx = self.table.current_page * self.table.page_size + current_row
        
        if global_idx < len(self.codigos_generados):
            # Remover del cache
            del self.codigos_generados[global_idx]
            
            # Recargar página actual
            self.table.load_current_page()
            self._update_pagination_info()

    def _save_current_page_data(self):
        """Guarda los datos de la página actual en el cache"""
        start_idx = self.table.current_page * self.table.page_size
        
        for row in range(self.table.rowCount()):
            global_idx = start_idx + row
            if global_idx < len(self.codigos_generados):
                
                code_item = self.table.item(row, 0)
                fecha_widget = self.table.cellWidget(row, 1)
                
                if code_item:
                    self.codigos_generados[global_idx]['codigo'] = code_item.text().strip()
                    
                # Manejar AutoFormatDateEdit
                if isinstance(fecha_widget, AutoFormatDateEdit):
                    self.codigos_generados[global_idx]['fecha'] = fecha_widget.date_iso()

    def _recolectar_unidades(self) -> bool:
        """Recolecta datos de todas las páginas - OPTIMIZADO"""
        if not self.codigos_generados:
            return self._warn("No hay datos para guardar.")
        
        # Guardar datos de la página actual
        self._save_current_page_data()
        
        # Validar todos los códigos
        unidades = []
        codigos_vistos = set()
        
        for i, data in enumerate(self.codigos_generados):
            codigo = data["codigo"].strip()
            if not codigo:
                return self._warn(f"Falta código en la unidad {i+1}.")
            
            # Verificar códigos duplicados
            if codigo in codigos_vistos:
                return self._warn(f"Código duplicado encontrado: {codigo}")
            codigos_vistos.add(codigo)
            
            fecha = data["fecha"].strip() or None
            if fecha and not self._validate_date(fecha):
                return self._warn(f"Fecha inválida en unidad {i+1}: {fecha}")
            
            unidades.append({
                "codigo_barras": codigo,
                "fecha_vencimiento": fecha
            })
        
        self.unidades_temp = unidades
        return self._guardar_con_progress()

    def _validate_date(self, date_str):
        """Valida formato de fecha YYYY-MM-DD"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _guardar_con_progress(self):
        """Guarda con progress bar para cantidades grandes - VERSIÓN MEJORADA"""
        try:
            total_unidades = len(self.unidades_temp)
            
            # Crear progress dialog para cantidades grandes
            if total_unidades > 100:
                progress = QProgressDialog("Guardando producto...", "Cancelar", 0, 100, self)
                progress.setWindowTitle("Guardando")
                progress.setModal(True)
                progress.setWindowFlags(progress.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
                progress.show()
                QApplication.processEvents()
            
            # 1. Crear producto
            if total_unidades > 100:
                progress.setLabelText("Creando producto...")
                progress.setValue(10)
                QApplication.processEvents()
                
            producto_creado = controller.agregar_producto_controller(self.datos_producto)
            print(f"Producto creado: {producto_creado.nombre} con ID {producto_creado.id}")
            
            if total_unidades > 100:
                progress.setValue(20)
                QApplication.processEvents()
                
                if progress.wasCanceled():
                    return False
            
            # 2. Crear unidades físicas si no es divisible
            if not producto_creado.es_divisible and self.unidades_temp:
                ahora = fecha_actual_iso()
                batch_size = 50  # Batches pequeños para mantener responsividad
                
                for i in range(0, len(self.unidades_temp), batch_size):
                    if total_unidades > 100:
                        if progress.wasCanceled():
                            return False
                            
                        progress_value = 20 + int((i / len(self.unidades_temp)) * 60)
                        progress.setLabelText(f"Guardando unidades... ({i+1}-{min(i+batch_size, len(self.unidades_temp))} de {len(self.unidades_temp)})")
                        progress.setValue(progress_value)
                        QApplication.processEvents()
                    
                    batch = self.unidades_temp[i:i+batch_size]
                    for unidad_data in batch:
                        controller.agregar_unidad_controller({
                            "producto_id": producto_creado.id,
                            "codigo_barras": unidad_data["codigo_barras"],
                            "estado": "activo",
                            "fecha_ingreso": ahora,
                            "fecha_modificacion": ahora,
                            "observaciones": "",
                            "fecha_vencimiento": unidad_data["fecha_vencimiento"]
                        })
                
                print(f"Se registraron {len(self.unidades_temp)} unidades físicas.")
                
            # 3. Si es divisible (kg), crear una unidad especial
            elif producto_creado.es_divisible:
                if total_unidades > 100:
                    progress.setLabelText("Creando unidad de kilogramos...")
                    progress.setValue(80)
                    QApplication.processEvents()
                    
                from aplicacion.backend.stock.utils import generar_codigo_barras_con_letras
                codigo = generar_codigo_barras_con_letras()
                ahora = fecha_actual_iso()
                controller.agregar_unidad_controller({
                    "producto_id": producto_creado.id,
                    "codigo_barras": codigo,
                    "estado": "activo",
                    "fecha_ingreso": ahora,
                    "fecha_modificacion": ahora,
                    "observaciones": "Producto a granel (kg)",
                    "fecha_vencimiento": None
                })
                print(f"Producto por kg registrado con código interno: {codigo}")
            
            # 4. Exportar JSON actualizado - SECCIÓN MEJORADA
            if total_unidades > 100:
                progress.setLabelText("Actualizando inventario...")
                progress.setValue(90)
                QApplication.processEvents()
                
            try:
                from aplicacion.backend.stock.crud import exportar_productos_json
                print("🔄 Generando JSON actualizado...")
                
                # Pequeña pausa para asegurar que la BD esté completamente actualizada
                import time
                time.sleep(0.2)
                
                json_exportado = exportar_productos_json()
                if json_exportado:
                    print("✅ JSON de stock actualizado exitosamente")
                    
                    # Verificar que el archivo realmente se escribió
                    import os
                    from pathlib import Path
                    base_dir = Path(__file__).resolve().parent.parent.parent
                    json_path = base_dir / "frontend" / "json" / "stock.json"
                    
                    if json_path.exists():
                        # MEJORA: Verificar estabilidad del archivo
                        file_size = json_path.stat().st_size
                        timestamp = os.path.getmtime(json_path)
                        time.sleep(0.1)  # Pequeña pausa
                        
                        # Verificar que el tamaño no cambió (archivo estable)
                        if json_path.stat().st_size == file_size and file_size > 0:
                            print(f"📅 JSON estable: timestamp={time.ctime(timestamp)}, size={file_size} bytes")
                            
                            # **MEJORA: TRIPLE ACTUALIZACIÓN CON DIFERENTES DELAYS**
                            print("🔄 Iniciando actualización múltiple de pantallas...")
                            
                            # Actualización inmediata
                            resultado_inmediato = self._actualizar_pantallas_relacionadas()
                            print(f"📊 Actualización inmediata: {resultado_inmediato}")
                            
                            # Actualización con delay corto (para casos rápidos)
                            QTimer.singleShot(200, lambda: self._actualizar_con_delay("corto"))
                            
                            # Actualización con delay largo (para casos lentos)
                            QTimer.singleShot(800, lambda: self._actualizar_con_delay("largo"))
                            
                        else:
                            print("⏳ Archivo JSON aún siendo escrito, esperando...")
                            time.sleep(0.3)
                            print(f"📅 JSON actualizado después de espera: size={json_path.stat().st_size} bytes")
                        
                    else:
                        print(f"❌ JSON no encontrado en {json_path}")
                        
                else:
                    print("⚠️ Advertencia: No se pudo actualizar el JSON de stock")
            except Exception as e:
                print(f"⚠️ Error al exportar JSON: {e}")
                import traceback
                traceback.print_exc()
            
            if total_unidades > 100:
                progress.setValue(100)
                progress.close()
            
            # Mostrar mensaje de éxito
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Éxito")
            msg.setText(f"Producto '{producto_creado.nombre}' guardado exitosamente.")
            msg.setInformativeText(f"Se crearon {total_unidades} unidades.")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            
            return True
            
        except Exception as e:
            if 'progress' in locals():
                progress.close()
            return self._warn(f"Error al guardar el producto: {str(e)}")

    def _actualizar_con_delay(self, tipo_delay):
        """Actualización con delay - para logging mejorado"""
        resultado = self._actualizar_pantallas_relacionadas()
        print(f"📊 Actualización con delay {tipo_delay}: {resultado}")

    # ===========================
    # SISTEMA MEJORADO DE ACTUALIZACIÓN DE PANTALLAS
    # ===========================
    def _actualizar_pantallas_relacionadas(self):
        """
        VERSIÓN MEJORADA: Actualiza las pantallas de ventas con mejor búsqueda y timing.
        """
        try:
            print("🔍 [MEJORADO] Buscando pantallas para actualizar...")
            
            # Buscar todas las instancias de VentasTab en la aplicación
            app = QApplication.instance()
            if not app:
                print("❌ No se pudo obtener la instancia de QApplication")
                return False
            
            # Buscar en todos los widgets de la aplicación
            all_widgets = app.allWidgets()
            ventas_tabs = []
            
            for widget in all_widgets:
                # Verificar si es VentasTab por nombre de clase
                if widget.__class__.__name__ == 'VentasTab':
                    ventas_tabs.append(widget)
            
            print(f"🔄 Encontrados {len(ventas_tabs)} VentasTab en la aplicación")
            
            actualizaciones_exitosas = 0
            
            for i, ventas_tab in enumerate(ventas_tabs):
                try:
                    print(f"🔄 Actualizando VentasTab #{i+1}...")
                    
                    # Recargar datos con pequeño delay para asegurar que el JSON esté listo
                    ventas_tab.reload_data()
                    
                    # Si hay texto en búsqueda, refiltrar para mostrar el nuevo producto
                    if hasattr(ventas_tab, 'search_input') and ventas_tab.search_input:
                        current_text = ventas_tab.search_input.text().strip()
                        if current_text:
                            print(f"🔍 Refiltrando con texto: '{current_text}'")
                            ventas_tab.filter_products()
                        else:
                            # Si no hay texto, limpiar la lista para forzar recarga completa
                            ventas_tab.products_list.clear()
                    
                    print(f"✅ VentasTab #{i+1} actualizado correctamente")
                    actualizaciones_exitosas += 1
                    
                except Exception as e:
                    print(f"❌ Error actualizando VentasTab #{i+1}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Resultado final
            resultado_exitoso = actualizaciones_exitosas > 0
            if resultado_exitoso:
                print(f"✅ Actualización completada: {actualizaciones_exitosas}/{len(ventas_tabs)} pantallas actualizadas")
            else:
                print("⚠️ No se actualizaron pantallas correctamente")
            
            return resultado_exitoso
            
        except Exception as e:
            print(f"❌ Error general en actualización de pantallas: {e}")
            import traceback
            traceback.print_exc()
            return False

    # ===========================
    # Utilidades
    # ===========================
    def _warn(self, msg: str) -> bool:
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Atención")
        box.setText(msg)

        # Forzamos estilo claro, independientemente del tema global
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setStyleSheet("""
            QMessageBox { background: #ffffff; }
            QMessageBox QLabel { color: #111111; }
            QMessageBox QFrame { background: #ffffff; border: 1px solid #dcdcdc; }
            QMessageBox QPushButton {
                color: #111111;
                background: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 4px 12px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover { background: #e9e9e9; }
            QMessageBox QPushButton:pressed { background: #e0e0e0; }
        """)

        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
        return False

    def closeEvent(self, event):
        """
        Sobrescribe el evento de cierre para mostrar confirmación
        """
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Icon.Question)
        reply.setWindowTitle("Confirmar cierre")
        
        # Mensaje diferente según el paso
        if self.stack.currentIndex() == 0:
            reply.setText("¿Estás seguro que querés cancelar el nuevo producto?")
            reply.setInformativeText("Se perderán todos los datos ingresados en el formulario.")
        else:
            reply.setText("¿Estás seguro que querés cancelar?")
            reply.setInformativeText("Se perderán todos los datos del producto y códigos generados.")
        
        # Aplicar estilo claro al mensaje de confirmación
        reply.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        reply.setStyleSheet("""
            QMessageBox { 
                background: #ffffff; 
            }
            QMessageBox QLabel { 
                color: #111111; 
                font-size: 12pt;
            }
            QMessageBox QFrame { 
                background: #ffffff; 
                border: 1px solid #dcdcdc; 
            }
            QMessageBox QPushButton {
                color: #111111;
                background: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 16px;
                min-width: 80px;
                font-weight: bold;
            }
            QMessageBox QPushButton:hover { 
                background: #e9e9e9; 
            }
            QMessageBox QPushButton:pressed { 
                background: #d9d9d9; 
            }
        """)
        
        # Configurar botones personalizados
        si_button = reply.addButton("Sí, cancelar", QMessageBox.ButtonRole.YesRole)
        no_button = reply.addButton("No, continuar", QMessageBox.ButtonRole.NoRole)
        
        # Establecer el botón "No" como predeterminado (más seguro)
        reply.setDefaultButton(no_button)
        
        # Ejecutar el diálogo y verificar la respuesta
        reply.exec()
        
        if reply.clickedButton() == si_button:
            # Usuario confirmó el cierre
            # Detener thread si está corriendo
            if self.codigo_thread and self.codigo_thread.isRunning():
                self.codigo_thread.terminate()
                self.codigo_thread.wait()
            event.accept()  # Permitir cerrar la ventana
            print("🚪 Usuario canceló la creación del producto")
        else:
            # Usuario decidió continuar
            event.ignore()  # Ignorar el evento de cierre
            print("📝 Usuario continúa con el producto")