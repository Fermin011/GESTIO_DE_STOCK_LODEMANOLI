# stock_ventanas/ver_stock.py
from __future__ import annotations

import json
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QProgressBar,
    QApplication, QLineEdit
)

# Importar los widgets optimizados del diálogo de agregar producto
from .agregar_producto_dialog import AutoFormatDateEdit, OptimizedTableWidget

# Importar las funciones de utils.py para obtener códigos de barras
from aplicacion.backend.stock.utils import (
    obtener_codigos_por_producto,
    obtener_codigos_activos_por_producto,
    mostrar_codigos_producto
)

# Importar controller para obtener información del producto
from aplicacion.backend.stock import controller

# Importar las nuevas funciones del controller para editar fechas
from aplicacion.backend.stock.controller import (
    actualizar_fecha_vencimiento_unidad_controller,
    actualizar_fechas_vencimiento_lote_controller
)


class VerStockDialog(QDialog):
    def __init__(self, parent=None, nombre_producto=None, producto_id=None):
        super().__init__(parent)
        self.producto_id = producto_id
        self.nombre_producto = nombre_producto or ""
        self.unidades_datos = []
        self.producto_info = {}
        self.cambios_realizados = []  # Para trackear cambios en fechas
        self.fecha_widgets = {}  # Para almacenar referencias a los widgets de fecha
        
        self.setWindowTitle("VER UNIDADES REGISTRADAS")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        
        # Cargar datos del producto
        self._cargar_datos_producto()
        self._build_ui()
        self._cargar_unidades()
        
        # Establecer el modo activo por defecto
        self._actualizar_estilos_botones("activos")

    def obtener_cambios_realizados(self):
        """
        Retorna lista de cambios realizados en las fechas de vencimiento
        """
        return self.cambios_realizados.copy()

    def _cargar_datos_producto(self):
        """Carga la información del producto desde la base de datos usando el controller"""
        try:
            # Verificar si producto_id es realmente un entero o es un nombre
            if self.producto_id and isinstance(self.producto_id, str) and not self.producto_id.isdigit():
                # Si producto_id es un string que no es numérico, tratarlo como nombre
                print(f"Detectado nombre como producto_id: {self.producto_id}")
                self.nombre_producto = self.producto_id
                self.producto_id = None
            
            if not self.producto_id:
                # Si no tenemos ID pero sí nombre, buscar por nombre
                if self.nombre_producto:
                    print(f"Buscando producto por nombre: {self.nombre_producto}")
                    productos = controller.listar_productos_controller()
                    for producto in productos:
                        if producto.nombre == self.nombre_producto:
                            self.producto_id = producto.id
                            print(f"Producto encontrado - ID: {producto.id}, Nombre: {producto.nombre}")
                            self.producto_info = {
                                'id': producto.id,
                                'nombre': producto.nombre,
                                'stock': producto.cantidad,
                                'unidad_medida': producto.unidad_medida,
                                'precio': producto.precio_redondeado,
                                'categoria_id': producto.categoria_id,
                                'es_divisible': producto.es_divisible
                            }
                            break
                
                if not self.producto_id:
                    print(f"No se encontró el producto: {self.nombre_producto}")
                    return
            else:
                # Si tenemos ID, obtener datos directamente
                print(f"Buscando producto por ID: {self.producto_id}")
                productos = controller.listar_productos_controller()
                for producto in productos:
                    if producto.id == self.producto_id:
                        self.producto_info = {
                            'id': producto.id,
                            'nombre': producto.nombre,
                            'stock': producto.cantidad,
                            'unidad_medida': producto.unidad_medida,
                            'precio': producto.precio_redondeado,
                            'categoria_id': producto.categoria_id,
                            'es_divisible': producto.es_divisible
                        }
                        self.nombre_producto = producto.nombre
                        print(f"Producto encontrado por ID - Nombre: {producto.nombre}")
                        break
                        
            # Obtener nombre de categoría si existe
            if self.producto_info.get('categoria_id'):
                categorias = controller.listar_clasificaciones_controller()
                for categoria in categorias:
                    if categoria.id == self.producto_info['categoria_id']:
                        self.producto_info['categoria_nombre'] = categoria.nombre
                        break
            else:
                self.producto_info['categoria_nombre'] = 'Sin categoría'
                
        except Exception as e:
            print(f"Error al cargar datos del producto: {e}")
            self._mostrar_error(f"Error al cargar datos del producto: {e}")

    def _build_ui(self):
        """Construye la interfaz de usuario"""
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Título
        title = QLabel("VER UNIDADES REGISTRADAS")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #22C55E;")
        root.addWidget(title)

        # Información del producto
        if self.producto_info:
            info_text = f"Producto: {self.producto_info.get('nombre', 'N/A')} | "
            info_text += f"Stock: {self.producto_info.get('stock', 0)} {self.producto_info.get('unidad_medida', 'unidades')} | "
            info_text += f"Precio: ${self.producto_info.get('precio', 0)} | "
            info_text += f"Categoría: {self.producto_info.get('categoria_nombre', 'Sin categoría')}"
            
            info_label = QLabel(info_text)
            info_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            info_label.setStyleSheet("""
                color: #666;
                font-size: 14px;
                background: #f0f0f0;
                padding: 8px;
                border-radius: 6px;
                margin: 5px 0;
            """)
            root.addWidget(info_label)

        # Frame principal
        frame = QFrame()
        frame.setObjectName("panel")
        frame.setStyleSheet("""
            QFrame#panel {
                background:#3f3f3f; 
                border:2px solid #5a5a5a; 
                border-radius:10px;
            }
        """)
        root.addWidget(frame, 1)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(18, 18, 18, 18)
        frame_layout.setSpacing(12)

        # Contenido de la tabla
        self._build_table_content(frame_layout)

        # Footer con botones
        self._build_footer(root)

    def _build_table_content(self, parent_layout):
        """Construye el contenido de la tabla con campos más grandes"""
        box = QFrame()
        box.setObjectName("box2")
        box.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        box.setStyleSheet("""
            QFrame#box2 { 
                background: white; 
                border-radius: 14px; 
            }

            #box2 QTableWidget {
                background: white; 
                color: #111;
                gridline-color: #e0e0e0;
                selection-background-color: #E3F2FD; 
                selection-color: #111;
                border: 1px solid #dcdcdc; 
                border-radius: 8px;
            }
            #box2 QTableWidget::item {
                background: white;
                color: #111;
                border: none;
                padding: 8px;
            }
            #box2 QTableWidget::item:selected {
                background: #E3F2FD;
                color: #111;
            }
            #box2 QTableWidget::item:alternate {
                background: #f8f9fa;
                color: #111;
            }
            #box2 QHeaderView::section { 
                background: #e7eefc; 
                font-weight: bold; 
                color: #111; 
                border: 1px solid #dcdcdc;
                padding: 12px 8px;
                font-size: 14px;
            }

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
        parent_layout.addWidget(box, 1)

        gl = QVBoxLayout(box)
        gl.setContentsMargins(16, 16, 16, 16)
        gl.setSpacing(8)

        # Subtítulo con instrucciones
        subt = QLabel("CÓDIGOS DE BARRAS DEL PRODUCTO")
        subt.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subt.setStyleSheet("color:#444;font-weight:bold;font-size:14px;")
        gl.addWidget(subt)
        
        # Instrucciones de edición
        instrucciones = QLabel("💡 Tip: Haz click en las fechas de vencimiento para editarlas")
        instrucciones.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        instrucciones.setStyleSheet("""
            color: #059669;
            font-size: 12px;
            background: #ecfdf5;
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid #a7f3d0;
            margin: 5px 0;
        """)
        gl.addWidget(instrucciones)

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

        # Tabla - con encabezados mejorados y configuración de tamaños
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código de barras", "📅 Fecha de Vencimiento", "Estado"])
        
        # Configurar el redimensionamiento de columnas - MEJORADO PARA FECHA MÁS ANCHA
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Código se estira
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Vencimiento tamaño fijo más ancho
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Estado se ajusta al contenido
        
        # Establecer ancho específico para la columna de vencimiento (más ancho)
        self.table.setColumnWidth(1, 200)  # 200 píxeles para la columna de fecha
        
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # IMPORTANTE: Aumentar la altura de las filas para que los campos se vean mejor
        self.table.verticalHeader().setDefaultSectionSize(60)  # Altura de 60 píxeles por fila
        
        gl.addWidget(self.table, 1)

        # Variables para paginación manual
        self.current_page = 0
        self.page_size = 50  # Mostrar 50 elementos por página

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
        self.btn_mostrar_todos = QPushButton("Ver todos (activos + inactivos)")
        self.btn_mostrar_activos = QPushButton("Solo códigos activos")
        
        # Estilo para indicar cuál está activo
        self.btn_mostrar_activos.setStyleSheet("""
            QPushButton {
                background: #22C55E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        
        act.addStretch()
        act.addWidget(self.btn_mostrar_todos)
        act.addWidget(self.btn_mostrar_activos)
        act.addStretch()
        gl.addLayout(act)

        # Conectar señales
        self.btn_mostrar_todos.clicked.connect(self._mostrar_todos_codigos)
        self.btn_mostrar_activos.clicked.connect(self._mostrar_solo_activos)

    def _build_footer(self, parent_layout):
        """Construye el footer con botones"""
        footer = QHBoxLayout()
        footer.addStretch()

        self.btn_cancelar = QPushButton("CERRAR")
        self.btn_cancelar.setFixedHeight(44)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background:#6B7280;
                color:white;
                border:none;
                border-radius:22px;
                padding:0 24px;
                font-weight:bold;
            } 
            QPushButton:hover {
                background:#4B5563;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_actualizar = QPushButton("ACTUALIZAR")
        self.btn_actualizar.setFixedHeight(44)
        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background:#22C55E;
                color:white;
                border:none;
                border-radius:22px;
                padding:0 24px;
                font-weight:bold;
            } 
            QPushButton:hover {
                background:#16A34A;
            }
        """)
        self.btn_actualizar.clicked.connect(self._actualizar_datos)

        footer.addWidget(self.btn_cancelar)
        footer.addWidget(self.btn_actualizar)
        parent_layout.addLayout(footer)

    def _cargar_unidades(self):
        """Carga las unidades usando las funciones de utils.py - SOLO ACTIVOS por defecto"""
        if not self.producto_id:
            self._mostrar_error("No se pudo obtener el ID del producto")
            return

        try:
            print(f"Cargando unidades ACTIVAS para producto_id: {self.producto_id} (tipo: {type(self.producto_id)})")
            
            # Asegurar que producto_id sea entero
            if isinstance(self.producto_id, str):
                try:
                    self.producto_id = int(self.producto_id)
                except ValueError:
                    self._mostrar_error(f"ID de producto inválido: {self.producto_id}")
                    return
            
            # Usar la función obtener_codigos_activos_por_producto para obtener SOLO códigos activos
            codigos_activos = obtener_codigos_activos_por_producto(self.producto_id)
            print(f"Códigos activos obtenidos: {len(codigos_activos)} códigos encontrados")
            
            if not codigos_activos:
                self.info_label.setText("Este producto no tiene códigos de barras activos")
                self.unidades_datos = []
                self._actualizar_tabla()
                print("No se encontraron códigos activos para este producto")
                return

            # Convertir los datos al formato esperado por la tabla
            self.unidades_datos = []
            for codigo, vencimiento in codigos_activos.items():
                venc_display = vencimiento or "Sin vencimiento"
                
                print(f"  Código: {codigo} | Vence: {venc_display} | Estado: activo")
                
                self.unidades_datos.append({
                    "codigo": codigo,
                    "vencimiento": vencimiento,  # Mantener el valor original para edición
                    "vencimiento_display": venc_display,  # Para mostrar
                    "estado": "✅ Activo",
                    "estado_raw": "activo",
                    "unidad_id": None  # Se llenará a continuación
                })

            print(f"Total de unidades activas procesadas: {len(self.unidades_datos)}")
            
            # Siempre obtener los IDs de las unidades para edición
            self._obtener_ids_unidades()
            
            # Actualizar tabla
            self._actualizar_tabla()
            
        except Exception as e:
            print(f"Error al cargar unidades: {e}")
            import traceback
            traceback.print_exc()
            self._mostrar_error(f"Error al cargar códigos de barras: {e}")

    def _obtener_ids_unidades(self):
        """Obtiene los IDs de las unidades para poder editarlas"""
        try:
            from aplicacion.backend.stock.controller import obtener_unidades_de_producto_controller
            
            unidades_completas = obtener_unidades_de_producto_controller(self.producto_id)
            
            # Crear un mapeo de código_barras -> unidad_id
            codigo_a_id = {}
            for unidad in unidades_completas:
                if unidad.codigo_barras and unidad.estado == "activo":
                    codigo_a_id[unidad.codigo_barras] = unidad.id
            
            # Actualizar los datos con los IDs
            for datos in self.unidades_datos:
                codigo = datos["codigo"]
                if codigo in codigo_a_id:
                    datos["unidad_id"] = codigo_a_id[codigo]
                    
            print(f"IDs de unidades obtenidos: {len(codigo_a_id)} unidades")
            
        except Exception as e:
            print(f"Error al obtener IDs de unidades: {e}")

    def _mostrar_todos_codigos(self):
        """Muestra todos los códigos (activos e inactivos)"""
        if not self.producto_id:
            return

        try:
            print(f"Cargando TODOS los códigos (activos + inactivos) para producto_id: {self.producto_id}")
            
            # Usar la función obtener_codigos_por_producto para obtener todos los códigos
            codigos_completos = obtener_codigos_por_producto(self.producto_id)
            
            if not codigos_completos:
                self.info_label.setText("Este producto no tiene códigos de barras registrados")
                self.unidades_datos = []
                self.current_page = 0
                self._actualizar_tabla()
                return

            # Convertir los datos al formato esperado por la tabla
            self.unidades_datos = []
            for codigo, info in codigos_completos.items():
                vencimiento = info.get("vencimiento")
                venc_display = vencimiento or "Sin vencimiento"
                estado = info.get("estado", "desconocido")
                
                # Agregar emoji para el estado
                estado_display = "✅ Activo" if estado == "activo" else "❌ Inactivo"
                
                self.unidades_datos.append({
                    "codigo": codigo,
                    "vencimiento": vencimiento,  # Mantener el valor original
                    "vencimiento_display": venc_display,  # Para mostrar
                    "estado": estado_display,
                    "estado_raw": estado,
                    "unidad_id": info.get("id_unidad"),
                    "observaciones": info.get("observaciones", "")
                })

            # Resetear página y actualizar tabla
            self.current_page = 0
            self._actualizar_tabla()
            
            # Actualizar estilos de botones
            self._actualizar_estilos_botones("todos")
            
        except Exception as e:
            print(f"Error al cargar todos los códigos: {e}")
            self._mostrar_error(f"Error al cargar todos los códigos: {e}")

    def _mostrar_solo_activos(self):
        """Muestra solo los códigos activos"""
        if not self.producto_id:
            return

        try:
            # Usar la función obtener_codigos_activos_por_producto
            codigos_activos = obtener_codigos_activos_por_producto(self.producto_id)
            
            if not codigos_activos:
                self.info_label.setText("Este producto no tiene códigos activos")
                self.unidades_datos = []
                self.current_page = 0
                self._actualizar_tabla()
                return

            # Convertir los datos al formato esperado por la tabla
            self.unidades_datos = []
            for codigo, vencimiento in codigos_activos.items():
                venc_display = vencimiento or "Sin vencimiento"
                
                self.unidades_datos.append({
                    "codigo": codigo,
                    "vencimiento": vencimiento,  # Mantener el valor original
                    "vencimiento_display": venc_display,  # Para mostrar
                    "estado": "✅ Activo",
                    "estado_raw": "activo",
                    "unidad_id": None  # Se llenará si es necesario
                })

            # Siempre obtener IDs para edición
            self._obtener_ids_unidades()

            # Resetear página y actualizar tabla
            self.current_page = 0
            self._actualizar_tabla()
            
            # Actualizar estilos de botones
            self._actualizar_estilos_botones("activos")
            
        except Exception as e:
            print(f"Error al cargar códigos activos: {e}")
            self._mostrar_error(f"Error al cargar códigos activos: {e}")

    def _actualizar_estilos_botones(self, modo):
        """Actualiza los estilos de los botones según el modo activo"""
        estilo_normal = """
            QPushButton {
                background: #f5f5f5;
                color: #111;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: #e9e9e9;
            }
        """
        
        estilo_activo = """
            QPushButton {
                background: #22C55E;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #16A34A;
            }
        """
        
        if modo == "activos":
            self.btn_mostrar_activos.setStyleSheet(estilo_activo)
            self.btn_mostrar_todos.setStyleSheet(estilo_normal)
        else:  # modo == "todos"
            self.btn_mostrar_todos.setStyleSheet(estilo_activo)
            self.btn_mostrar_activos.setStyleSheet(estilo_normal)

    def _actualizar_tabla(self):
        """Actualiza la tabla con los datos de las unidades - CAMPOS MÁS GRANDES"""
        print(f"Actualizando tabla con {len(self.unidades_datos)} unidades")
        
        # Limpiar tabla y widgets previos
        self.table.setRowCount(0)
        self.fecha_widgets.clear()
        
        # Calcular datos para la página actual
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(self.unidades_datos))
        
        # Mostrar datos de la página actual
        datos_pagina = self.unidades_datos[start_idx:end_idx]
        self.table.setRowCount(len(datos_pagina))
        
        for row, unidad in enumerate(datos_pagina):
            global_idx = start_idx + row  # Índice global en la lista completa
            
            # Código de barras (no editable)
            codigo_item = QTableWidgetItem(unidad.get("codigo", ""))
            codigo_item.setFlags(codigo_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # No editable
            self.table.setItem(row, 0, codigo_item)
            
            # Vencimiento (editable para códigos activos) - CAMPOS MÁS GRANDES
            vencimiento_valor = unidad.get("vencimiento") or ""
            es_activo = unidad.get("estado_raw") == "activo"
            
            if es_activo:
                # Crear widget editable para la fecha con TAMAÑO MEJORADO
                fecha_edit = QLineEdit()
                fecha_edit.setPlaceholderText("YYYY-MM-DD")
                fecha_edit.setText(vencimiento_valor)
                
                # Estilos MEJORADOS para campos más grandes y legibles
                fecha_edit.setStyleSheet("""
                    QLineEdit {
                        background: #ffffff;
                        color: #111;
                        border: 2px solid #22C55E;
                        border-radius: 8px;
                        padding: 12px 16px;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 14px;
                        font-weight: 500;
                        min-height: 30px;
                        min-width: 150px;
                    }
                    QLineEdit:hover {
                        border-color: #16A34A;
                        background: #f0fff0;
                        cursor: text;
                    }
                    QLineEdit:focus {
                        border-color: #059669;
                        background: #ecfdf5;
                        outline: none;
                        border-width: 3px;
                    }
                    QLineEdit:disabled {
                        background: #f8f9fa;
                        color: #666;
                        border-color: #d0d0d0;
                    }
                """)
                
                # Conectar señal para trackear cambios
                fecha_edit.textChanged.connect(
                    lambda text, idx=global_idx, widget=fecha_edit: self._on_fecha_changed(idx, text, widget)
                )
                
                # Agregar evento de click para mejor UX
                fecha_edit.mousePressEvent = lambda event, widget=fecha_edit: self._on_fecha_click(event, widget)
                
                # Agregar tooltip mejorado
                fecha_edit.setToolTip("📅 Click para editar fecha de vencimiento\n" + 
                                    "Formato: YYYY-MM-DD\n" +
                                    "Ejemplo: 2024-12-31\n" +
                                    "Deja vacío para 'Sin vencimiento'")
                
                self.table.setCellWidget(row, 1, fecha_edit)
                self.fecha_widgets[global_idx] = fecha_edit
            else:
                # Mostrar como texto no editable para códigos inactivos
                venc_display = unidad.get("vencimiento_display", "Sin vencimiento")
                vencimiento_item = QTableWidgetItem(venc_display)
                vencimiento_item.setFlags(vencimiento_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                # Estilo para campos no editables con mejor tamaño
                vencimiento_item.setBackground(Qt.GlobalColor.lightGray)
                vencimiento_item.setFont(QFont("Segoe UI", 12))
                self.table.setItem(row, 1, vencimiento_item)
            
            # Estado (no editable)
            estado_item = QTableWidgetItem(unidad.get("estado", ""))
            estado_item.setFlags(estado_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            estado_item.setFont(QFont("Segoe UI", 12))
            self.table.setItem(row, 2, estado_item)
            
            print(f"  Fila {row+1}: {unidad.get('codigo')} | {vencimiento_valor} | {unidad.get('estado')}")
        
        self._update_pagination_info()
        print("Tabla actualizada correctamente")

    def _on_fecha_changed(self, global_idx, nuevo_texto, widget):
        """Maneja cambios en los campos de fecha con validación mejorada - ESTILOS MÁS GRANDES"""
        # Obtener datos de la unidad
        if global_idx >= len(self.unidades_datos):
            return
            
        unidad = self.unidades_datos[global_idx]
        unidad_id = unidad.get("unidad_id")
        
        if not unidad_id:
            widget.setStyleSheet("""
                QLineEdit {
                    background: #ffe6e6;
                    color: #111;
                    border: 3px solid #dc2626;
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    font-weight: 500;
                    min-height: 30px;
                }
            """)
            widget.setToolTip("❌ ERROR: No se encontró ID de unidad")
            return
        
        # Validar formato de fecha
        fecha_limpia = nuevo_texto.strip()
        es_valida = True
        tooltip_mensaje = "📅 Click para editar fecha de vencimiento\nFormato: YYYY-MM-DD\nEjemplo: 2024-12-31"
        
        if fecha_limpia and fecha_limpia not in ["Sin vencimiento", ""]:
            try:
                # Validación de formato YYYY-MM-DD
                if len(fecha_limpia) == 10 and fecha_limpia[4] == '-' and fecha_limpia[7] == '-':
                    from datetime import datetime
                    fecha_obj = datetime.strptime(fecha_limpia, '%Y-%m-%d')
                    # Verificar que la fecha no sea muy antigua
                    if fecha_obj.year < 2020:
                        tooltip_mensaje = "⚠️ Fecha muy antigua. Verifique el año."
                    elif fecha_obj.year > 2050:
                        tooltip_mensaje = "⚠️ Fecha muy lejana. Verifique el año."
                    else:
                        tooltip_mensaje = f"✅ Fecha válida: {fecha_obj.strftime('%d/%m/%Y')}"
                else:
                    es_valida = False
                    tooltip_mensaje = "❌ Formato inválido. Use: YYYY-MM-DD"
            except ValueError:
                es_valida = False
                tooltip_mensaje = "❌ Fecha inválida. Verifique día/mes."
        elif not fecha_limpia:
            tooltip_mensaje = "📅 Sin fecha de vencimiento"
        
        # Crear o actualizar el cambio
        cambio_existente = None
        for i, cambio in enumerate(self.cambios_realizados):
            if cambio["unidad_id"] == unidad_id:
                cambio_existente = cambio
                break
        
        if cambio_existente:
            cambio_existente["nueva_fecha"] = fecha_limpia
        else:
            self.cambios_realizados.append({
                "unidad_id": unidad_id,
                "nueva_fecha": fecha_limpia,
                "codigo": unidad.get("codigo", ""),
                "fecha_original": unidad.get("vencimiento", "")
            })
        
        # Aplicar estilo según validez con CAMPOS MÁS GRANDES
        estilo_base = """
            QLineEdit {{
                color: #111;
                border-radius: 8px;
                padding: 12px 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                min-height: 30px;
                min-width: 150px;
            }}
            QLineEdit:hover {{
                cursor: text;
            }}
            QLineEdit:focus {{
                outline: none;
                border-width: 3px;
            }}
        """
        
        if fecha_limpia == "" or fecha_limpia == "Sin vencimiento":
            widget.setStyleSheet(estilo_base.format() + """
                QLineEdit {
                    background: #fffbeb;
                    border: 2px solid #f59e0b;
                }
                QLineEdit:hover {
                    background: #fef3c7;
                    border-color: #d97706;
                }
                QLineEdit:focus {
                    background: #fef3c7;
                    border-color: #92400e;
                }
            """)
        elif es_valida:
            widget.setStyleSheet(estilo_base.format() + """
                QLineEdit {
                    background: #f0fdf4;
                    border: 2px solid #22c55e;
                }
                QLineEdit:hover {
                    background: #dcfce7;
                    border-color: #16a34a;
                }
                QLineEdit:focus {
                    background: #dcfce7;
                    border-color: #15803d;
                }
            """)
        else:
            widget.setStyleSheet(estilo_base.format() + """
                QLineEdit {
                    background: #fef2f2;
                    border: 2px solid #ef4444;
                }
                QLineEdit:hover {
                    background: #fee2e2;
                    border-color: #dc2626;
                }
                QLineEdit:focus {
                    background: #fee2e2;
                    border-color: #b91c1c;
                }
            """)
        
        # Actualizar tooltip
        widget.setToolTip(tooltip_mensaje)

    def _on_fecha_click(self, event, widget):
        """Maneja el click en los campos de fecha para mejor UX"""
        # Seleccionar todo el texto cuando se hace click
        widget.selectAll()
        # Establecer el foco en el widget
        widget.setFocus()
        # Llamar al evento original
        QLineEdit.mousePressEvent(widget, event)

    def _debug_consola(self):
        """Muestra información de debug en la consola usando mostrar_codigos_producto"""
        if not self.producto_id:
            print("No hay ID de producto disponible")
            return
            
        try:
            print(f"\n{'='*50}")
            print(f"DEBUG: Producto ID {self.producto_id} - {self.nombre_producto}")
            print(f"{'='*50}")
            
            # Usar la función mostrar_codigos_producto para debug
            mostrar_codigos_producto(self.producto_id)
            
            # También mostrar información básica del producto
            print(f"\nINFO DEL PRODUCTO:")
            print(f"  ├─ Nombre: {self.producto_info.get('nombre', 'N/A')}")
            print(f"  ├─ Stock: {self.producto_info.get('stock', 0)} {self.producto_info.get('unidad_medida', 'unidades')}")
            print(f"  ├─ Es divisible: {self.producto_info.get('es_divisible', False)}")
            print(f"  └─ Categoría: {self.producto_info.get('categoria_nombre', 'Sin categoría')}")
            print(f"{'='*50}\n")
            
            self._mostrar_info("Información de debug mostrada en la consola")
            
        except Exception as e:
            print(f"Error en debug: {e}")
            self._mostrar_error(f"Error en debug: {e}")

    def _update_pagination_info(self):
        """Actualiza la información de paginación"""
        total = len(self.unidades_datos)
        if total == 0:
            self.info_label.setText("Sin códigos de barras registrados")
            self.page_info.setText("Página 0")
            self.btn_prev_page.setEnabled(False)
            self.btn_next_page.setEnabled(False)
            return
            
        start = self.current_page * self.page_size + 1
        end = min((self.current_page + 1) * self.page_size, total)
        max_page = (total - 1) // self.page_size + 1
        
        # Mostrar cuántos activos hay
        activos = sum(1 for u in self.unidades_datos if u.get("estado_raw") == "activo")
        
        self.info_label.setText(f"Mostrando {start}-{end} de {total} códigos ({activos} activos)")
        self.page_info.setText(f"Página {self.current_page + 1} de {max_page}")
        
        self.btn_prev_page.setEnabled(self.current_page > 0)
        self.btn_next_page.setEnabled(end < total)

    def _prev_page(self):
        """Página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self._actualizar_tabla()

    def _next_page(self):
        """Página siguiente"""
        max_page = (len(self.unidades_datos) - 1) // self.page_size
        if self.current_page < max_page:
            self.current_page += 1
            self._actualizar_tabla()

    def _actualizar_datos(self):
        """Actualiza los datos o procesa cambios según si hay cambios realizados"""
        try:
            if self.cambios_realizados:
                # Procesar cambios de fechas
                print(f"Procesando {len(self.cambios_realizados)} cambios de fechas")
                
                # Mostrar resumen de cambios al usuario
                cambios_texto = []
                for cambio in self.cambios_realizados:
                    codigo = cambio.get("codigo", "N/A")
                    fecha_original = cambio.get("fecha_original") or "Sin fecha"
                    nueva_fecha = cambio.get("nueva_fecha") or "Sin fecha"
                    cambios_texto.append(f"• {codigo}: {fecha_original} → {nueva_fecha}")
                
                # Mostrar mensaje de confirmación con detalles
                mensaje_confirmacion = f"¿Deseas guardar los siguientes cambios?\n\n"
                mensaje_confirmacion += "\n".join(cambios_texto[:10])  # Mostrar máximo 10
                if len(cambios_texto) > 10:
                    mensaje_confirmacion += f"\n... y {len(cambios_texto) - 10} cambios más"
                
                reply = QMessageBox.question(
                    self,
                    "Confirmar cambios de fechas",
                    mensaje_confirmacion,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Procesar cambios usando el backend
                    self._procesar_cambios_fechas()
                else:
                    # Cancelar cambios
                    self.cambios_realizados.clear()
                    self._recargar_datos_sin_cambios()
                    print("Cambios cancelados por el usuario")
            else:
                # No hay cambios: simplemente recargar datos
                self._recargar_datos_sin_cambios()
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            self._mostrar_error(f"Error al actualizar datos: {e}")

    def _procesar_cambios_fechas(self):
        """Procesa los cambios de fechas usando el backend"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(0)  # Modo indeterminado
            
            # Validar que todos los cambios tengan unidad_id
            cambios_validos = []
            cambios_invalidos = []
            
            for cambio in self.cambios_realizados:
                if cambio.get("unidad_id"):
                    cambios_validos.append(cambio)
                else:
                    cambios_invalidos.append(cambio.get("codigo", "N/A"))
            
            if cambios_invalidos:
                self._mostrar_advertencia(
                    f"Se omitirán {len(cambios_invalidos)} cambios sin ID de unidad válido"
                )
            
            if not cambios_validos:
                self._mostrar_error("No hay cambios válidos para procesar")
                self.progress_bar.setVisible(False)
                return
            
            # Procesar cambios usando el backend
            resultado = actualizar_fechas_vencimiento_lote_controller(cambios_validos)
            
            self.progress_bar.setVisible(False)
            
            # Mostrar resultado
            exitosos = resultado.get("exitosos", 0)
            fallidos = resultado.get("fallidos", 0)
            errores = resultado.get("errores", [])
            
            if exitosos > 0 and fallidos == 0:
                self._mostrar_info(f"Se actualizaron {exitosos} fechas de vencimiento correctamente")
                self.cambios_realizados.clear()
                self._recargar_datos_sin_cambios()
            elif exitosos > 0 and fallidos > 0:
                mensaje = f"Proceso parcial:\n"
                mensaje += f"• {exitosos} fechas actualizadas correctamente\n"
                mensaje += f"• {fallidos} fechas fallaron\n\n"
                if errores:
                    mensaje += "Errores:\n" + "\n".join(errores[:5])
                    if len(errores) > 5:
                        mensaje += f"\n... y {len(errores) - 5} errores más"
                
                self._mostrar_advertencia(mensaje)
                # Recargar datos para ver los cambios aplicados
                self._recargar_datos_sin_cambios()
            else:
                mensaje = f"No se pudo actualizar ninguna fecha\n\n"
                if errores:
                    mensaje += "Errores:\n" + "\n".join(errores[:5])
                self._mostrar_error(mensaje)
            
        except ImportError:
            self.progress_bar.setVisible(False)
            self._mostrar_error("Error: No se encontraron las funciones del backend. Asegúrate de que estén implementadas en controller.py")
        except Exception as e:
            self.progress_bar.setVisible(False)
            self._mostrar_error(f"Error al procesar cambios: {e}")
            print(f"Error detallado al procesar cambios: {e}")

    def _recargar_datos_sin_cambios(self):
        """Recarga los datos desde la base de datos"""
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(0)  # Modo indeterminado
            
            # Limpiar cambios y widgets
            self.cambios_realizados.clear()
            self.fecha_widgets.clear()
            
            # Recargar datos del producto
            self._cargar_datos_producto()
            
            # Recargar unidades
            self._cargar_unidades()
            
            self.progress_bar.setVisible(False)
            self._mostrar_info("Datos actualizados correctamente")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self._mostrar_error(f"Error al recargar datos: {e}")

    def _exportar_lista(self):
        """Exporta la lista de unidades a un archivo"""
        if not self.unidades_datos:
            self._mostrar_advertencia("No hay datos para exportar")
            return
            
        try:
            # Crear contenido de exportación
            contenido = [f"CÓDIGOS DE BARRAS - {self.nombre_producto}"]
            contenido.append("=" * 60)
            contenido.append(f"Producto: {self.producto_info.get('nombre', 'N/A')}")
            contenido.append(f"Stock actual: {self.producto_info.get('stock', 0)} {self.producto_info.get('unidad_medida', 'unidades')}")
            contenido.append(f"Total de códigos: {len(self.unidades_datos)}")
            
            activos = sum(1 for u in self.unidades_datos if u.get("estado_raw") == "activo")
            contenido.append(f"Códigos activos: {activos}")
            contenido.append("")
            
            contenido.append("LISTADO DE CÓDIGOS:")
            contenido.append("-" * 60)
            
            for i, unidad in enumerate(self.unidades_datos, 1):
                contenido.append(f"{i:3d}. {unidad['codigo']}")
                contenido.append(f"     Vencimiento: {unidad['vencimiento_display']}")
                contenido.append(f"     Estado: {unidad['estado']}")
                if unidad.get('observaciones'):
                    contenido.append(f"     Observaciones: {unidad['observaciones']}")
                contenido.append("")
            
            # Guardar archivo
            nombre_archivo = f"codigos_{self.nombre_producto.replace(' ', '_')}.txt"
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(contenido))
            
            self._mostrar_info(f"Lista exportada como: {nombre_archivo}")
            
        except Exception as e:
            self._mostrar_error(f"Error al exportar: {e}")

    def _mostrar_error(self, mensaje):
        """Muestra un mensaje de error"""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Critical)
        box.setWindowTitle("Error")
        box.setText(mensaje)
        box.setStyleSheet(self._get_message_box_style())
        box.exec()

    def _mostrar_advertencia(self, mensaje):
        """Muestra un mensaje de advertencia"""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Advertencia")
        box.setText(mensaje)
        box.setStyleSheet(self._get_message_box_style())
        box.exec()

    def _mostrar_info(self, mensaje):
        """Muestra un mensaje informativo"""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Information)
        box.setWindowTitle("Información")
        box.setText(mensaje)
        box.setStyleSheet(self._get_message_box_style())
        box.exec()

    def _get_message_box_style(self):
        """Retorna el estilo para los message boxes"""
        return """
            QMessageBox { 
                background: #ffffff; 
            }
            QMessageBox QLabel { 
                color: #111111; 
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
                padding: 4px 12px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover { 
                background: #e9e9e9; 
            }
            QMessageBox QPushButton:pressed { 
                background: #e0e0e0; 
            }
        """