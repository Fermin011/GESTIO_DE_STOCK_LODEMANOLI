# ventas.py
import time
from datetime import datetime
from pathlib import Path
import json

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QFrame, QListWidgetItem, QMessageBox,
    QDialog, QDialogButtonBox, QComboBox, QFormLayout, QGraphicsDropShadowEffect,
    QSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor, QColor

# ---- Backend (ventas) ----
from aplicacion.backend.ventas import controller as ventas_controller
from aplicacion.backend.ventas import crud as ventas_crud
# NUEVO: import explícito de la función solicitada
from aplicacion.backend.ventas.controller import cancelar_ultima_venta_controller

# ---- Backend (stock) ----
from aplicacion.backend.stock import controller as stock_controller
from aplicacion.backend.stock.crud import exportar_productos_json

# Búsqueda por código de barras en DB
from aplicacion.backend.stock.utils import buscar_productos_por_codigo

# ---- Backend (métricas) ----
from aplicacion.backend.metricas.ganancias.controller import registrar_ganancias_hoy_controller


# --------------------- Diálogo método de pago (estilizado) ---------------------
class MetodoPagoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Elegir método de pago")
        self.setFixedWidth(360)
        self.setStyleSheet("QDialog { background: #2a2a2a; }")

        # Header
        header = QFrame()
        header.setFixedHeight(44)
        header.setStyleSheet("""
            QFrame {
                background: #7B1FA2;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        titulo = QLabel("ELEGIR MÉTODO DE PAGO", header)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: white; font-weight: 700; letter-spacing: 1px;")
        h_header = QHBoxLayout(header)
        h_header.setContentsMargins(12, 0, 12, 0)
        h_header.addWidget(titulo)

        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1f1f1f;
                border: 1px solid #3b3b3b;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QLabel { color: #dddddd; font-size: 14px; }
            QComboBox {
                background: #2b2b2b; color: #eaeaea;
                padding: 6px 8px; border: 2px solid #1b8bb4; border-radius: 6px;
                min-width: 180px;
            }
            QComboBox:focus { border: 2px solid #1490c4; }
            QComboBox QAbstractItemView {
                background: #2b2b2b;
                selection-background-color: #147aa0; selection-color: white;
                border: 1px solid #3b3b3b; outline: none;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        self.combo = QComboBox(card)
        self.combo.addItems(["efectivo", "transferencia"])

        form = QFormLayout()
        form.setContentsMargins(16, 16, 16, 0)
        form.setSpacing(12)
        form.addRow(QLabel("Método de pago:"), self.combo)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel, parent=self)
        buttons.setStyleSheet("""
            QDialogButtonBox QPushButton {
                min-width: 96px; min-height: 36px; border-radius: 6px; font-weight: 600;
            }
            QDialogButtonBox QPushButton[text="OK"] { background: #1b8bb4; color: white; border: none; }
            QDialogButtonBox QPushButton[text="OK"]:hover { background: #147aa0; }
            QDialogButtonBox QPushButton[text="OK"]:pressed { background: #0f5e7b; }
            QDialogButtonBox QPushButton[text="Cancel"] { background: transparent; color: #e0e0e0; border: 2px solid #505050; }
            QDialogButtonBox QPushButton[text="Cancel"]:hover { background: #303030; }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        v_card = QVBoxLayout(card)
        v_card.setContentsMargins(0, 0, 12, 12)
        v_card.addLayout(form)
        v_card.addSpacing(6)
        v_card.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)
        root.addWidget(header)
        root.addWidget(card)

        self.combo.setFocus()
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint, True)

    def metodo(self) -> str:
        return self.combo.currentText()


# --------------------- NUEVO: Diálogo para cantidad en gramos ---------------------
class CantidadGramosDialog(QDialog):
    def __init__(self, producto_nombre, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Cantidad a vender")
        self.setFixedWidth(400)
        self.setStyleSheet("QDialog { background: #2a2a2a; }")

        # Header
        header = QFrame()
        header.setFixedHeight(44)
        header.setStyleSheet("""
            QFrame {
                background: #4CAF50;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
        """)
        titulo = QLabel("CANTIDAD A VENDER", header)
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: white; font-weight: 700; letter-spacing: 1px;")
        h_header = QHBoxLayout(header)
        h_header.setContentsMargins(12, 0, 12, 0)
        h_header.addWidget(titulo)

        # Card
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #1f1f1f;
                border: 1px solid #3b3b3b;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QLabel { color: #dddddd; font-size: 14px; }
            QSpinBox {
                background: #2b2b2b; color: #eaeaea;
                padding: 8px; border: 2px solid #4CAF50; border-radius: 6px;
                min-width: 120px; font-size: 16px; font-weight: bold;
            }
            QSpinBox:focus { border: 2px solid #66BB6A; }
        """)
        
        form = QFormLayout()
        form.setContentsMargins(20, 20, 20, 10)
        form.setSpacing(15)
        
        # Etiqueta del producto
        producto_label = QLabel(f"Producto: {producto_nombre}")
        producto_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 15px;")
        form.addRow(producto_label)
        
        # Campo para gramos
        self.gramos_spinbox = QSpinBox()
        self.gramos_spinbox.setRange(1, 50000)  # De 1 gramo a 50 kg
        self.gramos_spinbox.setValue(500)  # Valor por defecto 500g
        self.gramos_spinbox.setSuffix(" g")
        
        form.addRow(QLabel("Cantidad en gramos:"), self.gramos_spinbox)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                   QDialogButtonBox.StandardButton.Cancel, parent=self)
        buttons.setStyleSheet("""
            QDialogButtonBox QPushButton {
                min-width: 96px; min-height: 36px; border-radius: 6px; font-weight: 600;
            }
            QDialogButtonBox QPushButton[text="OK"] { background: #4CAF50; color: white; border: none; }
            QDialogButtonBox QPushButton[text="OK"]:hover { background: #45a049; }
            QDialogButtonBox QPushButton[text="Cancel"] { background: transparent; color: #e0e0e0; border: 2px solid #505050; }
            QDialogButtonBox QPushButton[text="Cancel"]:hover { background: #303030; }
        """)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 15)
        card_layout.addLayout(form)
        card_layout.addWidget(buttons, 0, Qt.AlignmentFlag.AlignRight)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)
        root.addWidget(header)
        root.addWidget(card)

        self.gramos_spinbox.setFocus()
        self.gramos_spinbox.selectAll()

    def get_gramos(self) -> int:
        return self.gramos_spinbox.value()


class VentasTab(QWidget):
    """Pantalla de Punto de Venta."""

    # --------------------- Utils precio ---------------------
    @staticmethod
    def _parse_price_ar(value) -> float:
        try:
            if isinstance(value, (int, float)):
                return float(value)
            if not isinstance(value, str):
                return 0.0
            s = value.strip().replace("$", "").replace(" ", "")
            s = s.replace(".", "").replace(",", ".")
            return float(s)
        except Exception:
            return 0.0

    @staticmethod
    def _format_price_ar(amount: float) -> str:
        s = f"{amount:,.2f}"
        return s.replace(",", "_").replace(".", ",").replace("_", ".")

    def __init__(self):
        super().__init__()
        
        # NUEVO: Identificador para facilitar búsqueda desde otros diálogos
        self.setObjectName("VentasTab")
        
        self.products_data = []
        self.load_products_data()

        # Detector de #código
        self.UMBRAL_CARACTERES = 5
        self.VENTANA_SEGUNDOS = 0.05
        self.REVERTIR_MS = 500
        self._len_prev = 0
        self._inicio_ventana = None
        self._conteo_en_ventana = 0
        self._modificado_rapido = False
        self._codigo_detectado = False
        self._esperando_codigo_completo = False
        self._ultimo_cambio = None

        # Buffer de códigos escaneados (sin '#')
        self._codigos_barras_usados: list[str] = []

        # Timers
        self._revertir_timer = QTimer(self)
        self._revertir_timer.setSingleShot(True)
        self._revertir_timer.timeout.connect(self._modo_normal)

        self._codigo_timer = QTimer(self)
        self._codigo_timer.setSingleShot(True)
        self._codigo_timer.timeout.connect(self._procesar_codigo_completo)

        self.setup_ui()

    # ===================== Carga de datos MEJORADA =====================
    def reload_data(self):
        """Recarga datos con logging mejorado"""
        print("🔄 VentasTab: Iniciando recarga de datos...")
        try:
            self.load_products_data()
            print(f"✅ VentasTab: {len(self.products_data)} productos cargados")
            
            # Si hay texto en búsqueda, refiltrar
            if hasattr(self, 'search_input') and self.search_input.text().strip():
                current_text = self.search_input.text().strip()
                print(f"🔍 VentasTab: Refiltrando con texto: '{current_text}'")
                self.filter_products()
                
        except Exception as e:
            print(f"❌ VentasTab: Error al recargar datos: {e}")

    def load_products_data(self):
        """Carga JSON de stock con verificación mejorada de estabilidad del archivo."""
        try:
            base_dir = Path(__file__).resolve().parent.parent
            json_path = base_dir / "frontend" / "json" / "stock.json"

            print(f"📁 VentasTab: Leyendo JSON desde {json_path}")

            if json_path.exists():
                # MEJORA: Verificar que el archivo no esté siendo escrito
                import time
                file_size = json_path.stat().st_size
                time.sleep(0.1)  # Pequeña pausa
                
                # Verificar que el tamaño no cambió (archivo estable)
                if json_path.stat().st_size == file_size and file_size > 0:
                    with open(json_path, 'r', encoding='utf-8') as file:
                        self.products_data = json.load(file)
                    print(f"✅ VentasTab: JSON cargado correctamente - {len(self.products_data)} productos")
                else:
                    print("⏳ VentasTab: Archivo JSON siendo escrito, reintentando...")
                    time.sleep(0.3)
                    with open(json_path, 'r', encoding='utf-8') as file:
                        self.products_data = json.load(file)
                    print(f"✅ VentasTab: JSON cargado después de reintento - {len(self.products_data)} productos")
            else:
                print("❌ VentasTab: JSON no existe, usando datos de ejemplo")
                self._cargar_datos_ejemplo()
        except Exception as e:
            print(f"❌ VentasTab: Error cargando JSON: {e}")
            self._cargar_datos_ejemplo()

    def _cargar_datos_ejemplo(self):
        self.products_data = [
            {"id": 1, "codigo": "871289371203", "nombre": "COCA COLA 1L", "categoria": "gaseosas",
             "stock": 0, "costo": "1.200,00", "precio": "3.400,00", "estado": "no disponible"},
            {"id": 2, "codigo": "1241515156", "nombre": "ARROZ 1KG", "categoria": "despensa",
             "stock": 4, "costo": "800,20", "precio": "1.200,10", "estado": "activo"},
        ]

    # ===================== UI =====================
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("PUNTO DE VENTA")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("QLabel { padding: 10px; background-color: transparent; }")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)

        # ----- Panel Izquierdo -----
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame { background-color: #e0e0e0; border: 1px solid #cccccc; border-radius: 6px; }")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        search_label = QLabel("🔍 Buscar Producto:")
        search_label.setStyleSheet("font-size: 14px; color: #858585;")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Código de barras o nombre…")
        self.search_input.setStyleSheet("""
            QLineEdit { border: 2px solid #1b8bb4; border-radius: 5px; padding-left: 8px;
                        font-size: 14px; background-color: white; color: black; }
            QLineEdit:focus { border: 2px solid #147aa0; }
        """)

        # NUEVO: Botón de actualizar
        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setFixedHeight(35)
        refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton { background-color: #28a745; color: white; border: none; border-radius: 5px; font-size: 12px; font-weight: bold; }
            QPushButton:hover { background-color: #218838; }
            QPushButton:pressed { background-color: #1e7e34; }
        """)
        refresh_btn.clicked.connect(self.reload_data)

        self.modo_label = QLabel("Modo: normal")
        self.modo_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")

        self.products_list = QListWidget()
        self.products_list.setStyleSheet("""
            QListWidget { border: 1px solid #858585; background-color: white; font-size: 13px; border-radius: 5px; color: black; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #eee; color: black; }
            QListWidget::item:selected { background-color: #e3f2fd; color: black; }
            QListWidget::item:hover { background-color: #f5f5f5; color: black; }
        """)

        left_layout.addWidget(search_label)
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(refresh_btn)  # NUEVO
        left_layout.addWidget(self.modo_label)
        left_layout.addWidget(self.products_list)

        # ----- Panel Derecho -----
        right_panel = QFrame()
        right_panel.setStyleSheet("QFrame { background-color: #e0e0e0; border: 1px solid #cccccc; border-radius: 6px; }")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        cart_label = QLabel("🛒 Carrito de Compras:")
        cart_label.setStyleSheet("font-size: 14px; color: #222;")

        self.cart_list = QListWidget()
        self.cart_list.setStyleSheet("""
            QListWidget { border: 1px solid #ccc; background-color: white; font-size: 13px; border-radius: 5px; color: black; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #eee; color: black; }
            QListWidget::item:selected { background-color: #A5D6A7; color: black; }
            QListWidget::item:hover { background-color: #C8E6C9; color: black; }
        """)
        self.cart_list.setSelectionMode(self.cart_list.SelectionMode.SingleSelection)

        right_layout.addWidget(cart_label)
        right_layout.addWidget(self.cart_list)
        right_layout.addStretch()

        self.total_label = QLabel("Total: $0,00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_label.setStyleSheet("""
            QLabel { font-size: 18px; font-weight: bold; color: #1b8bb4; background-color: #f7f7f7; padding: 10px; border-radius: 6px; }
        """)

        add_btn = QPushButton("➕ Agregar al Carrito")
        remove_btn = QPushButton("➖ Quitar del Carrito")
        clear_btn = QPushButton("🗑️ Limpiar Carrito")
        pay_btn = QPushButton("💰 Confirmar Venta")
        cancel_sale_btn = QPushButton("❌ Cancelar la última venta")  # NUEVO

        for btn in [add_btn, pay_btn]:
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: #1b8bb4; color: white; border: none; border-radius: 5px; font-size: 14px; font-weight: bold; }
                QPushButton:hover { background-color: #147aa0; }
                QPushButton:pressed { background-color: #0f5e7b; }
            """)
        for btn in [remove_btn, clear_btn]:
            btn.setFixedHeight(40)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background-color: white; color: #1b8bb4; border: 2px solid #1b8bb4; border-radius: 5px; font-size: 14px; }
                QPushButton:hover { background-color: #e6f0ff; }
                QPushButton:pressed { background-color: #cce0ff; }
            """)
        # Estilo rojo para cancelar última venta
        cancel_sale_btn.setFixedHeight(40)
        cancel_sale_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_sale_btn.setStyleSheet("""
            QPushButton { background-color: #d32f2f; color: white; border: none; border-radius: 5px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #b71c1c; }
            QPushButton:pressed { background-color: #7f0000; }
        """)

        right_layout.addWidget(self.total_label)
        right_layout.addWidget(add_btn)
        right_layout.addWidget(remove_btn)
        right_layout.addWidget(clear_btn)
        right_layout.addWidget(pay_btn)
        right_layout.addWidget(cancel_sale_btn)  # NUEVO

        content_layout.addWidget(left_panel, stretch=2)
        content_layout.addWidget(right_panel, stretch=1)

        main_layout.addWidget(title_label)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

        # Conexiones
        self.search_input.textChanged.connect(self._al_cambiar_texto_busqueda)
        self.products_list.itemDoubleClicked.connect(self.add_product_to_cart)
        add_btn.clicked.connect(self.add_selected_product_to_cart)
        remove_btn.clicked.connect(self.remove_selected_from_cart)
        clear_btn.clicked.connect(self.clear_cart_confirmed)
        pay_btn.clicked.connect(self.process_sale_flow)
        cancel_sale_btn.clicked.connect(self.cancel_last_sale_confirmed)  # NUEVO

        self._modo_normal()
        self.refresh_cart_view()

    # ===================== Búsqueda =====================
    def _al_cambiar_texto_busqueda(self):
        ahora = time.monotonic()
        texto_actual = self.search_input.text()
        delta = len(texto_actual) - self._len_prev
        self._ultimo_cambio = ahora

        if self._esperando_codigo_completo:
            self._len_prev = len(texto_actual)
            self._codigo_timer.start(200)
            return

        if delta > 0:
            if self._inicio_ventana is None or (ahora - self._inicio_ventana) > self.VENTANA_SEGUNDOS:
                self._inicio_ventana = ahora
                self._conteo_en_ventana = delta
                self._modificado_rapido = False
            else:
                self._conteo_en_ventana += delta

            if (self._conteo_en_ventana > self.UMBRAL_CARACTERES and
                (ahora - self._inicio_ventana) <= self.VENTANA_SEGUNDOS and
                not self._modificado_rapido and
                not self._esperando_codigo_completo):

                self._modo_rapido()
                if not texto_actual.startswith("#"):
                    self.search_input.blockSignals(True)
                    self.search_input.setText("#" + texto_actual)
                    cursor = self.search_input.textCursor() if hasattr(self.search_input, 'textCursor') else None
                    if cursor:
                        cursor.movePosition(QTextCursor.MoveOperation.End)
                        self.search_input.setTextCursor(cursor)
                    self.search_input.blockSignals(False)
                self._len_prev = len(self.search_input.text())
                self._modificado_rapido = True
                self._codigo_detectado = True
                self._esperando_codigo_completo = True
                self._codigo_timer.start(200)
                return

        if not texto_actual.startswith("#") and not self._esperando_codigo_completo:
            self.filter_products()

        self._revertir_timer.start(self.REVERTIR_MS)
        self._len_prev = len(self.search_input.text())

    def _procesar_codigo_completo(self):
        self._esperando_codigo_completo = False        # noqa
        self.filter_products()

    def _modo_rapido(self):
        self.modo_label.setText("Modo: código de barras - esperando pausa…")
        self.modo_label.setStyleSheet("font-size: 12px; color: #d32f2f; font-weight: bold; padding: 5px;")

    def _modo_normal(self):
        self.modo_label.setText("Modo: normal")
        self.modo_label.setStyleSheet("font-size: 12px; color: #666; padding: 5px;")
        self._modificado_rapido = False
        self._codigo_detectado = False
        self._esperando_codigo_completo = False
        if self._codigo_timer.isActive():
            self._codigo_timer.stop()

    def buscar_producto_por_id_en_json(self, producto_id):
        for product in self.products_data:
            if str(product.get("id", "")) == str(producto_id):
                return product
        return None
    #
    def filter_products(self):
        search_text = self.search_input.text().strip()
        self.products_list.clear()
        if not search_text:
            return

        if search_text.startswith("#"):
            codigo_barras = search_text[1:]
            # REMOVIDO: self.reload_data() - causaba bucle infinito
            try:
                productos = stock_controller.listar_productos_controller()
                unidades = []
                for p in productos:
                    unidades += stock_controller.obtener_unidades_de_producto_controller(p.id)
                encontrados = buscar_productos_por_codigo(unidades, codigo_barras)
                if encontrados:
                    unidad = encontrados[0]
                    product_data = self.buscar_producto_por_id_en_json(unidad.producto_id)
                    if product_data:
                        self.mostrar_producto_en_lista(product_data)
                    else:
                        self.products_list.addItem(QListWidgetItem("⚠ Producto no disponible en stock"))
                else:
                    self.products_list.addItem(QListWidgetItem("⚠ Código de barras no encontrado"))
            except Exception as e:
                print(f"⚠ Error búsqueda por código: {e}")
                self.products_list.addItem(QListWidgetItem("⚠ Error en búsqueda por código"))
        else:
            s = search_text.lower()
            for product in self.products_data:
                if s in product.get("nombre", "").lower():
                    self.mostrar_producto_en_lista(product)

    def mostrar_producto_en_lista(self, product):
        nombre = product.get("nombre", "Sin nombre")
        precio = product.get("precio", "0,00")
        stock = product.get("stock", 0)
        categoria = product.get("categoria", "")
        
        # NUEVO: Mostrar diferente info según si es divisible
        es_divisible = product.get("es_divisible", False)
        if es_divisible:
            stock_text = f"{stock} kg"
            tipo_text = "🏺 A granel"
        else:
            stock_text = f"{stock}"
            tipo_text = ""
        
        item_text = f"{nombre}\n${precio} | Stock: {stock_text} | {categoria}"
        if tipo_text:
            item_text += f"\n{tipo_text}"
            
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, product)
        self.products_list.addItem(item)

    # ===================== Carrito =====================
    def refresh_cart_view(self):
        """
        Refresca la vista del carrito y calcula correctamente los subtotales y el total.
        - Para unidades: subtotal = precio_unitario * cantidad
        - Para granel (gramos): subtotal = precio_por_kilo * (gramos / 1000)
        """
        self.cart_list.clear()
        carrito = ventas_controller.obtener_carrito_controller()
        total = 0.0

        for it in carrito:
            nombre = it.get("nombre", "Ítem")
            precio_por_unidad_o_kilo = float(it.get("precio_unitario", 0))
            es_granel = bool(it.get("es_granel", False))

            if es_granel:
                # CORREGIDO: Para productos a granel, usar cantidad_gramos si existe
                if "cantidad_gramos" in it:
                    gramos = float(it.get("cantidad_gramos", 0))
                    subtotal = precio_por_unidad_o_kilo * (gramos / 1000.0)
                    cant_text = f"{int(gramos)} g"
                else:
                    # Fallback: si no existe cantidad_gramos, cantidad está en kg
                    cantidad_kg = float(it.get("cantidad", 0))
                    gramos = cantidad_kg * 1000
                    subtotal = precio_por_unidad_o_kilo * cantidad_kg
                    cant_text = f"{int(gramos)} g"
            else:
                # cantidad viene en unidades
                cantidad = float(it.get("cantidad", 0))
                subtotal = precio_por_unidad_o_kilo * cantidad
                # Mostrar sin ceros innecesarios
                cant_text = f"{cantidad:g}"

            total += subtotal

            # Mostrar línea del carrito (precio se muestra tal cual; para granel es por kilo)
            self.cart_list.addItem(QListWidgetItem(
                f"{nombre}  |  ${self._format_price_ar(precio_por_unidad_o_kilo)} x {cant_text}  →  ${self._format_price_ar(subtotal)}"
            ))

        self.total_label.setText(f"Total: ${self._format_price_ar(total)}")


    def add_product_to_cart(self, item):
        product_data = item.data(Qt.ItemDataRole.UserRole)
        if product_data:
            self.add_to_cart(product_data)

    def add_selected_product_to_cart(self):
        current_item = self.products_list.currentItem()
        if current_item:
            product_data = current_item.data(Qt.ItemDataRole.UserRole)
            if product_data:
                self.add_to_cart(product_data)

    def _cantidad_en_carrito(self, producto_id: int) -> float:
        cant = 0.0
        for it in ventas_controller.obtener_carrito_controller():
            if int(it.get("producto_id", -1)) == int(producto_id):
                cantidad_item = float(it.get("cantidad", 0))
                # Si es producto a granel, convertir gramos a kg para el cálculo
                if it.get("es_granel", False):
                    cantidad_item = cantidad_item / 1000.0  # Convertir gramos a kg
                cant += cantidad_item
        return cant

    # ---------- helper: agregar forzado al carrito (incluye unidad_id) ----------
    def _agregar_al_carrito_sin_validar(self, product_data, cantidad=1, unidad_id=0, codigo_barras=None, es_granel=False, **kwargs):
        """
        Empuja el ítem directo al carrito del backend (ventas_crud.carrito),
        seteando también 'tipo_venta' para que el controller no falle.
        """
        try:
            # si tenemos una unidad concreta (por #código), va por unidad_id; si no, por producto_id
            tipo_venta = "unidad_id" if (unidad_id and int(unidad_id) > 0) else "producto_id"

            item = {
                "producto_id": int(product_data.get("id")),
                "unidad_id": int(unidad_id) if unidad_id else None,   # puede ser None si no hay unidad
                "nombre": product_data.get("nombre", "Sin nombre"),
                "precio_unitario": float(self._parse_price_ar(product_data.get("precio", "0"))),
                "cantidad": float(cantidad),
                "codigo_barras": (codigo_barras or ""),
                "tipo_venta": tipo_venta,
                "forzado": True,
                "es_granel": es_granel,  # NUEVO
            }
            ventas_crud.carrito.append(item)
            return True
        except Exception as e:
            print(f"[WARN] _agregar_al_carrito_sin_validar falló: {e}")
            return False
    #########
    def add_to_cart(self, product_data):
        """
        MODIFICADO: Maneja venta a granel para productos divisibles
        """
        prod_id = int(product_data.get("id"))
        es_divisible = product_data.get("es_divisible", False)
        
        # NUEVO: Si es divisible (a granel), preguntar cantidad en gramos
        if es_divisible:
            dialog = CantidadGramosDialog(product_data.get("nombre", ""), self)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return
            
            gramos = dialog.get_gramos()
            cantidad_kg = gramos / 1000.0  # Convertir a kg para el cálculo
            
            # Verificar stock disponible
            try:
                stock_disp = float(product_data.get("stock", 0))
            except Exception:
                stock_disp = 0.0

            en_carrito = self._cantidad_en_carrito(prod_id)

            if stock_disp > 0 and (en_carrito + cantidad_kg) > stock_disp:
                QMessageBox.information(
                    self, "Stock insuficiente",
                    f"No hay suficiente stock.\n"
                    f"Disponible: {stock_disp} kg, en carrito: {en_carrito} kg\n"
                    f"Intentando agregar: {cantidad_kg} kg"
                )
                return

            # CORREGIDO: Usar métodos específicos para granel
            # Verificar si viene de código de barras
            tx = (self.search_input.text() or "").strip()
            if tx.startswith("#") and len(tx) > 1:
                codigo_barras = tx[1:]
                res = ventas_controller.agregar_producto_granel_por_codigo_controller(codigo_barras, gramos)
            else:
                res = ventas_controller.agregar_producto_granel_por_id_controller(prod_id, gramos)
            
            if not res.get("exito"):
                # Si falla, agregar forzado (mantener lógica existente)
                if not self._agregar_al_carrito_sin_validar(product_data, gramos, es_granel=True):
                    QMessageBox.warning(self, "Error", "No se pudo agregar el producto a granel.")
                    return
            # NO necesitamos marcar es_granel=True aquí porque los métodos específicos ya lo hacen

        else:
            # Lógica original para productos por unidades (SIN CAMBIOS)
            try:
                stock_disp = int(float(product_data.get("stock", 0)))
            except Exception:
                stock_disp = 0

            en_carrito = self._cantidad_en_carrito(prod_id)

            permitir_forzado = False
            if stock_disp == 0:
                resp = QMessageBox.question(
                    self, "Sin stock registrado",
                    "Estás por vender algo sin unidades registradas, ¿continuar?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
                permitir_forzado = True

            if stock_disp > 0 and (en_carrito + 1) > stock_disp:
                QMessageBox.information(
                    self, "Stock insuficiente",
                    f"No podés agregar más de lo disponible.\n"
                    f"Hay {stock_disp} en stock y ya tenés {en_carrito:g} en el carrito."
                )
                return

            # Intento normal por controller
            res = ventas_controller.agregar_producto_por_id_controller(prod_id, 1)

            if not res.get("exito"):
                if permitir_forzado:
                    # Si venís con #código, intento resolver la unidad exacta
                    tx = (self.search_input.text() or "").strip()
                    unidad_id = 0
                    codigo_barra = None
                    if tx.startswith("#") and len(tx) > 1:
                        codigo_barra = tx[1:]
                        try:
                            productos = stock_controller.listar_productos_controller()
                            unidades = []
                            for p in productos:
                                unidades += stock_controller.obtener_unidades_de_producto_controller(p.id)
                            encontrados = buscar_productos_por_codigo(unidades, codigo_barra)
                            if encontrados:
                                unidad_id = int(encontrados[0].id)
                        except Exception as e:
                            print(f"[WARN] No pude resolver unidad por código: {e}")

                    if not self._agregar_al_carrito_sin_validar(product_data, 1, unidad_id=unidad_id, codigo_barras=codigo_barra):
                        QMessageBox.warning(self, "Error", "No se pudo agregar el ítem sin validar.")
                        return
                else:
                    QMessageBox.warning(self, "No se pudo agregar", res.get("mensaje", "Error al agregar."))
                    return

        # Si se está usando #código, registrarlo (SIN CAMBIOS)
        tx = (self.search_input.text() or "").strip()
        if tx.startswith("#") and len(tx) > 1:
            self._codigos_barras_usados.append(tx[1:])

        self.refresh_cart_view()
        if self.cart_list.count() > 0:
            self.cart_list.setCurrentRow(self.cart_list.count() - 1)

    def remove_selected_from_cart(self):
        row = self.cart_list.currentRow()
        if row < 0:
            return
        ventas_controller.eliminar_item_carrito_controller(row)
        self.refresh_cart_view()

    def clear_cart_confirmed(self):
        if self.cart_list.count() == 0:
            return
        if QMessageBox.question(
            self, "Vaciar carrito",
            "¿Querés limpiar todo el carrito? Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            ventas_controller.limpiar_carrito_controller()
            self._codigos_barras_usados.clear()
            self.refresh_cart_view()

    # ---------- helper: leer stock real desde BD (objeto o dict) ----------
    def _get_stock_real(self, pid: int) -> int:
        try:
            obj = ventas_crud.obtener_producto_por_id(pid)
            if obj is None:
                return 0
            if isinstance(obj, dict):
                val = obj.get("cantidad", obj.get("stock", 0))
            else:
                val = getattr(obj, "cantidad", getattr(obj, "stock", 0))
            return int(float(val or 0))
        except Exception:
            return 0

    # ===================== Flujo de venta =====================
    def process_sale_flow(self):
        carrito = ventas_controller.obtener_carrito_controller()
        if not carrito:
            QMessageBox.information(self, "Carrito vacío", "Agregá al menos un producto antes de confirmar.")
            return

        # 0) Revalidar stock real en DB por cada ítem
        faltantes = []
        for it in carrito:
            pid = int(it.get("producto_id"))
            cant = float(it.get("cantidad", 0))
            stock_real = self._get_stock_real(pid)
            if cant > stock_real:
                faltantes.append((it.get("nombre", f"ID {pid}"), stock_real, cant))

        if faltantes:
            detalle = "\n".join([f"• {nom}: solo hay stock de {stk} (en carrito: {cant:g})"
                                 for nom, stk, cant in faltantes])
            resp = QMessageBox.question(
                self, "Stock insuficiente",
                f"Se detectó falta de stock en algunos productos:\n\n{detalle}\n\n"
                f"¿Continuar de todos modos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if resp != QMessageBox.StandardButton.Yes:
                return

        # 1) Elegir método de pago
        dlg = MetodoPagoDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        metodo = dlg.metodo()

        # 2) Confirmación final
        if QMessageBox.question(
            self, "Confirmar venta", f"Método: {metodo}\n\n¿Deseás confirmar la venta?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        ) != QMessageBox.StandardButton.Yes:
            return

        # 3) Confirmar venta y post-proceso
        self._confirm_and_process_sale(metodo)

    def _confirm_and_process_sale(self, metodo_pago: str):
        # Marca temporal para esperar aplicación de cambios en DB
        marca_inicio_iso = datetime.now().isoformat()

        # --- Normalizo carrito: asegurar 'tipo_venta' en todos los ítems ---
        try:
            for it in ventas_crud.carrito:
                if "tipo_venta" not in it:
                    unidad_id = int(it.get("unidad_id") or 0)
                    it["tipo_venta"] = "unidad_id" if unidad_id > 0 else "producto_id"
        except Exception as e:
            print(f"[WARN] Normalizando carrito: {e}")
        # -------------------------------------------------------------------

        data = {"metodo_pago": metodo_pago, "usuario_id": 1}
        resultado = ventas_controller.confirmar_venta_controller(data)
        if not resultado.get("exito"):
            QMessageBox.critical(self, "Error", resultado.get("mensaje", "No se pudo confirmar la venta"))
            return

        # 3.1 Inactivar unidad por cada código escaneado (no vuelve a descontar stock)
        for codigo in list(self._codigos_barras_usados):
            try:
                ventas_crud.actualizar_estado_unidad_inactivo_por_codigo(codigo)
            except Exception as e:
                print(f"[WARN] No se pudo inactivar unidad {codigo}: {e}")

        # 3.2 Esperar confirmación de cambios y limpiar unidades fantasma
        productos_vendidos = {p.get("producto_id") for p in resultado.get("productos", []) if p.get("producto_id")}
        if not productos_vendidos:
            for it in ventas_controller.obtener_carrito_controller():
                pid = it.get("producto_id")
                if pid:
                    productos_vendidos.add(int(pid))

        def _parse_iso(dt_val):
            from datetime import datetime as _dt
            try:
                return _dt.fromisoformat(str(dt_val))
            except Exception:
                return None

        def esperar_stock(pid, timeout=3.0, interval=0.1):
            ini = time.monotonic()
            while time.monotonic() - ini < timeout:
                try:
                    prod = ventas_crud.obtener_producto_por_id(pid)
                    um = getattr(prod, "ultima_modificacion", None)
                    if um and _parse_iso(um) and _parse_iso(um) >= _parse_iso(marca_inicio_iso):
                        return True
                except Exception:
                    pass
                time.sleep(interval)
            return False

        for pid in productos_vendidos:
            ok = esperar_stock(pid, timeout=3.0, interval=0.1)
            if not ok:
                time.sleep(2.0)  # colchón
            try:
                stock_controller.limpiar_unidades_fantasma_controller(pid)
            except Exception as e:
                print(f"[WARN] limpiar_unidades_fantasma_controller({pid}) falló: {e}")

            # 3.2.1 NUEVO: Purga definitiva de unidades INACTIVAS del producto vendido
            try:
                ventas_controller.purgar_unidades_inactivas_controller(pid)
            except Exception as e:
                print(f"[WARN] purgar_unidades_inactivas_controller({pid}) falló: {e}")

        # 3.3 Regenerar JSON y refrescar UI
        try:
            exportar_productos_json()
        except Exception as e:
            print(f"[WARN] No se pudo exportar stock.json: {e}")

        # 3.4 REGISTRAR GANANCIAS AUTOMÁTICAMENTE
        try:
            registro_result = registrar_ganancias_hoy_controller(sobrescribir=True)
            if registro_result.get("success"):
                print(f"[INFO] Ganancias registradas automáticamente: {registro_result.get('message', 'Éxito')}")
            else:
                print(f"[WARN] No se pudo registrar ganancias automáticamente: {registro_result.get('message', 'Error desconocido')}")
        except Exception as e:
            print(f"[ERROR] Error al registrar ganancias automáticamente: {e}")

        # 3.5 ACTUALIZAR PANTALLA DE MÉTRICAS
        try:
            # Buscar la ventana principal que contiene el tab de métricas
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, 'metricas_tab'):
                parent_window = parent_window.parent()
            
            if parent_window and hasattr(parent_window, 'metricas_tab'):
                parent_window.metricas_tab.refresh_all_data()
                print("[INFO] Pantalla de métricas actualizada automáticamente")
        except Exception as e:
            print(f"[WARN] No se pudo actualizar pantalla de métricas: {e}")

        ventas_controller.limpiar_carrito_controller()
        self._codigos_barras_usados.clear()
        self.refresh_cart_view()
        self.reload_data()
        self.filter_products()  # respeta el texto de búsqueda

        QMessageBox.information(self, "Venta realizada", "✅ Venta registrada con éxito.")


    # ===================== NUEVO: cancelar última venta =====================
    def cancel_last_sale_confirmed(self):
        """
        Pregunta confirmación y, si aceptás, llama a cancelar_ultima_venta_controller().
        Refresca la UI si todo sale bien.
        """
        if QMessageBox.question(
            self, "Cancelar última venta",
            "¿Estás seguro de que querés cancelar la última venta registrada?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            try:
                resultado = cancelar_ultima_venta_controller()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error al cancelar la venta:\n{e}")
                return

            if resultado.get("exito"):
                QMessageBox.information(self, "Venta cancelada", "✅ Última venta cancelada con éxito.")
                # Refrescamos datos y carrito
                self.refresh_cart_view()
                self.reload_data()
                self.filter_products()
            else:
                QMessageBox.warning(self, "Error", resultado.get("mensaje", "❌ No se pudo cancelar la venta."))