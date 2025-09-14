# aplicacion/frontend/stock_ventanas/categorias.py
from __future__ import annotations

from pathlib import Path
import json
from typing import List, Dict

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QFontMetrics, QPalette, QColor
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QGridLayout, QMessageBox, QStackedWidget,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QSpacerItem, QComboBox, QListView
)

THIS_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = THIS_DIR.parent
JSON_CATEGORIAS = FRONTEND_DIR / "json" / "categorias.json"
JSON_STOCK = FRONTEND_DIR / "json" / "stock.json"


# =========================
# Helpers de estilo para combos (siempre texto negro/fondo blanco)
# =========================
def style_combo_black_on_white(combo: QComboBox):
    combo.setStyleSheet("""
        QComboBox {
            background: #ffffff;
            color: #000000;
            border: 2px solid #888888;
            border-radius: 14px;
            padding: 4px 10px;
            font-size: 14px;
        }
        QComboBox:focus { border-color: #21AFBD; }
        QComboBox QAbstractItemView {
            background: #ffffff;
            color: #000000;
            selection-background-color: #E3F2FD;
            selection-color: #000000;
            border: 1px solid #888888;
            outline: 0;
        }
        QComboBox QAbstractItemView::item { color: #000000; }
    """)
    view = QListView()
    pal = view.palette()
    pal.setColor(QPalette.ColorRole.Text, QColor("#000000"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#FFFFFF"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#E3F2FD"))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#000000"))
    view.setPalette(pal)
    view.setStyleSheet("""
        QListView { background: #ffffff; color: #000000; }
        QListView::item:selected { background: #E3F2FD; color: #000000; }
    """)
    combo.setView(view)


# =========================
# Diálogo "Agregar categoría" (solo UI)
# =========================
class AddCategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Agregar categoría")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._build_ui()

    def _build_ui(self):
        self.setMinimumSize(520, 360)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)

        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: #4A4A4A; border: 2px solid #5A5A5A; border-radius: 18px; }
        """)
        cont_lyt = QVBoxLayout(container)
        cont_lyt.setContentsMargins(28, 24, 28, 24)
        cont_lyt.setSpacing(18)

        title = QLabel("AGREGAR CATEGORÍA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2ECC71; font-weight: 900; font-size: 20px;")
        cont_lyt.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border: 2px solid #CFCFCF; border-radius: 16px; }
        """)
        card_lyt = QVBoxLayout(card)
        card_lyt.setContentsMargins(24, 24, 24, 24)
        card_lyt.setSpacing(14)

        # Nombre
        row_nombre = QHBoxLayout()
        lbl_nombre = QLabel("Nombre:")
        lbl_nombre.setStyleSheet("color: #2b2b2b; font-size: 16px;")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Escribí el nombre de la categoría...")
        self.name_edit.setFixedHeight(36)
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background: #ffffff; color: #000000; border: 2px solid #888888;
                border-radius: 14px; padding: 6px 10px; font-size: 14px;
            }
            QLineEdit:focus { border-color: #21AFBD; }
        """)
        row_nombre.addWidget(lbl_nombre)
        row_nombre.addSpacing(12)
        row_nombre.addWidget(self.name_edit, 1)
        card_lyt.addLayout(row_nombre)

        # Descripción
        row_desc = QHBoxLayout()
        lbl_desc = QLabel("Descripción:")
        lbl_desc.setStyleSheet("color: #2b2b2b; font-size: 16px;")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Descripción de la categoría (opcional)...")
        self.desc_edit.setFixedHeight(36)
        self.desc_edit.setStyleSheet("""
            QLineEdit {
                background: #ffffff; color: #000000; border: 2px solid #888888;
                border-radius: 14px; padding: 6px 10px; font-size: 14px;
            }
            QLineEdit:focus { border-color: #21AFBD; }
        """)
        row_desc.addWidget(lbl_desc)
        row_desc.addSpacing(12)
        row_desc.addWidget(self.desc_edit, 1)
        card_lyt.addLayout(row_desc)

        cont_lyt.addWidget(card, 1)

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        btn_cancel = QPushButton("CANCELAR")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedSize(220, 56)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; color: #0B0B0B; border: 2px solid #E94C4C;
                border-radius: 26px; font-weight: 800; letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #FF8383; }
            QPushButton:pressed { background-color: #E94C4C; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btns.addSpacing(24)

        btn_ok = QPushButton("GUARDAR")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedSize(220, 56)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71; color: #0B0B0B; border: 2px solid #27AE60;
                border-radius: 26px; font-weight: 800; letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #45D882; }
            QPushButton:pressed { background-color: #27AE60; }
        """)
        btn_ok.clicked.connect(self.accept)
        btns.addWidget(btn_ok)

        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        cont_lyt.addLayout(btns)
        root.addWidget(container)

    def get_category_data(self) -> Dict[str, str]:
        return {
            "nombre": (self.name_edit.text() or "").strip(),
            "descripcion": (self.desc_edit.text() or "").strip()
        }


# =========================
# Diálogo "Eliminar categoría" (solo UI con combo)
# =========================
class RemoveCategoryDialog(QDialog):
    def __init__(self, categories: List[Dict], parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Eliminar categoría")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._categories = categories or []
        self._build_ui()

    def _build_ui(self):
        self.setMinimumSize(520, 360)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)

        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: #4A4A4A; border: 2px solid #5A5A5A; border-radius: 18px; }
        """)
        cont_lyt = QVBoxLayout(container)
        cont_lyt.setContentsMargins(28, 24, 28, 24)
        cont_lyt.setSpacing(18)

        title = QLabel("ELIMINAR CATEGORÍA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FF6B6B; font-weight: 900; font-size: 20px;")
        cont_lyt.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border: 2px solid #CFCFCF; border-radius: 16px; }
        """)
        card_lyt = QVBoxLayout(card)
        card_lyt.setContentsMargins(24, 24, 24, 24)
        card_lyt.setSpacing(14)

        row = QHBoxLayout()
        lbl = QLabel("Categoría:")
        lbl.setStyleSheet("color: #2b2b2b; font-size: 16px;")
        self.combo = QComboBox()
        self.combo.setMinimumHeight(36)
        style_combo_black_on_white(self.combo)
        for cat in self._categories:
            if isinstance(cat, dict):
                nombre = cat.get("nombre", "")
                if isinstance(nombre, str) and nombre.strip():
                    self.combo.addItem(nombre)
        row.addWidget(lbl); row.addSpacing(12); row.addWidget(self.combo, 1)
        card_lyt.addLayout(row)

        cont_lyt.addWidget(card, 1)

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        btn_cancel = QPushButton("CANCELAR")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedSize(220, 56)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #B0B0B0; color: #0B0B0B; border: 2px solid #9A9A9A;
                border-radius: 26px; font-weight: 800; letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #C4C4C4; }
            QPushButton:pressed { background-color: #9A9A9A; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btns.addSpacing(24)

        btn_ok = QPushButton("ELIMINAR")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedSize(220, 56)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; color: #0B0B0B; border: 2px solid #E94C4C;
                border-radius: 26px; font-weight: 800; letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #FF8383; }
            QPushButton:pressed { background-color: #E94C4C; }
        """)
        btn_ok.clicked.connect(self.accept)
        btns.addWidget(btn_ok)

        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        cont_lyt.addLayout(btns)
        root.addWidget(container)

    def get_selected_category(self) -> str:
        return self.combo.currentText().strip()

    def get_selected_category_data(self) -> Dict:
        selected_name = self.get_selected_category()
        for cat in self._categories:
            if cat.get("nombre") == selected_name:
                return cat
        return {}


# =========================
# Diálogo genérico para elegir producto (solo UI)
# =========================
class ProductPickDialog(QDialog):
    """Dialog con combo para elegir un producto de una lista."""
    def __init__(self, title: str, label: str, products: List[Dict], parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._products = products or []
        self._build_ui(label)

    def _build_ui(self, label_text: str):
        self.setMinimumSize(620, 380)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(16)

        container = QFrame()
        container.setStyleSheet("""
            QFrame { background-color: #4A4A4A; border: 2px solid #5A5A5A; border-radius: 18px; }
        """)
        cont_lyt = QVBoxLayout(container)
        cont_lyt.setContentsMargins(28, 24, 28, 24)
        cont_lyt.setSpacing(18)

        title = QLabel(self.windowTitle().upper())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # color según acción (verde para agregar, rojo para eliminar)
        color = "#2ECC71" if "AGREGAR" in self.windowTitle().upper() else "#FF6B6B"
        title.setStyleSheet(f"color: {color}; font-weight: 900; font-size: 20px;")
        cont_lyt.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border: 2px solid #CFCFCF; border-radius: 16px; }
        """)
        card_lyt = QVBoxLayout(card)
        card_lyt.setContentsMargins(24, 24, 24, 24)
        card_lyt.setSpacing(14)

        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setStyleSheet("color: #2b2b2b; font-size: 16px;")
        self.combo = QComboBox()
        self.combo.setMinimumHeight(36)
        style_combo_black_on_white(self.combo)
        for p in self._products:
            if isinstance(p, dict):
                nombre = p.get("nombre", "")
                if nombre:
                    self.combo.addItem(nombre)
        row.addWidget(lbl); row.addSpacing(12); row.addWidget(self.combo, 1)
        card_lyt.addLayout(row)

        cont_lyt.addWidget(card, 1)

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        btn_cancel = QPushButton("CANCELAR")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedSize(220, 56)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #B0B0B0; color: #0B0B0B; border: 2px solid #9A9A9A;
                border-radius: 26px; font-weight: 800; letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #C4C4C4; }
            QPushButton:pressed { background-color: #9A9A9A; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btns.addSpacing(24)

        btn_ok = QPushButton("GUARDAR")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedSize(220, 56)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71; color: #0B0B0B; border: 2px solid #27AE60;
                border-radius: 26px; font-weight: 800; letter-spacing: 0.5px;
            }
            QPushButton:hover { background-color: #45D882; }
            QPushButton:pressed { background-color: #27AE60; }
        """)
        btn_ok.clicked.connect(self.accept)
        btns.addWidget(btn_ok)

        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        cont_lyt.addLayout(btns)
        root.addWidget(container)

    def get_selected_product(self) -> str:
        return self.combo.currentText().strip()

    def get_selected_product_data(self) -> Dict:
        selected_name = self.get_selected_product()
        for p in self._products:
            if p.get("nombre") == selected_name:
                return p
        return {}


# =========================
# Tabla de productos para una categoría (simplificada)
# =========================
class CategoryProductsTable(QWidget):
    requestBack = pyqtSignal()

    def __init__(self, categoria: str, parent=None):
        super().__init__(parent)
        self.categoria = categoria
        self.products_data: List[Dict] = []
        self.filtered_data: List[Dict] = []
        self._load_products_data()
        self._build_ui()
        self._apply_category_filter()

    # ---- data ----
    def _load_products_data(self):
        try:
            if JSON_STOCK.exists():
                self.products_data = json.loads(JSON_STOCK.read_text(encoding="utf-8"))
                print(f"Productos disponibles para venta: {len(self.products_data)}")
            else:
                print(f"No existe {JSON_STOCK}")
                self.products_data = []
        except Exception as e:
            print(f"[categorias] Error leyendo {JSON_STOCK}: {e}")
            self.products_data = []

    def set_category(self, categoria: str):
        self.categoria = categoria
        self.category_title.setText(f"CATEGORÍA: {self.categoria.upper()}")
        self.search_input.clear()
        self._apply_category_filter()

    def _apply_category_filter(self):
        cat_norm = (self.categoria or "").strip().lower()
        self.filtered_data = [
            p for p in self.products_data
            if str(p.get("categoria", "")).strip().lower() == cat_norm
        ]
        self._load_table(self.filtered_data)

    # ---- ui ----
    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(14)

        header = QHBoxLayout()

        back = QPushButton("← VOLVER A CATEGORÍAS")
        back.setFixedHeight(36)
        back.setCursor(Qt.CursorShape.PointingHandCursor)
        back.setStyleSheet("""
            QPushButton {
                background-color: #21AFBD; color: #FFFFFF; border: 1px solid #1A98A6;
                border-radius: 18px; padding: 6px 14px; font-weight: 700;
            }
            QPushButton:hover  { background-color: #25BCD0; }
            QPushButton:pressed{ background-color: #1C9FB0; }
        """)
        back.clicked.connect(self._emit_back)

        self.category_title = QLabel(f"CATEGORÍA: {self.categoria.upper()}")
        self.category_title.setStyleSheet("color: white; font-weight: bold;")
        self.category_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(back)
        header.addStretch(1)
        header.addWidget(self.category_title)
        header.addStretch(1)
        header.addSpacing(120)

        # buscador
        search_row = QHBoxLayout()
        search_row.setSpacing(12)
        search_lbl = QLabel("Buscar:")
        search_lbl.setStyleSheet("color: white; font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("buscar por nombre de producto...")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px; font-size: 14px; border: 2px solid #6A6A6A; border-radius: 5px;
                background-color: white; color: black;
            }
            QLineEdit:focus { border: 2px solid #21AFBD; }
        """)
        self.search_input.textChanged.connect(self._filter_by_text)

        search_row.addWidget(search_lbl)
        search_row.addWidget(self.search_input, 1)

        # tabla (simplificada)
        self.table = QTableWidget()
        self._setup_table()

        main.addLayout(header)
        main.addLayout(search_row)
        main.addWidget(self.table)

    def _setup_table(self):
        headers = ["NOMBRE", "CATEGORIA", "STOCK", "PRECIO", "ESTADO"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; border: 1px solid #CCCCCC; border-radius: 5px;
                gridline-color: #DDDDDD; font-size: 13px; selection-background-color: #E3F2FD; color: black;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #EEEEEE; color: black; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: black; }
            QHeaderView::section {
                background-color: #F5F5F5; padding: 8px; border: 1px solid #DDDDDD;
                font-weight: bold; color: black;
            }
        """)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # que la tabla se estire con el contenedor
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        header = self.table.horizontalHeader()

        # columnas fijas (ancho mínimo razonable)
        self.table.setColumnWidth(2, 90)   # STOCK
        self.table.setColumnWidth(3, 110)  # PRECIO
        self.table.setColumnWidth(4, 120)  # ESTADO

        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        # estas dos columnas se ESTIRAN para ocupar el resto del ancho
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # NOMBRE
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # CATEGORIA


    def _load_table(self, data: List[Dict]):
        self.table.setRowCount(len(data))
        for row, product in enumerate(data):
            def add(col, text, align=Qt.AlignmentFlag.AlignLeft):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                item.setForeground(Qt.GlobalColor.black)
                self.table.setItem(row, col, item)

            add(0, product.get("nombre", ""), Qt.AlignmentFlag.AlignLeft)
            add(1, product.get("categoria", ""), Qt.AlignmentFlag.AlignCenter)
            add(2, product.get("stock", ""), Qt.AlignmentFlag.AlignCenter)
            add(3, product.get("precio", ""), Qt.AlignmentFlag.AlignRight)

            estado_item = QTableWidgetItem(str(product.get("estado", "")))
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if str(product.get("estado", "")).lower() == "activo":
                estado_item.setBackground(Qt.GlobalColor.green)
                estado_item.setForeground(Qt.GlobalColor.white)
            else:
                estado_item.setBackground(Qt.GlobalColor.red)
                estado_item.setForeground(Qt.GlobalColor.white)
            self.table.setItem(row, 4, estado_item)

        self._filter_by_text(self.search_input.text())

    def _filter_by_text(self, text: str):
        text = (text or "").lower().strip()
        for r in range(self.table.rowCount()):
            nombre = self.table.item(r, 0).text().lower() if self.table.item(r, 0) else ""
            self.table.setRowHidden(r, text not in nombre)

    def _emit_back(self):
        self.requestBack.emit()


# =========================
# Pantalla de Categorías (grilla + tabla por categoría)
# =========================
class CategoriasScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._categorias: List[Dict] = []
        self._cat_font = QFont("Arial", 11, QFont.Weight.Bold)
        self._build_ui()
        self._mode = "categorias"   # estado de la botonera inferior
        self.refresh()

    # ---------- UI ----------
    def _build_ui(self):
        self.setObjectName("CategoriasScreen")
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # contenedor principal
        content = QFrame()
        content.setStyleSheet("""
            QFrame { background-color: #4A4A4A; border: 2px solid #5A5A5A; border-radius: 10px; }
        """)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

        # logo arriba
        icon_container = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setStyleSheet("""
            QLabel { background-color: #21AFBD; border-radius: 30px; border: 3px solid #FFFFFF; }
        """)
        try:
            base_dir = Path(__file__).resolve().parent.parent
            image_path = base_dir / "Lo de manoli.png"
            pix = QPixmap(str(image_path))
            if not pix.isNull():
                icon_label.setPixmap(pix.scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio,
                                                Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            print(f"[categorias] Error cargando 'Lo de manoli.png': {e}")

        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_container.addStretch(1)
        icon_container.addWidget(icon_label)
        icon_container.addStretch(1)
        content_layout.addLayout(icon_container)

        # panel interno con stack (vista grilla <-> vista tabla)
        inner_panel = QFrame()
        inner_panel.setStyleSheet("""
            QFrame { background-color: #2E2E2E; border: 2px solid #BFBFBF; border-radius: 10px; }
        """)
        inner_layout = QVBoxLayout(inner_panel)
        inner_layout.setContentsMargins(18, 18, 18, 18)
        inner_layout.setSpacing(12)

        self.stack = QStackedWidget()

        # --- vista grilla ---
        grid_wrapper = QWidget()
        grid_v = QVBoxLayout(grid_wrapper)
        grid_v.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.grid_host = QWidget()
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(16, 8, 16, 8)
        self.grid.setHorizontalSpacing(18)
        self.grid.setVerticalSpacing(16)

        self.scroll.setWidget(self.grid_host)
        grid_v.addWidget(self.scroll)
        self.stack.addWidget(grid_wrapper)

        inner_layout.addWidget(self.stack)
        content_layout.addWidget(inner_panel)

        # Botonera inferior
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(6, 0, 6, 0)
        bottom_row.addStretch(1)

        self.btn_agregar = QPushButton("AGREGAR CATEGORIA")
        self.btn_agregar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agregar.setFixedHeight(64)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71; color: #0B0B0B; border: 2px solid #27AE60;
                border-radius: 22px; font-weight: 700; font-size: 14px; padding: 8px 16px;
            }
            QPushButton:hover { background-color: #45D882; }
            QPushButton:pressed { background-color: #27AE60; }
        """)
        self.btn_agregar.clicked.connect(self._on_agregar)
        bottom_row.addWidget(self.btn_agregar)

        self.btn_eliminar = QPushButton("ELIMINAR CATEGORIA")
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.setFixedHeight(64)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; color: #0B0B0B; border: 2px solid #E94C4C;
                border-radius: 22px; font-weight: 700; font-size: 14px; padding: 8px 16px;
            }
            QPushButton:hover { background-color: #FF8383; }
            QPushButton:pressed { background-color: #E94C4C; }
        """)
        self.btn_eliminar.clicked.connect(self._on_eliminar)
        bottom_row.addSpacing(18)
        bottom_row.addWidget(self.btn_eliminar)
        bottom_row.addStretch(1)

        # Ensamble
        root.addWidget(content)
        root.addLayout(bottom_row)

        # tamaño inicial acorde al modo categorías
        self._resize_bottom_buttons(min_w=260, max_w=360, height=64)

    # ---------- datos ----------
    def _read_json(self) -> List[Dict]:
        try:
            if not JSON_CATEGORIAS.exists():
                return [{"id": None, "nombre": "SIN CATEGORÍA", "descripcion": "", "activa": True}]
            raw = json.loads(JSON_CATEGORIAS.read_text(encoding="utf-8"))
            src = raw.get("categorias") if isinstance(raw, dict) else raw
            items: List[Dict] = []
            if isinstance(src, list) and src and isinstance(src[0], dict):
                for it in src:
                    nombre = str(it.get("nombre", "")).strip()
                    if not nombre or not bool(it.get("activa", True)):
                        continue
                    items.append({
                        "id": it.get("id"),
                        "nombre": nombre,
                        "descripcion": str(it.get("descripcion", "")).strip(),
                        "activa": True
                    })
            elif isinstance(src, list):
                for s in src:
                    s = str(s).strip()
                    if s:
                        items.append({"id": None, "nombre": s, "descripcion": "", "activa": True})
            if not items:
                items = [{"id": None, "nombre": "SIN CATEGORÍA", "descripcion": "", "activa": True}]
            return items
        except Exception as e:
            print(f"[categorias] Error leyendo {JSON_CATEGORIAS}: {e}")
            return [{"id": None, "nombre": "SIN CATEGORÍA", "descripcion": "", "activa": True}]

    def refresh(self):
        self._categorias = self._read_json()
        self._rebuild_grid()

    # ---------- helpers de botonera ----------
    def _resize_bottom_buttons(self, min_w: int, max_w: int, height: int):
        def calc_w(btn: QPushButton) -> int:
            fm = QFontMetrics(btn.font())
            return max(min_w, min(fm.horizontalAdvance(btn.text()) + 48, max_w))
        self.btn_agregar.setFixedSize(calc_w(self.btn_agregar), height)
        self.btn_eliminar.setFixedSize(calc_w(self.btn_eliminar), height)

    def _set_bottom_mode(self, mode: str):
        self._mode = mode
        if mode == "productos":
            self.btn_agregar.setText("AGREGAR PRODUCTO A ESTA CATEGORÍA")
            self.btn_eliminar.setText("QUITAR PRODUCTO DE ESTA CATEGORÍA")
            self._resize_bottom_buttons(min_w=380, max_w=520, height=64)
        else:
            self.btn_agregar.setText("AGREGAR CATEGORIA")
            self.btn_eliminar.setText("ELIMINAR CATEGORIA")
            self._resize_bottom_buttons(min_w=260, max_w=360, height=64)

    # ---------- utilidades stock ----------
    def _read_stock(self) -> List[Dict]:
        try:
            if JSON_STOCK.exists():
                return json.loads(JSON_STOCK.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[categorias] Error leyendo {JSON_STOCK}: {e}")
        return []

    def _get_all_products_from_backend(self) -> List[Dict]:
        """Obtener todos los productos desde el backend"""
        try:
            from aplicacion.backend.stock import controller
            productos = controller.listar_productos_controller()
            return [{"id": p.id, "nombre": p.nombre, "categoria_id": p.categoria_id} for p in productos]
        except Exception as e:
            print(f"[categorias] Error obteniendo productos del backend: {e}")
            return []

    @staticmethod
    def _is_sin_categoria(cat: str | None) -> bool:
        if cat is None:
            return True
        s = str(cat).strip().lower()
        return (s == "") or (s == "sin_categoria")

    def _get_products_without_category(self) -> List[Dict]:
        """Obtener productos sin categoría o con categoría 'sin_categoria' desde el backend"""
        try:
            from aplicacion.backend.stock import controller
            productos = controller.listar_productos_controller()
            
            # Obtener categorías para encontrar el ID de "sin_categoria"
            categorias = controller.listar_clasificaciones_controller()
            sin_categoria_id = None
            for cat in categorias:
                if cat.nombre.lower().strip() in ["sin_categoria", "sin categoria", "sin categoría"]:
                    sin_categoria_id = cat.id
                    break
            
            return [
                {"id": p.id, "nombre": p.nombre} 
                for p in productos 
                if p.categoria_id is None or p.categoria_id == sin_categoria_id
            ]
        except Exception as e:
            print(f"[categorias] Error obteniendo productos sin categoría: {e}")
            return []

    def _get_products_in_category(self, categoria_id: int) -> List[Dict]:
        """Obtener productos de una categoría específica desde el backend"""
        try:
            from aplicacion.backend.stock import controller
            productos = controller.listar_productos_controller()
            return [
                {"id": p.id, "nombre": p.nombre} 
                for p in productos 
                if p.categoria_id == categoria_id
            ]
        except Exception as e:
            print(f"[categorias] Error obteniendo productos de categoría {categoria_id}: {e}")
            return []

    def _get_category_id_by_name(self, nombre: str) -> int:
        """Obtener ID de categoría por su nombre"""
        for cat in self._categorias:
            if cat.get("nombre") == nombre:
                return cat.get("id")
        return None

    # ---------- regeneración de JSONs ----------
    def _regenerate_jsons(self):
        """Regenerar ambos JSONs después de cambios en BD"""
        try:
            from aplicacion.backend.stock.crud import exportar_categorias_json, exportar_productos_json
            print("Regenerando JSONs...")
            
            # Regenerar categorías
            cat_ok = exportar_categorias_json()
            if cat_ok:
                print("JSON de categorías regenerado exitosamente")
            else:
                print("Error regenerando JSON de categorías")
            
            # Regenerar stock
            stock_ok = exportar_productos_json() 
            if stock_ok:
                print("JSON de stock regenerado exitosamente")
            else:
                print("Error regenerando JSON de stock")
                
            return cat_ok and stock_ok
            
        except Exception as e:
            print(f"Error regenerando JSONs: {e}")
            return False

    # ---------- grilla ----------
    def _rebuild_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        cols = 5
        btn_w, btn_h = 280, 72

        for idx, cat in enumerate(self._categorias):
            nombre = (cat.get("nombre") or "").upper()
            desc = cat.get("descripcion") or ""
            r, c = divmod(idx, cols)

            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumSize(btn_w, btn_h)
            btn.setMaximumSize(btn_w, btn_h)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setFont(self._cat_font)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2E65B3; color: #FFFFFF; border: 2px solid #244F8C;
                    border-radius: 14px; padding: 8px 10px; text-align: center;
                }
                QPushButton:hover { background-color: #3474CC; border-color: #2E65B3; }
                QPushButton:pressed { background-color: #244F8C; }
            """)

            max_px = btn_w - 22
            fm = QFontMetrics(self._cat_font)
            text_to_set = nombre
            f_for_button = QFont(self._cat_font)
            if fm.horizontalAdvance(nombre) > max_px:
                f_for_button.setPointSize(max(self._cat_font.pointSize() - 1, 9))
                fm2 = QFontMetrics(f_for_button)
                if fm2.horizontalAdvance(nombre) > max_px:
                    text_to_set = fm2.elidedText(nombre, Qt.TextElideMode.ElideRight, max_px)
                btn.setFont(f_for_button)
            btn.setText(text_to_set)

            btn.setToolTip(f"{cat.get('nombre')}\n\n{desc}" if desc else cat.get('nombre'))
            btn.clicked.connect(lambda _=False, data=cat: self._on_categoria_click(data))
            self.grid.addWidget(btn, r, c)

        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self._go_back_to_grid()  # mostrar grilla tras refrescar

    # ---------- acciones ----------
    def _on_categoria_click(self, cat: dict):
        nombre = cat.get("nombre", "")
        print(f"[categorias] Click en categoría: {nombre}")

        table_view = None
        for i in range(self.stack.count()):
            w = self.stack.widget(i)
            if isinstance(w, CategoryProductsTable):
                table_view = w
                break

        if table_view is None:
            table_view = CategoryProductsTable(nombre, parent=self)
            table_view.requestBack.connect(self._go_back_to_grid)
            self.stack.addWidget(table_view)
        else:
            table_view.set_category(nombre)

        self.stack.setCurrentWidget(table_view)
        self._set_bottom_mode("productos")
        # Guardar categoría actual para uso en botones
        self._current_category = cat

    def _go_back_to_grid(self):
        self.stack.setCurrentIndex(0)
        self._set_bottom_mode("categorias")
        self._current_category = None

    def _on_agregar(self):
        if getattr(self, "_mode", "categorias") == "productos":
            # Agregar producto a categoría actual
            current_cat = getattr(self, "_current_category", None)
            if not current_cat:
                QMessageBox.warning(self, "Error", "No se pudo determinar la categoría actual.")
                return
                
            categoria_id = current_cat.get("id")
            if categoria_id is None:
                QMessageBox.warning(self, "Error", "La categoría seleccionada no tiene ID válido.")
                return

            # Obtener productos sin categoría
            productos_sin_categoria = self._get_products_without_category()
            if not productos_sin_categoria:
                QMessageBox.information(
                    self, 
                    "Sin productos disponibles", 
                    "No hay productos sin categoría para agregar."
                )
                return

            # Mostrar diálogo para seleccionar producto
            dlg = ProductPickDialog(
                "Agregar producto a categoría",
                "Seleccionar producto:",
                productos_sin_categoria,
                self
            )
            
            if dlg.exec():
                producto_data = dlg.get_selected_product_data()
                producto_id = producto_data.get("id")
                producto_nombre = producto_data.get("nombre", "")
                
                if producto_id:
                    try:
                        # Llamar directamente al crud para asignar (evitar controller defectuoso)
                        from aplicacion.backend.stock.crud import asignar_producto_a_categoria
                        resultado = asignar_producto_a_categoria(producto_id, categoria_id)
                        
                        if resultado:
                            # Regenerar JSONs
                            if self._regenerate_jsons():
                                # Refrescar vista
                                table_view = self.stack.currentWidget()
                                if isinstance(table_view, CategoryProductsTable):
                                    table_view._load_products_data()
                                    table_view._apply_category_filter()
                                
                                QMessageBox.information(
                                    self,
                                    "Producto agregado",
                                    f"El producto '{producto_nombre}' se agregó exitosamente a la categoría '{current_cat.get('nombre')}'."
                                )
                            else:
                                QMessageBox.warning(
                                    self, 
                                    "Advertencia", 
                                    "Producto agregado pero hubo problemas regenerando los archivos JSON."
                                )
                        else:
                            QMessageBox.warning(self, "Error", "No se pudo agregar el producto a la categoría.")
                            
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Error al agregar producto: {e}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo obtener el ID del producto seleccionado.")
            
            return

        # MODO grilla: agregar categoría
        dlg = AddCategoryDialog(self)
        if dlg.exec():
            data = dlg.get_category_data()
            nombre = data.get("nombre", "").strip()
            descripcion = data.get("descripcion", "").strip()
            
            if not nombre:
                QMessageBox.warning(self, "Error", "El nombre de la categoría no puede estar vacío.")
                return
            
            # Verificar que no existe una categoría con el mismo nombre
            for cat in self._categorias:
                if cat.get("nombre", "").strip().lower() == nombre.lower():
                    QMessageBox.warning(
                        self, 
                        "Categoría duplicada", 
                        f"Ya existe una categoría con el nombre '{nombre}'."
                    )
                    return
            
            try:
                # Llamar al controller para crear
                from aplicacion.backend.stock import controller
                nueva_categoria = controller.agregar_clasificacion_controller({
                    "nombre": nombre,
                    "descripcion": descripcion,
                    "activa": True
                })
                
                if nueva_categoria:
                    # Regenerar JSONs
                    if self._regenerate_jsons():
                        # Refrescar vista
                        self.refresh()
                        QMessageBox.information(
                            self, 
                            "Categoría creada", 
                            f"La categoría '{nombre}' se creó exitosamente con ID {nueva_categoria.id}."
                        )
                    else:
                        QMessageBox.warning(
                            self, 
                            "Advertencia", 
                            "Categoría creada pero hubo problemas regenerando los archivos JSON."
                        )
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear la categoría.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear categoría: {e}")

    def _on_eliminar(self):
        if getattr(self, "_mode", "categorias") == "productos":
            # Quitar producto de categoría actual
            current_cat = getattr(self, "_current_category", None)
            if not current_cat:
                QMessageBox.warning(self, "Error", "No se pudo determinar la categoría actual.")
                return
                
            categoria_id = current_cat.get("id")
            if categoria_id is None:
                QMessageBox.warning(self, "Error", "La categoría seleccionada no tiene ID válido.")
                return

            # Obtener productos de esta categoría
            productos_categoria = self._get_products_in_category(categoria_id)
            if not productos_categoria:
                QMessageBox.information(
                    self,
                    "Sin productos",
                    f"La categoría '{current_cat.get('nombre')}' no tiene productos asignados."
                )
                return

            # Mostrar diálogo para seleccionar producto a quitar
            dlg = ProductPickDialog(
                "Quitar producto de categoría",
                "Seleccionar producto:",
                productos_categoria,
                self
            )
            
            if dlg.exec():
                producto_data = dlg.get_selected_product_data()
                producto_id = producto_data.get("id")
                producto_nombre = producto_data.get("nombre", "")
                
                if producto_id:
                    # Confirmar acción
                    reply = QMessageBox.question(
                        self,
                        "Confirmar acción",
                        f"¿Estás seguro de que deseas quitar el producto '{producto_nombre}' de la categoría '{current_cat.get('nombre')}'?\n\nEl producto quedará sin categoría asignada.",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.Yes:
                        try:
                            # Llamar directamente al crud para quitar categoría (evitar controller defectuoso)
                            from aplicacion.backend.stock.crud import quitar_categoria_a_producto
                            resultado = quitar_categoria_a_producto(producto_id)
                            
                            if resultado:
                                # Regenerar JSONs
                                if self._regenerate_jsons():
                                    # Refrescar vista
                                    table_view = self.stack.currentWidget()
                                    if isinstance(table_view, CategoryProductsTable):
                                        table_view._load_products_data()
                                        table_view._apply_category_filter()
                                    
                                    QMessageBox.information(
                                        self,
                                        "Producto removido",
                                        f"El producto '{producto_nombre}' se quitó exitosamente de la categoría '{current_cat.get('nombre')}'."
                                    )
                                else:
                                    QMessageBox.warning(
                                        self, 
                                        "Advertencia", 
                                        "Producto removido pero hubo problemas regenerando los archivos JSON."
                                    )
                            else:
                                QMessageBox.warning(self, "Error", "No se pudo quitar el producto de la categoría.")
                                
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Error al quitar producto: {e}")
                else:
                    QMessageBox.warning(self, "Error", "No se pudo obtener el ID del producto seleccionado.")
            
            return

        # MODO grilla: eliminar categoría
        if not self._categorias:
            QMessageBox.information(self, "Sin categorías", "No hay categorías para eliminar.")
            return

        dlg = RemoveCategoryDialog(self._categorias, self)
        if dlg.exec():
            categoria_data = dlg.get_selected_category_data()
            categoria_id = categoria_data.get("id")
            categoria_nombre = categoria_data.get("nombre", "")
            
            if categoria_id is None:
                QMessageBox.warning(self, "Error", "La categoría seleccionada no tiene ID válido.")
                return
            
            # Verificar si hay productos asignados a esta categoría
            productos_asignados = self._get_products_in_category(categoria_id)
            if productos_asignados:
                reply = QMessageBox.question(
                    self,
                    "Categoría con productos",
                    f"La categoría '{categoria_nombre}' tiene {len(productos_asignados)} productos asignados.\n\n¿Deseas continuar? Los productos quedarán sin categoría.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Confirmar eliminación
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Estás seguro de que deseas eliminar la categoría '{categoria_nombre}'?\n\nEsta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # Primero quitar la categoría de todos los productos asignados
                    from aplicacion.backend.stock.crud import quitar_categoria_a_producto
                    for producto in productos_asignados:
                        quitar_categoria_a_producto(producto["id"])
                    
                    # Luego eliminar la categoría
                    from aplicacion.backend.stock.crud import eliminar_clasificacion
                    resultado = eliminar_clasificacion(categoria_id)
                    
                    if resultado:
                        # Regenerar JSONs
                        if self._regenerate_jsons():
                            # Refrescar vista
                            self.refresh()
                            QMessageBox.information(
                                self,
                                "Categoría eliminada",
                                f"La categoría '{categoria_nombre}' se eliminó exitosamente."
                            )
                        else:
                            QMessageBox.warning(
                                self, 
                                "Advertencia", 
                                "Categoría eliminada pero hubo problemas regenerando los archivos JSON."
                            )
                    else:
                        QMessageBox.warning(self, "Error", "No se pudo eliminar la categoría.")
                        
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al eliminar categoría: {e}")