# aplicacion/frontend/stock_ventanas/vencimientos.py
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Iterable

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QSpacerItem, QProgressDialog, QApplication, QMessageBox
)

BASE_DIR = Path(__file__).resolve().parent.parent  # .../frontend
ICON_IMG = BASE_DIR / "stock_ventanas" / "Lo de manoli.png"

COLOR_RED = "#E53935"
COLOR_RED_HOVER = "#EF5350"
COLOR_GREEN = "#4CAF50"
COLOR_ORANGE = "#FF9800"

def _css_lineedit_black() -> str:
    return """
        QLineEdit {
            background: #1E1E1E;
            color: white;
            border: 1px solid #BFBFBF;
            border-radius: 6px;
            padding: 6px 8px;
        }
        QLineEdit:focus {
            border: 1px solid #21AFBD;
        }
    """

def _css_combo_black() -> str:
    return """
        QComboBox {
            background: #1E1E1E;
            color: white;
            border: 1px solid #BFBFBF;
            border-radius: 6px;
            padding: 4px 6px;
        }
        QComboBox::drop-down {
            border: none;
        }
    """

def _table_header_stylesheet() -> str:
    return """
        QHeaderView::section {
            background-color: #E0E0E0;
            color: #333333;
            padding: 6px 8px;
            border: 0px;
            border-right: 1px solid #CCCCCC;
            font-weight: bold;
        }
    """

def _estado_cell_widget(texto: str) -> QWidget:
    """
    Crea el widget de la celda ESTADO:
    • puntito de color + texto en negro
    • rojo si VENCIDO, naranja si POR VENCER
    • sin recuadros negros (fondos transparentes)
    """
    estado = (texto or "").strip().upper()
    is_vencido = (estado == "VENCIDO")
    color = COLOR_RED if is_vencido else COLOR_ORANGE
    label_text = "VENCIDO" if is_vencido else "POR VENCER"

    w = QWidget()
    w.setStyleSheet("background: transparent;")
    lay = QHBoxLayout(w)
    lay.setContentsMargins(6, 2, 6, 2)
    lay.setSpacing(6)

    dot = QFrame()
    dot.setFixedSize(12, 12)
    dot.setStyleSheet(f"border-radius: 6px; background-color: {color};")

    lbl = QLabel(label_text)
    lbl.setStyleSheet("color: black; background: transparent; border: none;")

    lay.addWidget(dot, 0, Qt.AlignmentFlag.AlignVCenter)
    lay.addWidget(lbl, 0, Qt.AlignmentFlag.AlignVCenter)
    lay.addStretch(1)
    return w


class DataLoader(QThread):
    """Thread para cargar datos de vencimientos sin bloquear la UI"""
    data_loaded = pyqtSignal(list, dict)  # datos, estadísticas
    error_occurred = pyqtSignal(str)

    def run(self):
        """
        - Trae unidades vencidas y por vencer (crud) ya formateadas como diccionarios
        - Combina los datos y calcula estadísticas
        - Devuelve filas "listas para pintar" y estadísticas
        """
        try:
            print("[vencimientos] Cargando datos desde BD...")

            # Obtener datos ya formateados desde crud
            from aplicacion.backend.stock.crud import obtener_unidades_vencidas, obtener_unidades_por_vencer

            vencidas = obtener_unidades_vencidas()
            por_vencer = obtener_unidades_por_vencer()

            # Combinar todos los datos
            datos = vencidas + por_vencer

            # Orden básico: vencidos primero, luego por vencer por fecha
            def _sort_key(r: dict):
                estado_rank = 0 if r["estado"] == "VENCIDO" else 1
                # fecha para ordenar (vacío al final)
                fv = r["fecha_venc"]
                return (estado_rank, fv if fv else "9999-12-31", r["nombre"].lower())

            datos.sort(key=_sort_key)

            # Estadísticas
            total = len(datos)
            cant_vencidos = len(vencidas)
            cant_por_vencer = len(por_vencer)

            stats = {
                "total": total,
                "vencidos": cant_vencidos,
                "por_vencer": cant_por_vencer,
            }

            self.data_loaded.emit(datos, stats)

        except Exception as e:
            self.error_occurred.emit(str(e))


class VencimientosScreen(QWidget):
    """
    Pantalla de VENCIMIENTOS con integración completa al backend:
    - Carga datos desde consultas SQL optimizadas
    - Barra de progreso durante la carga
    - Cache local de datos para filtros rápidos
    - Refresh automático al abrir
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_rows: List[Dict] = []
        self._filtered_rows: List[Dict] = []
        self._categories: List[str] = ["Todas.."]
        self._loading = False
        self._data_loader = None
        self._progress_dialog = None

        self._build_ui()

        # Timer para refresh automático cuando se muestre la ventana
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._load_data)
        self._refresh_timer.setSingleShot(True)

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        # Marco principal
        outer = QFrame()
        outer.setStyleSheet("""
            QFrame { background-color: #4A4A4A; border: 2px solid #5A5A5A; border-radius: 10px; }
        """)
        outer_l = QVBoxLayout(outer)
        outer_l.setContentsMargins(30, 30, 30, 30)
        outer_l.setSpacing(18)

        # Logo arriba
        icon_row = QHBoxLayout()
        icon_row.setContentsMargins(0, 0, 0, 0)
        icon_row.setSpacing(8)
        icon = QLabel()
        pix = QPixmap(str(ICON_IMG))
        if not pix.isNull():
            icon.setPixmap(pix.scaledToHeight(60, Qt.TransformationMode.SmoothTransformation))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_row.addStretch(1)
        icon_row.addWidget(icon)
        icon_row.addStretch(1)
        outer_l.addLayout(icon_row)

        # Contenedor interno
        inner = QFrame()
        inner.setStyleSheet("""
            QFrame { background-color: #2E2E2E; border: 2px solid #BFBFBF; border-radius: 10px; }
        """)
        inner_l = QVBoxLayout(inner)
        inner_l.setContentsMargins(16, 16, 16, 16)
        inner_l.setSpacing(10)

        # Cabecera: buscador + filtro + botón refresh
        header = QHBoxLayout()
        header.setSpacing(12)

        lbl_buscar = QLabel("Buscar:")
        lbl_buscar.setStyleSheet("color: white; font-weight: bold;")
        self.search = QLineEdit()
        self.search.setPlaceholderText("buscar por nombre o código de barras…")
        self.search.setFixedHeight(32)
        self.search.setStyleSheet(_css_lineedit_black())
        self.search.textChanged.connect(self._apply_filters)

        header.addWidget(lbl_buscar)
        header.addWidget(self.search, 1)

        header.addSpacerItem(QSpacerItem(30, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        lbl_mostrar = QLabel("MOSTRAR:")
        lbl_mostrar.setStyleSheet("color: white; font-weight: bold;")
        self.combo_categoria = QComboBox()
        self.combo_categoria.setStyleSheet(_css_combo_black())
        self.combo_categoria.setFixedHeight(32)
        self.combo_categoria.currentIndexChanged.connect(self._apply_filters)

        # Botón de refresh
        self.btn_refresh = QLabel("🔄")
        self.btn_refresh.setStyleSheet("""
            QLabel {
                background-color: #21AFBD; color: white; 
                border-radius: 15px; padding: 8px;
                font-size: 16px; font-weight: bold;
            }
            QLabel:hover { background-color: #25BCD0; }
        """)
        self.btn_refresh.setFixedSize(32, 32)
        self.btn_refresh.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.mousePressEvent = lambda event: self._on_refresh_clicked()

        # Botón de limpiar vencidos
        self.btn_clean = QLabel("🧹")
        self.btn_clean.setStyleSheet(f"""
            QLabel {{
                background-color: {COLOR_RED}; color: white;
                border-radius: 15px; padding: 8px;
                font-size: 16px; font-weight: bold;
            }}
            QLabel:hover {{ background-color: {COLOR_RED_HOVER}; }}
        """)
        self.btn_clean.setFixedSize(32, 32)
        self.btn_clean.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clean.mousePressEvent = lambda event: self._on_clean_clicked()

        header.addWidget(lbl_mostrar)
        header.addWidget(self.combo_categoria)
        header.addSpacing(10)
        header.addWidget(self.btn_refresh)
        header.addSpacing(8)
        header.addWidget(self.btn_clean)

        inner_l.addLayout(header)

        # Tabla
        self.table = QTableWidget()
        self._setup_table()
        inner_l.addWidget(self.table)

        # Notificaciones al pie
        notif_box = QFrame()
        notif_box.setStyleSheet("""
            QFrame {
                background-color: white; border: 2px solid #CFCFCF; border-radius: 10px;
            }
        """)
        notif_l = QVBoxLayout(notif_box)
        notif_l.setContentsMargins(14, 12, 14, 12)

        self.notif_title = QLabel("Resumen")
        self.notif_title.setStyleSheet("color: black; font-size: 16px; font-weight: bold;")

        self.notif_lines = QLabel("")
        self.notif_lines.setStyleSheet("color: black;")
        self.notif_lines.setWordWrap(True)

        notif_l.addWidget(self.notif_title)
        notif_l.addWidget(self.notif_lines)
        inner_l.addWidget(notif_box)

        outer_l.addWidget(inner)
        root.addWidget(outer)

    def _setup_table(self):
        headers = ["CÓDIGO", "NOMBRE", "CATEGORÍA", "FECHA VENC.", "DÍAS RESTAN.", "ESTADO"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #CFCFCF;
                border-radius: 6px;
            }
            QTableWidget::item {
                color: black;  /* <- fuerza texto negro siempre */
                selection-background-color: #CDEEF2;
                selection-color: black;
            }
        """)
        hh = self.table.horizontalHeader()
        hh.setStyleSheet(_table_header_stylesheet())
        hh.setHighlightSections(False)
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Anchos
        self.table.setColumnWidth(0, 130)  # código
        self.table.setColumnWidth(1, 320)  # nombre
        self.table.setColumnWidth(2, 180)  # categoría
        self.table.setColumnWidth(3, 130)  # fecha
        self.table.setColumnWidth(4, 120)  # días
        # col 5 (estado) se estira

    # ---------- Eventos ----------
    def showEvent(self, event):
        super().showEvent(event)
        # Refresh automático al mostrar la ventana
        if not self._loading and not self._all_rows:
            # Delay pequeño para que la ventana se renderice completamente
            self._refresh_timer.start(100)

    def _on_refresh_clicked(self):
        """Manual refresh al hacer click en el botón"""
        if not self._loading:
            self._load_data()

    def _on_clean_clicked(self):
        """Confirma, limpia vencidos en BD y recarga tabla."""
        resp = QMessageBox.question(
            self,
            "Limpiar vencidos",
            "¿Seguro que querés BORRAR todas las unidades vencidas?\n"
            "Esta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            from aplicacion.backend.stock import controller
            borrados = controller.limpiar_unidades_vencidas_controller()
            QMessageBox.information(
                self,
                "Limpieza completada",
                f"Se eliminaron {borrados} unidades vencidas."
            )
            self._load_data()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo limpiar vencidos:\n{e}"
            )

    # ---------- Data Loading ----------
    def _load_data(self):
        """Cargar datos de vencimientos en thread separado"""
        if self._loading:
            return

        self._loading = True
        self.btn_refresh.setEnabled(False)

        # Crear y mostrar diálogo de progreso
        self._progress_dialog = QProgressDialog("Cargando datos de vencimientos...", "Cancelar", 0, 0, self)
        self._progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._progress_dialog.setMinimumDuration(0)
        self._progress_dialog.setValue(0)

        # Thread
        self._data_loader = DataLoader()
        self._data_loader.data_loaded.connect(self._on_data_loaded)
        self._data_loader.error_occurred.connect(self._on_data_error)
        self._data_loader.finished.connect(self._on_data_finished)
        self._data_loader.start()

    def _on_data_finished(self):
        self._loading = False
        self.btn_refresh.setEnabled(True)
        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None

    def _on_data_error(self, msg: str):
        QMessageBox.critical(self, "Error", f"Falló la carga de vencimientos:\n{msg}")

    def _on_data_loaded(self, rows: List[Dict], stats: Dict):
        # Guardar cache
        self._all_rows = rows
        
        # Extraer categorías de los datos que ya vienen
        cats = ["Todas.."]
        seen = set()
        for r in rows:
            c = r["categoria"] or "Sin categoría"
            if c not in seen:
                seen.add(c)
                cats.append(c)
        self._categories = cats

        # Pintar combo
        self.combo_categoria.blockSignals(True)
        self.combo_categoria.clear()
        for c in self._categories:
            self.combo_categoria.addItem(c)
        self.combo_categoria.blockSignals(False)

        # Aplicar filtros activos (si los hay)
        self._apply_filters()

        # Resumen
        self._update_footer(stats)

    # ---------- Filtros ----------
    def _apply_filters(self):
        text = (self.search.text() or "").strip().lower()
        cat = self.combo_categoria.currentText() if self.combo_categoria.count() else "Todas.."

        def _match(row: Dict) -> bool:
            ok = True
            if text:
                if not (text in (row["nombre"] or "").lower() or text in (row["codigo"] or "").lower()):
                    ok = False
            if ok and cat and cat != "Todas..":
                if (row["categoria"] or "Sin categoría") != cat:
                    ok = False
            return ok

        self._filtered_rows = [r for r in self._all_rows if _match(r)]
        self._paint_table()

    # ---------- Pintado ----------
    def _paint_table(self):
        rows = self._filtered_rows
        self.table.setRowCount(len(rows))

        for i, r in enumerate(rows):
            # CÓDIGO
            item0 = QTableWidgetItem(r["codigo"])
            item0.setFlags(item0.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 0, item0)

            # NOMBRE
            item1 = QTableWidgetItem(r["nombre"])
            item1.setFlags(item1.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 1, item1)

            # CATEGORÍA
            item2 = QTableWidgetItem(r["categoria"])
            item2.setFlags(item2.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 2, item2)

            # FECHA VENC.
            item3 = QTableWidgetItem(r["fecha_venc"])
            item3.setFlags(item3.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 3, item3)

            # DÍAS RESTAN.
            dias_txt = "" if r["dias_rest"] is None else str(r["dias_rest"])
            item4 = QTableWidgetItem(dias_txt)
            item4.setFlags(item4.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(i, 4, item4)

            # ESTADO (widget)
            estado_w = _estado_cell_widget(r["estado"])
            self.table.setCellWidget(i, 5, estado_w)

    # ---------- Resumen ----------
    def _update_footer(self, stats: Dict):
        total = stats.get("total", 0)
        vencidos = stats.get("vencidos", 0)
        por_vencer = stats.get("por_vencer", 0)

        self.notif_title.setText("Resumen")
        html = (
            f"<span style='color:black;'>- "
            f"<span style='color:{COLOR_RED}; font-weight:700;'>{vencidos}</span> "
            f"productos vencidos</span><br>"
            f"<span style='color:black;'>- "
            f"<span style='color:{COLOR_ORANGE}; font-weight:700;'>{por_vencer}</span> "
            f"productos vencerán en los próximos "
            f"<span style='color:{COLOR_ORANGE}; font-weight:700;'>10</span> días</span><br>"
            f"<span style='color:black;'>- Total de unidades activas: "
            f"<span style='color:{COLOR_GREEN}; font-weight:700;'>{total}</span></span>"
        )
        self.notif_lines.setTextFormat(Qt.TextFormat.RichText)
        self.notif_lines.setText(html)

    # ---------- Public API ----------
    def refresh(self):
        """Método público para refrescar datos"""
        self._load_data()


# Si querés testear esta vista sola:
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = VencimientosScreen()
    w.resize(1100, 600)
    w.show()
    sys.exit(app.exec())
