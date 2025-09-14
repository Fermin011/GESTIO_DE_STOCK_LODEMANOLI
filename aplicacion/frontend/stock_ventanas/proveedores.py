# aplicacion/frontend/stock_ventanas/proveedores.py
from __future__ import annotations

from pathlib import Path
import json
from typing import List, Dict, Iterable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QPushButton, QSpacerItem, QDialog, QGridLayout, QMessageBox
)

THIS_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = THIS_DIR.parent
JSON_PROVEEDORES = FRONTEND_DIR / "json" / "proveedores.json"


def _css_lineedit_black() -> str:
    return """
        QLineEdit {
            color: black; background-color: white;
            border: 2px solid #6A6A6A; border-radius: 14px;
            padding: 6px 10px; font-size: 14px;
        }
        QLineEdit:focus { border: 2px solid #21AFBD; }
    """


# =========================
# Form de Alta/Edición (solo UI)
# =========================
class ProveedorFormDialog(QDialog):
    def __init__(self, mode: str = "AGREGAR", data: Optional[Dict] = None, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle(f"{mode.capitalize()} proveedor")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._mode = mode.upper()
        self._build_ui()
        if data:
            self._set_form(data)

    def _build_ui(self):
        self.setMinimumSize(560, 520)

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

        title = QLabel(
            "AGREGAR PROVEEDOR" if self._mode == "AGREGAR" else "EDITAR PROVEEDOR"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #2ECC71; font-weight: 900; font-size: 20px;")
        cont_lyt.addWidget(title)

        card = QFrame()
        card.setStyleSheet("""
            QFrame { background-color: #FFFFFF; border: 2px solid #CFCFCF; border-radius: 16px; }
        """)
        grid = QGridLayout(card)
        grid.setContentsMargins(24, 24, 24, 24)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(18)

        def add_row(row: int, label: str, edit: QLineEdit):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #2b2b2b; font-size: 16px;")
            grid.addWidget(lbl, row, 0)
            edit.setFixedHeight(36)
            edit.setStyleSheet(_css_lineedit_black())
            grid.addWidget(edit, row, 1)

        self.ed_nombre = QLineEdit()
        self.ed_telefono = QLineEdit()
        self.ed_email = QLineEdit()
        self.ed_direccion = QLineEdit()
        self.ed_contacto = QLineEdit()

        add_row(0, "Nombre:", self.ed_nombre)
        add_row(1, "Teléfono:", self.ed_telefono)
        add_row(2, "E-Mail:", self.ed_email)
        add_row(3, "Dirección:", self.ed_direccion)
        add_row(4, "Contacto:", self.ed_contacto)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)

        cont_lyt.addWidget(card, 1)

        # Botones
        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        btn_cancel = QPushButton("CANCELAR")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedSize(220, 56)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; color: #0B0B0B; border: 2px solid #E94C4C;
                border-radius: 26px; font-weight: 800;
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
                border-radius: 26px; font-weight: 800;
            }
            QPushButton:hover { background-color: #45D882; }
            QPushButton:pressed { background-color: #27AE60; }
        """)
        btn_ok.clicked.connect(self.accept)
        btns.addWidget(btn_ok)

        btns.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        cont_lyt.addLayout(btns)

        root.addWidget(container)

    def _set_form(self, r: Dict):
        self.ed_nombre.setText(str(r.get("nombre", "")))
        self.ed_telefono.setText(str(r.get("telefono", "")))
        self.ed_email.setText(str(r.get("email", "")))
        self.ed_direccion.setText(str(r.get("direccion", "")))
        self.ed_contacto.setText(str(r.get("contacto", "")))

    def get_data(self) -> Dict:
        return {
            "nombre": self.ed_nombre.text().strip(),
            "telefono": self.ed_telefono.text().strip(),
            "email": self.ed_email.text().strip(),
            "direccion": self.ed_direccion.text().strip(),
            "contacto": self.ed_contacto.text().strip(),
        }

    def is_data_valid(self) -> bool:
        """Valida que al menos el nombre no esté vacío"""
        return bool(self.ed_nombre.text().strip())


# =========================
# Pantalla principal
# =========================
class ProveedoresScreen(QWidget):
    """
    Pantalla de Proveedores con lógica backend implementada:
      - Carga datos desde proveedores.json generado por el backend
      - CRUD completo integrado con controller y crud
      - Regeneración automática de JSON tras cada operación
      - Actualización automática de la UI
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[Dict] = []
        self._build_ui()
        self.refresh()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        outer = QFrame()
        outer.setStyleSheet("""
            QFrame { background-color: #4A4A4A; border: 2px solid #5A5A5A; border-radius: 10px; }
        """)
        outer_l = QVBoxLayout(outer)
        outer_l.setContentsMargins(30, 30, 30, 30)
        outer_l.setSpacing(18)

        # Logo
        icon_row = QHBoxLayout()
        icon = QLabel()
        icon.setFixedSize(60, 60)
        icon.setStyleSheet("""
            QLabel { background-color: #21AFBD; border-radius: 30px; border: 3px solid #FFFFFF; }
        """)
        try:
            base_dir = Path(__file__).resolve().parent.parent
            image_path = base_dir / "Lo de manoli.png"
            pix = QPixmap(str(image_path))
            if not pix.isNull():
                icon.setPixmap(pix.scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
        except Exception as e:
            print(f"[proveedores] Error cargando 'Lo de manoli.png': {e}")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_row.addStretch(1)
        icon_row.addWidget(icon)
        icon_row.addStretch(1)
        outer_l.addLayout(icon_row)

        # Panel interno
        inner = QFrame()
        inner.setStyleSheet("""
            QFrame { background-color: #2E2E2E; border: 2px solid #BFBFBF; border-radius: 10px; }
        """)
        inner_l = QVBoxLayout(inner)
        inner_l.setContentsMargins(16, 16, 16, 16)
        inner_l.setSpacing(10)

        # Cabecera: buscador
        header = QHBoxLayout()
        header.setSpacing(12)

        lbl_buscar = QLabel("Buscar:")
        lbl_buscar.setStyleSheet("color: white; font-weight: bold;")
        self.search = QLineEdit()
        self.search.setPlaceholderText("buscar por nombre…")
        self.search.setFixedHeight(32)
        self.search.setStyleSheet(_css_lineedit_black())
        self.search.textChanged.connect(self._apply_filter)

        header.addWidget(lbl_buscar)
        header.addWidget(self.search, 1)
        header.addSpacerItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        inner_l.addLayout(header)

        # Tabla
        self.table = QTableWidget()
        self._setup_table()
        inner_l.addWidget(self.table)

        outer_l.addWidget(inner)
        root.addWidget(outer)

        # Botonera
        bottom = QHBoxLayout()
        bottom.setContentsMargins(6, 0, 6, 0)
        bottom.addStretch(1)

        self.btn_add = QPushButton("AGREGAR")
        self.btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add.setFixedHeight(56)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71; color: #0B0B0B; border: 2px solid #27AE60;
                border-radius: 22px; font-weight: 700; font-size: 14px; padding: 8px 18px;
            }
            QPushButton:hover { background-color: #45D882; }
            QPushButton:pressed { background-color: #27AE60; }
        """)
        self.btn_add.clicked.connect(self._on_add)

        self.btn_edit = QPushButton("EDITAR")
        self.btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_edit.setFixedHeight(56)
        self.btn_edit.setStyleSheet("""
            QPushButton {
                background-color: #3B73C8; color: #FFFFFF; border: 2px solid #2D59A0;
                border-radius: 22px; font-weight: 700; font-size: 14px; padding: 8px 18px;
            }
            QPushButton:hover { background-color: #4A86E0; }
            QPushButton:pressed { background-color: #2D59A0; }
        """)
        self.btn_edit.clicked.connect(self._on_edit)

        self.btn_del = QPushButton("ELIMINAR")
        self.btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_del.setFixedHeight(56)
        self.btn_del.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; color: #0B0B0B; border: 2px solid #E94C4C;
                border-radius: 22px; font-weight: 700; font-size: 14px; padding: 8px 18px;
            }
            QPushButton:hover { background-color: #FF8383; }
            QPushButton:pressed { background-color: #E94C4C; }
        """)
        self.btn_del.clicked.connect(self._on_delete)

        bottom.addWidget(self.btn_add)
        bottom.addSpacing(18)
        bottom.addWidget(self.btn_edit)
        bottom.addSpacing(18)
        bottom.addWidget(self.btn_del)
        bottom.addStretch(1)

        root.addLayout(bottom)

    def _setup_table(self):
        headers = ["NOMBRE", "TELÉFONO", "E-MAIL", "DIRECCIÓN", "CONTACTO"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white; border: 1px solid #CCCCCC;
                border-radius: 6px; gridline-color: #DDDDDD; font-size: 13px;
                selection-background-color: #E3F2FD; color: black;
            }
            QTableWidget::item { padding: 6px; border-bottom: 1px solid #EEEEEE; color: black; }
            QTableWidget::item:selected { background-color: #E3F2FD; color: black; }
            QHeaderView::section {
                background-color: #F5F5F5; padding: 8px; border: 1px solid #DDDDDD;
                font-weight: bold; color: black;
            }
        """)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        header = self.table.horizontalHeader()

        # Fijas mínimas
        self.table.setColumnWidth(1, 140)  # teléfono
        self.table.setColumnWidth(4, 140)  # contacto
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        # Estas ocupan el resto del ancho
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # e-mail
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # dirección

    # ---------- Data ----------
    def _load_from_json(self):
        """Cargar datos desde proveedores.json generado por el backend"""
        try:
            if JSON_PROVEEDORES.exists():
                raw = json.loads(JSON_PROVEEDORES.read_text(encoding="utf-8"))
                # Manejar tanto formato {proveedores: []} como []
                data = raw.get("proveedores") if isinstance(raw, dict) else raw
                if isinstance(data, list):
                    # Filtrar "sin_proveedores" del frontend
                    filtered_data = []
                    for r in data:
                        nombre = str(r.get("nombre", "")).strip().lower()
                        if nombre not in ["sin_proveedor", "sin proveedor", "sin proveedores"]:
                            filtered_data.append(self._normalize_row(r))
                    
                    self._rows = filtered_data
                    print(f"[proveedores] Cargados {len(self._rows)} proveedores desde JSON (sin_proveedores filtrado)")
                else:
                    print("[proveedores] Formato de JSON inválido")
                    self._rows = []
            else:
                print(f"[proveedores] No existe {JSON_PROVEEDORES}")
                self._rows = []
        except Exception as e:
            print(f"[proveedores] Error leyendo {JSON_PROVEEDORES}: {e}")
            self._rows = []

    @staticmethod
    def _normalize_row(r: Dict) -> Dict:
        """Normaliza un registro de proveedor desde JSON"""
        return {
            "id": r.get("id"),  # Mantener ID para operaciones backend
            "nombre": str(r.get("nombre", "")).strip(),
            "telefono": str(r.get("telefono", "")).strip(),
            "email": str(r.get("email", "") or r.get("e-mail", "")).strip(),
            "direccion": str(r.get("direccion", "")).strip(),
            "contacto": str(r.get("contacto", "")).strip(),
        }

    def refresh(self):
        """Recargar datos desde JSON y actualizar la tabla"""
        self._load_from_json()
        self._apply_filter()

    # ---------- Backend Integration ----------
    def _regenerate_json(self) -> bool:
        """Regenerar el JSON de proveedores después de cambios en BD"""
        try:
            from aplicacion.backend.stock.crud import exportar_proveedores_json
            print("Regenerando JSON de proveedores...")
            
            ok = exportar_proveedores_json()
            if ok:
                print("JSON de proveedores regenerado exitosamente")
                return True
            else:
                print("Error regenerando JSON de proveedores")
                return False
                
        except Exception as e:
            print(f"Error regenerando JSON de proveedores: {e}")
            return False

    def _get_provider_id_by_data(self, row_data: Dict) -> Optional[int]:
        """Obtener ID del proveedor desde los datos de la fila seleccionada"""
        nombre = row_data.get("nombre", "").strip()
        
        # Buscar en los datos cargados
        for row in self._rows:
            if (row.get("nombre", "").strip() == nombre and
                row.get("telefono", "").strip() == row_data.get("telefono", "").strip() and
                row.get("email", "").strip() == row_data.get("email", "").strip()):
                return row.get("id")
        
        return None

    # ---------- Filtro y pintado ----------
    def _apply_filter(self):
        text = (self.search.text() or "").strip().lower()
        if not text:
            filtered = self._rows
        else:
            def match(r: Dict) -> bool:
                return any(text in str(r.get(k, "")).lower()
                           for k in ("nombre", "telefono", "email", "direccion", "contacto"))
            filtered = [r for r in self._rows if match(r)]
        self._load_table(filtered)

    def _load_table(self, rows: List[Dict]):
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            def add(col: int, value: str, align=Qt.AlignmentFlag.AlignLeft):
                item = QTableWidgetItem(value)
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                item.setForeground(Qt.GlobalColor.black)
                self.table.setItem(i, col, item)

            add(0, r.get("nombre", ""), Qt.AlignmentFlag.AlignLeft)
            add(1, r.get("telefono", ""), Qt.AlignmentFlag.AlignCenter)
            add(2, r.get("email", ""), Qt.AlignmentFlag.AlignLeft)
            add(3, r.get("direccion", ""), Qt.AlignmentFlag.AlignLeft)
            add(4, r.get("contacto", ""), Qt.AlignmentFlag.AlignCenter)

    # ---------- Helpers selección ----------
    def _selected_row_as_dict(self) -> Optional[Dict]:
        row = self.table.currentRow()
        if row < 0:
            return None
        return {
            "nombre": self.table.item(row, 0).text() if self.table.item(row, 0) else "",
            "telefono": self.table.item(row, 1).text() if self.table.item(row, 1) else "",
            "email": self.table.item(row, 2).text() if self.table.item(row, 2) else "",
            "direccion": self.table.item(row, 3).text() if self.table.item(row, 3) else "",
            "contacto": self.table.item(row, 4).text() if self.table.item(row, 4) else "",
        }

    # ---------- Acciones con Backend ----------
    def _on_add(self):
        """Agregar nuevo proveedor usando el backend"""
        dlg = ProveedorFormDialog("AGREGAR", parent=self)
        if dlg.exec():
            if not dlg.is_data_valid():
                QMessageBox.warning(
                    self,
                    "Datos incompletos",
                    "El nombre del proveedor no puede estar vacío."
                )
                return
            
            data = dlg.get_data()
            nombre = data.get("nombre", "").strip()
            
            # Verificar que no existe un proveedor con el mismo nombre
            # También verificar que no intente crear "sin_proveedores"
            nombre_lower = nombre.lower()
            if nombre_lower in ["sin_proveedores", "sin proveedores", "sin proveedor"]:
                QMessageBox.warning(
                    self,
                    "Nombre no permitido",
                    "No se puede crear un proveedor con el nombre 'sin_proveedores' ya que es un valor reservado del sistema."
                )
                return
            
            for row in self._rows:
                if row.get("nombre", "").strip().lower() == nombre_lower:
                    QMessageBox.warning(
                        self,
                        "Proveedor duplicado",
                        f"Ya existe un proveedor con el nombre '{nombre}'."
                    )
                    return
            
            try:
                # Llamar al controller para crear
                from aplicacion.backend.stock import controller
                nuevo_proveedor = controller.agregar_proveedor_controller(data)
                
                if nuevo_proveedor:
                    # Regenerar JSON
                    if self._regenerate_json():
                        # Refrescar vista
                        self.refresh()
                        QMessageBox.information(
                            self,
                            "Proveedor creado",
                            f"El proveedor '{nombre}' se creó exitosamente con ID {nuevo_proveedor.id}."
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "Proveedor creado pero hubo problemas regenerando el archivo JSON."
                        )
                else:
                    QMessageBox.warning(self, "Error", "No se pudo crear el proveedor.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al crear proveedor: {e}")
        else:
            print("[proveedores] Alta cancelada")

    def _on_edit(self):
        """Editar proveedor seleccionado usando el backend"""
        row_data = self._selected_row_as_dict()
        if not row_data:
            QMessageBox.information(self, "Editar proveedor", "Selecciona un proveedor de la tabla.")
            return
        
        proveedor_id = self._get_provider_id_by_data(row_data)
        if proveedor_id is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID del proveedor seleccionado.")
            return
        
        dlg = ProveedorFormDialog("EDITAR", row_data, parent=self)
        if dlg.exec():
            if not dlg.is_data_valid():
                QMessageBox.warning(
                    self,
                    "Datos incompletos",
                    "El nombre del proveedor no puede estar vacío."
                )
                return
            
            new_data = dlg.get_data()
            nuevo_nombre = new_data.get("nombre", "").strip()
            
            # Verificar que no existe otro proveedor con el mismo nombre (excepto el actual)
            for row in self._rows:
                if (row.get("id") != proveedor_id and 
                    row.get("nombre", "").strip().lower() == nuevo_nombre.lower()):
                    QMessageBox.warning(
                        self,
                        "Nombre duplicado",
                        f"Ya existe otro proveedor con el nombre '{nuevo_nombre}'."
                    )
                    return
            
            try:
                # Llamar directamente al crud para actualizar
                from aplicacion.backend.stock.crud import actualizar_proveedor
                resultado = actualizar_proveedor(proveedor_id, new_data)
                
                if resultado:
                    # Regenerar JSON
                    if self._regenerate_json():
                        # Refrescar vista
                        self.refresh()
                        QMessageBox.information(
                            self,
                            "Proveedor actualizado",
                            f"El proveedor se actualizó exitosamente."
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "Proveedor actualizado pero hubo problemas regenerando el archivo JSON."
                        )
                else:
                    QMessageBox.warning(self, "Error", "No se pudo actualizar el proveedor.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar proveedor: {e}")
        else:
            print("[proveedores] Edición cancelada")

    def _on_delete(self):
        """Eliminar proveedor seleccionado usando el backend"""
        row_data = self._selected_row_as_dict()
        if not row_data:
            QMessageBox.information(self, "Eliminar proveedor", "Selecciona un proveedor de la tabla.")
            return
        
        proveedor_id = self._get_provider_id_by_data(row_data)
        if proveedor_id is None:
            QMessageBox.warning(self, "Error", "No se pudo obtener el ID del proveedor seleccionado.")
            return
        
        nombre = row_data.get("nombre", "este proveedor")
        
        # Verificar si hay productos asignados a este proveedor
        try:
            from aplicacion.backend.stock import controller
            productos = controller.listar_productos_controller()
            productos_asignados = [p for p in productos if p.proveedor_id == proveedor_id]
            
            if productos_asignados:
                reply = QMessageBox.question(
                    self,
                    "Proveedor con productos",
                    f"El proveedor '{nombre}' tiene {len(productos_asignados)} productos asignados.\n\n¿Deseas continuar? Los productos quedarán sin proveedor asignado.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
        except Exception as e:
            print(f"Error verificando productos del proveedor: {e}")
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar el proveedor '{nombre}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Llamar directamente al crud para eliminar
                from aplicacion.backend.stock.crud import eliminar_proveedor
                resultado = eliminar_proveedor(proveedor_id)
                
                if resultado:
                    # Regenerar JSON
                    if self._regenerate_json():
                        # Refrescar vista
                        self.refresh()
                        QMessageBox.information(
                            self,
                            "Proveedor eliminado",
                            f"El proveedor '{nombre}' se eliminó exitosamente."
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Advertencia",
                            "Proveedor eliminado pero hubo problemas regenerando el archivo JSON."
                        )
                else:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el proveedor.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar proveedor: {e}")
        else:
            print("[proveedores] Eliminación cancelada")