# stock_ventanas/editar_producto_dialog.py
from __future__ import annotations

import json
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)

# Importar la nueva clase separada
from .editar_datos import EditarDatosProductoDialog
# Importar el diálogo de ver stock
from .ver_stock import VerStockDialog
from .agregar_stock import ModificarStockDialog


class EditarProductoDialog(QDialog):
    def __init__(self, parent=None, producto_data=None):
        super().__init__(parent)
        self.producto_data = producto_data or {}
        self.selected_action = None
        self.datos_originales = None  # Variable para almacenar los datos originales
        
        self.setWindowTitle("EDITAR PRODUCTO")
        self.setModal(True)
        self.setFixedSize(520, 450)
        
        self._cargar_datos_originales()
        self._build_ui()
        
    def _cargar_datos_originales(self):
        """Carga los datos originales del producto desde stock.json"""
        try:
            nombre_producto = self.producto_data.get("nombre", "")
            if not nombre_producto:
                return
            
            # Ruta al archivo stock.json
            stock_path = os.path.join("aplicacion", "frontend", "json", "stock.json")
            
            if not os.path.exists(stock_path):
                print(f"No se encontró el archivo: {stock_path}")
                return
            
            with open(stock_path, 'r', encoding='utf-8') as file:
                productos = json.load(file)
            
            # Buscar el producto por nombre
            for producto in productos:
                if producto.get("nombre") == nombre_producto:
                    self.datos_originales = producto.copy()
                    break
            
            if self.datos_originales is None:
                print(f"No se encontró el producto: {nombre_producto}")
                
        except Exception as e:
            print(f"Error al cargar datos originales: {e}")
    
    def _obtener_datos_actuales(self):
        """Obtiene los datos actuales del producto desde stock.json"""
        try:
            nombre_producto = self.producto_data.get("nombre", "")
            if not nombre_producto:
                return None
            
            # Ruta al archivo stock.json
            stock_path = os.path.join("aplicacion", "frontend", "json", "stock.json")
            
            if not os.path.exists(stock_path):
                return None
            
            with open(stock_path, 'r', encoding='utf-8') as file:
                productos = json.load(file)
            
            # Buscar el producto por nombre
            for producto in productos:
                if producto.get("nombre") == nombre_producto:
                    return producto
            
            return None
            
        except Exception as e:
            print(f"Error al obtener datos actuales: {e}")
            return None
    
    def _comparar_cambios(self):
        """Compara los datos originales con los actuales y retorna los cambios"""
        if self.datos_originales is None:
            return None
        
        datos_actuales = self._obtener_datos_actuales()
        if datos_actuales is None:
            return None
        
        cambios = []
        
        # Campos a comparar
        campos_importantes = ['nombre', 'categoria', 'stock', 'costo', 'precio', 'estado', 'margen']
        
        for campo in campos_importantes:
            valor_original = self.datos_originales.get(campo)
            valor_actual = datos_actuales.get(campo)
            
            if valor_original != valor_actual:
                cambios.append(f"{campo}: {valor_original} → {valor_actual}")
        
        return cambios
        
    def _build_ui(self):
        # Layout principal
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        
        # Título
        title = QLabel("EDITAR PRODUCTO")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #22C55E;")
        root.addWidget(title)
        
        # Frame principal oscuro
        main_frame = QFrame()
        main_frame.setObjectName("mainFrame")
        main_frame.setStyleSheet("""
            QFrame#mainFrame {
                background-color: #3f3f3f;
                border: 2px solid #5a5a5a;
                border-radius: 10px;
            }
        """)
        root.addWidget(main_frame, 1)
        
        main_layout = QVBoxLayout(main_frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Frame blanco contenedor de botones
        buttons_frame = QFrame()
        buttons_frame.setObjectName("buttonsFrame")
        buttons_frame.setStyleSheet("""
            QFrame#buttonsFrame {
                background-color: white;
                border-radius: 14px;
            }
        """)
        
        buttons_layout = QVBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(30, 30, 30, 30)
        buttons_layout.setSpacing(25)
        
        # Botón 1: EDITAR DATOS DEL PRODUCTO
        self.btn_editar_datos = QPushButton("EDITAR DATOS DEL PRODUCTO")
        self.btn_editar_datos.setText("EDITAR DATOS DEL PRODUCTO ")
        self.btn_editar_datos.setStyleSheet("background-color: #367B94; color: white; font-size: 20px;")
        self.btn_editar_datos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar_datos.clicked.connect(self._on_editar_datos)
        buttons_layout.addWidget(self.btn_editar_datos)
        
        # Botón 2: AUMENTAR O RESTAR STOCK
        self.btn_modificar_stock = QPushButton("AUMENTAR O RESTAR STOCK")
        self.btn_modificar_stock.setText("AUMENTAR O RESTAR STOCK ")
        self.btn_modificar_stock.setStyleSheet("background-color: #367B94; color: white; font-size: 20px;")
        self.btn_modificar_stock.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_modificar_stock.clicked.connect(self._on_modificar_stock)
        buttons_layout.addWidget(self.btn_modificar_stock)
        
        # Botón 3: VER UNIDADES REGISTRADAS
        self.btn_ver_unidades = QPushButton("VER UNIDADES REGISTRADAS")
        self.btn_ver_unidades.setText("VER UNIDADES REGISTRADAS ")
        self.btn_ver_unidades.setStyleSheet("background-color: #367B94; color: white; font-size: 20px;")
        self.btn_ver_unidades.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_ver_unidades.clicked.connect(self._on_ver_unidades)
        buttons_layout.addWidget(self.btn_ver_unidades)
        
        # Agregar el frame de botones al layout principal
        main_layout.addWidget(buttons_frame, 1)
        
        # Sección inferior con botón CERRAR
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)
        
        # Botón CERRAR (Rojo)
        self.btn_cerrar = QPushButton("CERRAR")
        self.btn_cerrar.setFixedSize(160, 50)
        self.btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
            QPushButton:pressed {
                background-color: #B91C1C;
            }
        """)
        self.btn_cerrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cerrar.clicked.connect(self.reject)
        
        footer_layout.addStretch()
        footer_layout.addWidget(self.btn_cerrar)
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)
        
        # Si hay datos del producto, mostrarlos
        if self.producto_data:
            nombre_producto = self.producto_data.get("nombre", "Producto sin nombre")
            info_label = QLabel(f"Producto seleccionado: {nombre_producto}")
            info_label.setStyleSheet("""
                color: #9CA3AF;
                font-size: 12px;
                padding: 5px;
            """)
            info_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            root.insertWidget(1, info_label)
    
    def _on_editar_datos(self):
        """Abre la ventana de edición de datos del producto"""
        self.selected_action = "editar_datos"
        self._highlight_button(self.btn_editar_datos)
        
        # Obtener el nombre del producto para pasarlo al diálogo
        nombre_producto = self.producto_data.get("nombre", "")
        
        # Abrir la ventana de edición de datos
        dialog = EditarDatosProductoDialog(self, nombre_producto)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("Datos del producto editados exitosamente")
        
    def _on_modificar_stock(self):
            """Abrir la ventana visual para modificar el stock con ID del producto válido."""
            self.selected_action = "modificar_stock"
            self._highlight_button(self.btn_modificar_stock)

            # Obtener nombre del producto
            nombre_producto = self.producto_data.get("nombre", "")
            if not nombre_producto:
                self._mostrar_error("No se pudo obtener el nombre del producto.")
                return

            # Obtener datos actuales desde el JSON
            actual = self._obtener_datos_actuales()
            stock_actual = None
            producto_id = None
            
            if actual is not None:
                try:
                    stock_actual = float(actual.get("stock", 0))
                    # Intentar obtener ID desde el JSON
                    producto_id = actual.get("id")
                except (TypeError, ValueError):
                    stock_actual = None

            # Si no tenemos ID desde JSON, buscarlo en la base de datos
            if producto_id is None:
                try:
                    from aplicacion.backend.stock.controller import listar_productos_controller
                    print(f"Buscando ID del producto '{nombre_producto}' en la base de datos...")
                    
                    productos = listar_productos_controller()
                    for producto in productos:
                        if producto.nombre == nombre_producto:
                            producto_id = producto.id
                            # También actualizar stock_actual con el valor real de la BD
                            stock_actual = float(producto.cantidad) if producto.cantidad is not None else 0.0
                            print(f"Producto encontrado: ID={producto_id}, Stock={stock_actual}")
                            break
                    
                    if producto_id is None:
                        self._mostrar_error(f"No se encontró el producto '{nombre_producto}' en la base de datos.")
                        return
                        
                except Exception as e:
                    self._mostrar_error(f"Error al buscar el producto en la base de datos: {str(e)}")
                    print(f"Error detallado: {e}")
                    return

            # Crear el diálogo con todos los parámetros necesarios
            try:
                dlg = ModificarStockDialog(
                    parent=self, 
                    id_producto=producto_id,  # Ahora pasamos el ID
                    nombre_producto=nombre_producto, 
                    stock_actual=stock_actual
                )
                
                if dlg.exec() == QDialog.DialogCode.Accepted:
                    if dlg.fue_guardado():
                        nuevo_stock = dlg.get_nuevo_stock()
                        print(f"Stock actualizado exitosamente para '{nombre_producto}': {nuevo_stock}")
                        
                        # Actualizar los datos locales para reflejar el cambio
                        if actual is not None:
                            actual["stock"] = nuevo_stock
                        
                        self._mostrar_info(f"Stock actualizado correctamente.\n\nProducto: {nombre_producto}\nNuevo stock: {nuevo_stock}")
                    else:
                        print("Modificación de stock cancelada")
                else:
                    print("Diálogo de stock cerrado sin cambios")
                    
            except Exception as e:
                self._mostrar_error(f"Error al abrir el diálogo de modificar stock: {str(e)}")
                print(f"Error detallado al crear ModificarStockDialog: {e}")
    #        
    def _on_ver_unidades(self):
        """Maneja la acción de ver unidades registradas"""
        self.selected_action = "ver_unidades"
        self._highlight_button(self.btn_ver_unidades)
        
        try:
            # Obtener el nombre del producto
            nombre_producto = self.producto_data.get("nombre", "")
            
            if not nombre_producto:
                self._mostrar_error("No se pudo obtener el nombre del producto.")
                return
            
            # Verificar que el producto existe y tiene stock
            datos_actuales = self._obtener_datos_actuales()
            if datos_actuales is None:
                self._mostrar_error("No se pudo encontrar el producto en la base de datos.")
                return
            
            # Convertir stock a entero para evitar problemas con float
            stock_cantidad = datos_actuales.get('stock', 0)
            try:
                stock_cantidad = int(float(stock_cantidad))  # Convertir float a int
            except (ValueError, TypeError):
                stock_cantidad = 0
            
            if stock_cantidad <= 0:
                self._mostrar_advertencia(f"El producto '{nombre_producto}' no tiene unidades en stock para mostrar.")
                return
            
            print(f"Editando producto: {nombre_producto}")
            print(f"Stock detectado: {stock_cantidad} (tipo: {type(stock_cantidad)})")
            
            # Intentar abrir el diálogo con manejo de errores más específico
            try:
                print("Intentando crear VerStockDialog...")
                dialog = VerStockDialog(self, nombre_producto)
                print("VerStockDialog creado exitosamente")
                
                print("Intentando ejecutar dialog.exec()...")
                result = dialog.exec()
                print(f"Dialog ejecutado, resultado: {result}")
                
            except Exception as dialog_error:
                print(f"Error específico al crear/ejecutar VerStockDialog: {dialog_error}")
                print(f"Tipo de error: {type(dialog_error)}")
                import traceback
                print("Traceback completo:")
                traceback.print_exc()
                raise dialog_error
            
            # Si se hicieron cambios, podrías actualizar los datos locales aquí
            if result == QDialog.DialogCode.Accepted:
                print("Ventana de unidades cerrada con cambios guardados")
            else:
                print("Ventana de unidades cerrada sin cambios")
            
        except Exception as e:
            self._mostrar_error(f"Error al abrir la ventana de unidades: {e}")
            print(f"Editando producto: {nombre_producto}")
            print(f"Error detallado: {e}")
            print("Edición cancelada")
    
    def _highlight_button(self, selected_button):
        """Resalta el botón seleccionado con una paleta azul similar"""
        # Resetear todos los botones al estilo normal
        normal_style = "background-color: #367B94; color: white; font-size: 20px;"
        # Usar un azul más oscuro para la selección, manteniendo la paleta
        selected_style = "background-color: #2C5F7A; color: white; font-size: 20px; border: 3px solid #1E4A5F;"
        
        self.btn_editar_datos.setStyleSheet(normal_style)
        self.btn_modificar_stock.setStyleSheet(normal_style)
        self.btn_ver_unidades.setStyleSheet(normal_style)
        
        # Aplicar estilo de selección al botón clickeado
        selected_button.setStyleSheet(selected_style)
    
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