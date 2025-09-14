# stock_ventanas/productos.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, 
                             QPushButton, QFrame, QHeaderView, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from pathlib import Path
import json
import os

class ProductosScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.products_data = []
        self.load_products_data()
        self.init_ui()
        
    def load_products_data(self):
        """Cargar datos desde aplicacion/frontend/json/stock.json"""
        try:
            # Obtener la ruta absoluta del archivo JSON
            base_dir = Path(__file__).resolve().parent.parent  # Sube 2 niveles desde stock_ventanas/
            json_path = base_dir / "json" / "stock.json"
            
            print(f"Intentando cargar JSON desde: {json_path}")
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as file:
                    self.products_data = json.load(file)
                print(f"✅ JSON cargado exitosamente: {len(self.products_data)} productos encontrados")
            else:
                print(f"❌ Archivo no encontrado en: {json_path}")
                self._cargar_datos_ejemplo()
                
        except json.JSONDecodeError as e:
            print(f"❌ Error al decodificar JSON: {e}")
            self._cargar_datos_ejemplo()
        except Exception as e:
            print(f"❌ Error al cargar stock.json: {e}")
            self._cargar_datos_ejemplo()
    
    def _cargar_datos_ejemplo(self):
        """Cargar datos de ejemplo si no se puede cargar el JSON"""
        print("Cargando datos de ejemplo...")
        self.products_data = [
            {
                "codigo": "871289371203",
                "nombre": "COCA COLA 1L",
                "categoria": "gaseosas",
                "stock": 12,
                "costo": "1.200,00",
                "precio": "3.400,00",
                "estado": "activo",
                "vencimiento": "2025-12-31",
                "margen_ganancia": "15%",
                "ganancia_bruta_unitaria": "2.200,00",
                "ganancia_neta_unitaria": "2.000,00",
                "ganancia_bruta_total": "26.400,00",
                "ganancia_neta_total": "24.000,00"
            },
            {
                "codigo": "1241515156",
                "nombre": "ARROZ 1KG",
                "categoria": "despensa",
                "stock": 4,
                "costo": "800,20",
                "precio": "1.200,10",
                "estado": "activo",
                "vencimiento": "2026-06-15",
                "margen_ganancia": "50%",
                "ganancia_bruta_unitaria": "399,90",
                "ganancia_neta_unitaria": "350,00",
                "ganancia_bruta_total": "1.599,60",
                "ganancia_neta_total": "1.400,00"
            },
            {
                "codigo": "789456123",
                "nombre": "LECHE 1L",
                "categoria": "lácteos",
                "stock": 0,
                "costo": "450,00",
                "precio": "680,00",
                "estado": "inactivo",
                "vencimiento": "2025-02-20",
                "margen_ganancia": "51%",
                "ganancia_bruta_unitaria": "230,00",
                "ganancia_neta_unitaria": "200,00",
                "ganancia_bruta_total": "0,00",
                "ganancia_neta_total": "0,00"
            }
        ]
        
    def reload_data(self):
        """Método público para recargar los datos desde el JSON"""
        self.load_products_data()
        self.load_table_data()
        print("Datos recargados desde JSON")
        
    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título de la sección
        title_label = QLabel("PRODUCTOS")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Frame contenedor principal
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #4A4A4A;
                border: 2px solid #5A5A5A;
                border-radius: 10px;
            }
        """)
        
        # Layout del contenido
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        
        # Contenedor para el icono
        icon_container = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: #21AFBD;
                border-radius: 30px;
                border: 3px solid #FFFFFF;
            }
        """)
        
        # Cargar la imagen "Lo de manoli.png" usando ruta absoluta
        try:
            base_dir = Path(__file__).resolve().parent.parent
            image_path = base_dir / "Lo de manoli.png"
            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                print(f"No se pudo cargar la imagen desde: {image_path}")
        except Exception as e:
            print(f"Error al cargar 'Lo de manoli.png': {e}")
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_container.addStretch()
        icon_container.addWidget(icon_label)
        icon_container.addStretch()
        
        # Barra de búsqueda y filtros
        search_layout = QHBoxLayout()
        search_layout.setSpacing(20)
        
        # Barra de búsqueda
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("buscar por nombre de producto...")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #6A6A6A;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            QLineEdit:focus {
                border: 2px solid #21AFBD;
            }
        """)
        
        # Selector de categorías - cargar desde los datos reales
        categories_label = QLabel("Categorías:")
        categories_label.setStyleSheet("color: white; font-weight: bold;")
        
        self.categories_combo = QComboBox()
        self._load_categories()
        self.categories_combo.setFixedHeight(35)
        self.categories_combo.setFixedWidth(150)
        self.categories_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #6A6A6A;
                border-radius: 5px;
                background-color: white;
                color: black;
            }
            QComboBox:focus {
                border: 2px solid #21AFBD;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                color: black;
                background-color: white;
                selection-background-color: #E3F2FD;
                selection-color: black;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, stretch=1)
        search_layout.addWidget(categories_label)
        search_layout.addWidget(self.categories_combo)
        
        # Tabla de productos
        self.products_table = QTableWidget()
        self.setup_table()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Botón Recargar (Azul claro) - NUEVO
        reload_button = QPushButton("🔄 RECARGAR")
        reload_button.setFixedSize(150, 50)
        reload_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        reload_button.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #0E6674;
            }
        """)
        reload_button.clicked.connect(self.reload_data)
        
        # Botón Agregar (Verde)
        add_button = QPushButton("AGREGAR")
        add_button.setFixedSize(150, 50)
        add_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1E7E34;
            }
        """)
        add_button.clicked.connect(self.add_product)
        
        # Botón Editar (Azul)
        edit_button = QPushButton("EDITAR")
        edit_button.setFixedSize(150, 50)
        edit_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)
        edit_button.clicked.connect(self.edit_product)
        
        # Botón Eliminar (Rojo)
        delete_button = QPushButton("ELIMINAR")
        delete_button.setFixedSize(150, 50)
        delete_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C82333;
            }
            QPushButton:pressed {
                background-color: #A71E2A;
            }
        """)
        delete_button.clicked.connect(self.delete_product)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(reload_button)  # NUEVO BOTÓN
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(edit_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        
        # Agregar elementos al layout del contenido
        content_layout.addLayout(icon_container)
        content_layout.addLayout(search_layout)
        content_layout.addWidget(self.products_table)
        content_layout.addLayout(buttons_layout)
        
        # Agregar al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(content_frame)
        
        self.setLayout(main_layout)
        
        # Conectar eventos
        self.search_input.textChanged.connect(self.filter_products)
        self.categories_combo.currentTextChanged.connect(self.filter_products)
    
    def _load_categories(self):
        """Cargar categorías desde aplicacion/frontend/json/categorias.json"""
        self.categories_combo.addItem("Todas..")
        
        try:
            # Obtener la ruta absoluta del archivo JSON de categorías
            base_dir = Path(__file__).resolve().parent.parent  # Sube 2 niveles desde stock_ventanas/
            json_path = base_dir / "json" / "categorias.json"
            
            print(f"Intentando cargar categorías desde: {json_path}")
            
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as file:
                    categorias_data = json.load(file)
                print(f"JSON de categorías cargado exitosamente")
                
                # Agregar categorías activas ordenadas alfabéticamente
                if isinstance(categorias_data, list):
                    # Extraer nombres de categorías activas
                    categorias_activas = []
                    for categoria in categorias_data:
                        if isinstance(categoria, dict) and categoria.get("activa", False):
                            nombre = categoria.get("nombre", "").strip()
                            if nombre:
                                categorias_activas.append(nombre)
                    
                    # Agregar categorías ordenadas alfabéticamente al combo
                    for categoria in sorted(categorias_activas):
                        self.categories_combo.addItem(categoria)
                        
                    print(f"Se cargaron {len(categorias_activas)} categorías activas")
                else:
                    print("Formato de JSON de categorías no válido (debe ser una lista)")
                    self._cargar_categorias_defecto()
            else:
                print(f"Archivo de categorías no encontrado en: {json_path}")
                self._cargar_categorias_defecto()
                
        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON de categorías: {e}")
            self._cargar_categorias_defecto()
        except Exception as e:
            print(f"Error al cargar categorias.json: {e}")
            self._cargar_categorias_defecto()

    def _cargar_categorias_defecto(self):
        """Cargar categorías por defecto si no se puede cargar el JSON"""
        print("Cargando categorías por defecto...")
        categorias_defecto = ["gaseosas", "despensa", "limpieza", "lácteos"]
        for categoria in categorias_defecto:
            self.categories_combo.addItem(categoria)
    
    def setup_table(self):
        """Configurar la tabla de productos"""
        # Definir columnas sin CODIGO y sin VENCIMIENTO
        headers = ["NOMBRE", "CATEGORIA", "STOCK", "COSTO", "PRECIO", "ESTADO", 
                  "MARGEN DE GANANCIA", "GANANCIA BRUTA UNIT.", "GANANCIA NETA UNIT.", "GANANCIA BRUTA TOTAL", "GANANCIA NETA TOTAL"]
        self.products_table.setColumnCount(len(headers))
        self.products_table.setHorizontalHeaderLabels(headers)
        
        # Estilo de la tabla - FORZAMOS COLOR NEGRO PARA EL TEXTO
        self.products_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                gridline-color: #DDDDDD;
                font-size: 13px;
                selection-background-color: #E3F2FD;
                color: black;  /* Forzamos texto negro */
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
                color: black;  /* Forzamos texto negro en items */
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: black;  /* Forzamos texto negro en selección */
            }
            QHeaderView::section {
                background-color: #F5F5F5;
                padding: 8px;
                border: 1px solid #DDDDDD;
                font-weight: bold;
                color: black;  /* Forzamos texto negro en headers */
            }
        """)
        
        # Configurar selección
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Hacer tabla de solo lectura
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Configurar anchos de columnas fijos
        header = self.products_table.horizontalHeader()
        self.products_table.setColumnWidth(0, 300)  # NOMBRE (primera columna ahora)
        self.products_table.setColumnWidth(1, 180)  # CATEGORIA
        self.products_table.setColumnWidth(2, 80)   # STOCK
        self.products_table.setColumnWidth(3, 80)   # COSTO
        self.products_table.setColumnWidth(4, 80)   # PRECIO
        self.products_table.setColumnWidth(5, 80)   # ESTADO
        self.products_table.setColumnWidth(6, 190)  # MARGEN DE GANANCIA
        self.products_table.setColumnWidth(7, 190)  # GANANCIA BRUTA UNIT.
        self.products_table.setColumnWidth(8, 190)  # GANANCIA NETA UNIT.
        self.products_table.setColumnWidth(9, 190)  # GANANCIA BRUTA TOTAL
        self.products_table.setColumnWidth(10, 190) # GANANCIA NETA TOTAL
                
        # Desactivar redimensionamiento automático
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        
        # Cargar datos desde JSON
        self.load_table_data()
    
    def load_table_data(self):
        """Cargar datos en la tabla desde products_data"""
        self.products_table.setRowCount(len(self.products_data))
        
        for row, product in enumerate(self.products_data):
            # NOMBRE (ahora es la primera columna - índice 0)
            nombre_item = QTableWidgetItem(str(product.get("nombre", "")))
            nombre_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            nombre_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 0, nombre_item)
            
            # CATEGORIA (índice 1)
            categoria_item = QTableWidgetItem(str(product.get("categoria", "")))
            categoria_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            categoria_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 1, categoria_item)
            
            # STOCK (índice 2)
            stock_item = QTableWidgetItem(str(product.get("stock", "")))
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stock_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 2, stock_item)
            
            # COSTO (índice 3)
            costo_item = QTableWidgetItem(str(product.get("costo", "")))
            costo_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            costo_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 3, costo_item)
            
            # PRECIO (índice 4)
            precio_item = QTableWidgetItem(str(product.get("precio", "")))
            precio_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            precio_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 4, precio_item)
            
            # ESTADO (índice 5)
            estado_item = QTableWidgetItem(str(product.get("estado", "")))
            estado_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Colorear según el estado (mantenemos el color de fondo pero con texto blanco)
            if product.get("estado", "").lower() == "activo":
                estado_item.setBackground(Qt.GlobalColor.green)
                estado_item.setForeground(Qt.GlobalColor.white)  # Texto blanco para contraste
            else:
                estado_item.setBackground(Qt.GlobalColor.red)
                estado_item.setForeground(Qt.GlobalColor.white)  # Texto blanco para contraste
                
            self.products_table.setItem(row, 5, estado_item)
            
            # MARGEN DE GANANCIA (índice 6) - CORREGIDO PARA USAR "margen"
            margen_ganancia = product.get("margen", "")  # Cambio de "margen_ganancia" a "margen"
            
            # Formatear margen según su tipo
            if margen_ganancia == "" or margen_ganancia is None:
                margen_display = "0%"
            elif isinstance(margen_ganancia, (int, float)):
                # Si es decimal (ej: 0.2), convertir a porcentaje
                margen_display = f"{margen_ganancia * 100:.1f}%"
            elif isinstance(margen_ganancia, str):
                # Si ya es string, usarlo tal como está
                if "%" not in margen_ganancia:
                    try:
                        # Intentar convertir string a float y luego a porcentaje
                        margen_float = float(margen_ganancia)
                        if margen_float <= 1:  # Asumimos que es decimal (0.2)
                            margen_display = f"{margen_float * 100:.1f}%"
                        else:  # Asumimos que ya es porcentaje (20)
                            margen_display = f"{margen_float}%"
                    except ValueError:
                        margen_display = str(margen_ganancia)
                else:
                    margen_display = str(margen_ganancia)
            else:
                margen_display = "0%"
            
            margen_item = QTableWidgetItem(margen_display)
            margen_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            margen_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 6, margen_item)
            
            # GANANCIA BRUTA UNITARIA (índice 7)
            ganancia_bruta_unit_item = QTableWidgetItem(str(product.get("ganancia_bruta_unitaria", "") if product.get("ganancia_bruta_unitaria") is not None else ""))
            ganancia_bruta_unit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            ganancia_bruta_unit_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 7, ganancia_bruta_unit_item)
            
            # GANANCIA NETA UNITARIA (índice 8)
            ganancia_neta_unit_item = QTableWidgetItem(str(product.get("ganancia_neta_unitaria", "") if product.get("ganancia_neta_unitaria") is not None else ""))
            ganancia_neta_unit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            ganancia_neta_unit_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 8, ganancia_neta_unit_item)
            
            # GANANCIA BRUTA TOTAL (índice 9)
            ganancia_bruta_total_item = QTableWidgetItem(str(product.get("ganancia_bruta_total", "") if product.get("ganancia_bruta_total") is not None else ""))
            ganancia_bruta_total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            ganancia_bruta_total_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 9, ganancia_bruta_total_item)
            
            # GANANCIA NETA TOTAL (índice 10)
            ganancia_neta_total_item = QTableWidgetItem(str(product.get("ganancia_neta_total", "") if product.get("ganancia_neta_total") is not None else ""))
            ganancia_neta_total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            ganancia_neta_total_item.setForeground(Qt.GlobalColor.black)
            self.products_table.setItem(row, 10, ganancia_neta_total_item)
    
    def filter_products(self):
        """Filtrar productos según búsqueda y categoría"""
        search_text = self.search_input.text().lower()
        selected_category = self.categories_combo.currentText()
        
        for row in range(self.products_table.rowCount()):
            # Obtener datos de la fila (ahora nombre está en índice 0, categoría en índice 1)
            nombre = self.products_table.item(row, 0).text().lower() if self.products_table.item(row, 0) else ""
            categoria = self.products_table.item(row, 1).text() if self.products_table.item(row, 1) else ""
            
            # Verificar filtros (solo buscar en nombre)
            matches_search = search_text in nombre
            matches_category = selected_category == "Todas.." or categoria == selected_category
            
            # Mostrar/ocultar fila
            self.products_table.setRowHidden(row, not (matches_search and matches_category))
    
    def add_product(self):
        """Función para agregar producto"""
        try:
            from aplicacion.frontend.stock_ventanas.agregar_producto_dialog import AgregarProductoDialog
            
            dialog = AgregarProductoDialog(self)
            if dialog.exec() == AgregarProductoDialog.DialogCode.Accepted:
                print("Producto agregado exitosamente")
                # Recargar la tabla para mostrar el nuevo producto
                self.reload_data()
                QMessageBox.information(
                    self,
                    "Producto agregado",
                    "El producto se ha agregado exitosamente.\n\nLa tabla se ha actualizado automáticamente."
                )
            else:
                print("Agregado de producto cancelado")
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el diálogo de agregar producto: {e}")
    
    def edit_product(self):
        """Función para editar producto seleccionado"""
        selected_row = self.products_table.currentRow()
        
        if selected_row < 0:
            # Mostrar mensaje si no hay producto seleccionado
            QMessageBox.warning(
                self, 
                "Sin selección", 
                "Por favor, selecciona un producto de la lista para editar."
            )
            return
        
        try:
            # Obtener datos del producto seleccionado
            producto_data = {}
            
            # Si tenemos los datos en products_data, usarlos
            if selected_row < len(self.products_data):
                producto_data = self.products_data[selected_row].copy()
            else:
                # Si no, obtener los datos directamente de la tabla
                producto_data = {
                    "nombre": self.products_table.item(selected_row, 0).text() if self.products_table.item(selected_row, 0) else "",
                    "categoria": self.products_table.item(selected_row, 1).text() if self.products_table.item(selected_row, 1) else "",
                    "stock": self.products_table.item(selected_row, 2).text() if self.products_table.item(selected_row, 2) else "",
                    "costo": self.products_table.item(selected_row, 3).text() if self.products_table.item(selected_row, 3) else "",
                    "precio": self.products_table.item(selected_row, 4).text() if self.products_table.item(selected_row, 4) else "",
                    "estado": self.products_table.item(selected_row, 5).text() if self.products_table.item(selected_row, 5) else "",
                    "margen_ganancia": self.products_table.item(selected_row, 6).text() if self.products_table.item(selected_row, 6) else "",
                }
                
                # Si hay código en products_data, agregarlo
                if selected_row < len(self.products_data) and "codigo" in self.products_data[selected_row]:
                    producto_data["codigo"] = self.products_data[selected_row]["codigo"]
            
            print(f"Editando producto: {producto_data.get('nombre', 'Sin nombre')}")
            
            # Importar y abrir el diálogo de edición
            from aplicacion.frontend.stock_ventanas.editar_producto_dialog import EditarProductoDialog
            
            dialog = EditarProductoDialog(self, producto_data)
            result = dialog.exec()
            
            if result == EditarProductoDialog.DialogCode.Accepted:
                action = dialog.selected_action
                print(f"Acción confirmada: {action}")
                
                # Manejar las diferentes acciones
                if action == "editar_datos":
                    # TODO: Implementar edición de datos
                    QMessageBox.information(
                        self, 
                        "Función en desarrollo", 
                        f"Editar datos de: {producto_data.get('nombre', 'Sin nombre')}\n\nEsta función se implementará próximamente."
                    )
                
                elif action == "modificar_stock":
                    # TODO: Implementar modificación de stock
                    QMessageBox.information(
                        self, 
                        "Función en desarrollo", 
                        f"Modificar stock de: {producto_data.get('nombre', 'Sin nombre')}\n\nStock actual: {producto_data.get('stock', '0')}\n\nEsta función se implementará próximamente."
                    )
                
                elif action == "ver_unidades":
                    # TODO: Implementar visualización de unidades
                    QMessageBox.information(
                        self, 
                        "Función en desarrollo", 
                        f"Ver unidades de: {producto_data.get('nombre', 'Sin nombre')}\n\nEsta función se implementará próximamente."
                    )
                
                # Recargar tabla si es necesario
                # self.reload_data()
            else:
                print("Edición cancelada")
                
        except ImportError as e:
            QMessageBox.critical(
                self, 
                "Error de importación", 
                f"No se pudo cargar el diálogo de edición:\n{e}\n\nAsegúrate de que el archivo 'editar_producto_dialog.py' existe en la carpeta 'stock_ventanas'."
            )
        except Exception as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Ocurrió un error al intentar editar el producto:\n{e}"
            )
    
    def delete_product(self):
        """Función para eliminar producto seleccionado"""
        selected_row = self.products_table.currentRow()
        
        if selected_row < 0:
            QMessageBox.warning(
                self, 
                "Sin selección", 
                "Por favor, selecciona un producto de la lista para eliminar."
            )
            return
        
        # Obtener nombre del producto para mostrar en confirmación
        nombre_producto = ""
        if self.products_table.item(selected_row, 0):
            nombre_producto = self.products_table.item(selected_row, 0).text()
        
        # Obtener ID del producto desde products_data
        producto_id = None
        if selected_row < len(self.products_data):
            # Buscar el ID en los datos del producto
            if "id" in self.products_data[selected_row]:
                producto_id = self.products_data[selected_row]["id"]
            elif "codigo" in self.products_data[selected_row]:
                # Si no hay ID, intentar buscar por nombre en el backend
                try:
                    from aplicacion.backend.stock import controller
                    productos = controller.listar_productos_controller()
                    for p in productos:
                        if p.nombre == nombre_producto:
                            producto_id = p.id
                            break
                except Exception as e:
                    print(f"Error buscando producto por nombre: {e}")
        
        if producto_id is None:
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo obtener el ID del producto '{nombre_producto}'.\n\nAsegúrate de que el producto existe en la base de datos."
            )
            return
        
        # Confirmar eliminación
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar el producto:\n\n'{nombre_producto}'?\n\nEsta acción no se puede deshacer y eliminará:\n• El producto de la base de datos\n• Todas sus unidades físicas\n• Todo su historial",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Importar el controller
                from aplicacion.backend.stock import controller
                
                print(f"Eliminando producto: {nombre_producto} (ID: {producto_id})")
                
                # Llamar a la función del controller para eliminar
                resultado = controller.eliminar_producto_controller(producto_id)
                
                if resultado:
                    print(f"✅ Producto '{nombre_producto}' eliminado exitosamente")
                    
                    # Regenerar JSON actualizado
                    try:
                        from aplicacion.backend.stock.crud import exportar_productos_json
                        print("Generando JSON actualizado después de eliminación...")
                        json_exportado = exportar_productos_json()
                        if json_exportado:
                            print("✅ JSON de stock actualizado exitosamente")
                        else:
                            print("⚠️ Advertencia: No se pudo actualizar el JSON de stock")
                    except Exception as e:
                        print(f"⚠️ Error al exportar JSON: {e}")
                    
                    # Recargar la tabla para mostrar los cambios
                    self.reload_data()
                    
                    # Mostrar mensaje de éxito
                    QMessageBox.information(
                        self,
                        "Producto eliminado",
                        f"El producto '{nombre_producto}' se ha eliminado exitosamente.\n\nLa tabla se ha actualizado automáticamente."
                    )
                else:
                    print(f"❌ Error: No se pudo eliminar el producto")
                    QMessageBox.warning(
                        self,
                        "Error al eliminar",
                        f"No se pudo eliminar el producto '{nombre_producto}'.\n\nEs posible que el producto no exista o haya ocurrido un error en la base de datos."
                    )
                    
            except ImportError as e:
                QMessageBox.critical(
                    self,
                    "Error de importación",
                    f"No se pudo cargar el módulo del controller:\n{e}\n\nVerifica que el backend esté correctamente configurado."
                )
            except Exception as e:
                print(f"❌ Error eliminando producto: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Ocurrió un error al eliminar el producto:\n\n{str(e)}"
                )
        else:
            print("Eliminación cancelada por el usuario")