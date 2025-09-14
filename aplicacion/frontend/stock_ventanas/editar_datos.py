# stock_ventanas/editar_datos.py
from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QComboBox, QRadioButton, QButtonGroup, QMessageBox
)

# Imports para integración con backend
from aplicacion.backend.stock import controller


class EditarDatosProductoDialog(QDialog):
    """Ventana para editar los datos básicos de un producto"""
    
    def __init__(self, parent=None, producto_nombre=None):
        super().__init__(parent)
        self.producto_nombre = producto_nombre
        self.producto_data = {}
        
        self.setWindowTitle("EDITAR DATOS DEL PRODUCTO")
        self.setModal(True)
        self.setMinimumSize(720, 560)
        
        # Cargar datos del JSON antes de construir la UI
        self._cargar_datos_desde_json()
        
        self._build_ui()
        self._cargar_datos_existentes()
        
    def _cargar_datos_desde_json(self):
        """Carga los datos del producto desde el archivo JSON"""
        try:
            # Obtener la ruta del archivo JSON
            base_dir = Path(__file__).resolve().parent.parent.parent
            json_path = base_dir / "frontend" / "json" / "stock.json"
            
            if not json_path.exists():
                print(f"Archivo JSON no encontrado en: {json_path}")
                return
                
            with open(json_path, 'r', encoding='utf-8') as file:
                productos = json.load(file)
                
            # Buscar el producto por nombre
            for producto in productos:
                if producto.get("nombre") == self.producto_nombre:
                    self.producto_data = producto
                    print(f"✅ Datos cargados para: {self.producto_nombre}")
                    print(f"🔍 ID del producto: {self.producto_data.get('id')}")
                    return
                    
            print(f"❌ Producto no encontrado: {self.producto_nombre}")
            
        except Exception as e:
            print(f"Error cargando datos del JSON: {e}")
            
    def _parsear_precio(self, precio_str):
        """Convierte '$2.000,00' a float 2000.0"""
        if not precio_str:
            return 0.0
        try:
            # Remover $ y espacios, reemplazar , por .
            clean = precio_str.replace('$', '').replace(' ', '').replace('.', '').replace(',', '.')
            return float(clean)
        except:
            return 0.0
            
    def _formatear_margen(self, margen_decimal):
        """Convierte 0.44 a 44.0"""
        if margen_decimal is None:
            return 0.0
        try:
            return float(margen_decimal) * 100
        except:
            return 0.0
    
    def _build_ui(self):
        # Layout principal
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        
        # Título
        title = QLabel("EDITAR DATOS DEL PRODUCTO")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #22C55E;")
        root.addWidget(title)
        
        # Frame principal
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
        
        # Contenido del formulario
        self._build_form_content(frame_l)
        
        # Footer con botones
        self._build_footer(frame_l)
    
    def _build_form_content(self, parent_layout):
        """Construye el formulario igual al de agregar producto pero sin códigos de barras"""
        
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
                font-size: 12pt;
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
        parent_layout.addWidget(box, 1)

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

        # Categoría - cargar desde base de datos (simulado por ahora)
        self.combo_categoria = QComboBox()
        self._cargar_categorias()
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

        # Fila margen
        fila_m = QHBoxLayout()
        fila_m.setSpacing(8)

        lbl_m = QLabel("Margen de ganancia:")
        lbl_m.setProperty("role", "formLabel")
        lbl_m.setStyleSheet("font-size: 12px;")  # asegura el tamaño en esa label

        fila_m.addWidget(lbl_m)
        fila_m.addWidget(self.radio_margen)
        fila_m.addWidget(self.edit_margen)
        fila_m.addSpacing(6)

        pill = QLabel("Ingrese porcentaje ejemp: 10%")
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setStyleSheet("""
            color: #777; 
            background: #f0f0f0; 
            padding: 4px 8px; 
            border-radius: 6px;
        """)
        fila_m.addWidget(pill)
        fila_m.addStretch()
        gl.addLayout(fila_m)

        # Fila precio directo
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

        # Proveedor - cargar desde base de datos (simulado por ahora)
        self.combo_proveedor = QComboBox()
        self._cargar_proveedores()
        gl.addLayout(self._row_custom("Proveedor", self.combo_proveedor, w=240))

    def _row_label_input(self, label_text: str, attr_name: str, width: int = 260):
        """Crea una fila con label e input"""
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
        """Crea una fila con label y widget personalizado"""
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
        """Alterna entre usar margen o precio directo"""
        self.edit_margen.setEnabled(use_margen)
        self.edit_precio_venta.setEnabled(not use_margen)

    def _build_footer(self, parent_layout):
        """Construye el footer con botones"""
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(20)
        footer_layout.addStretch()

        # Botón CANCELAR
        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setFixedHeight(44)
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background:#EF4444;
                color:white;
                border:none;
                border-radius:22px;
                padding:0 24px;
                font-weight:bold;
            } 
            QPushButton:hover {
                background:#DC2626;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)

        # Botón GUARDAR
        self.btn_guardar = QPushButton("GUARDAR CAMBIOS")
        self.btn_guardar.setFixedHeight(44)
        self.btn_guardar.setStyleSheet("""
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
        self.btn_guardar.clicked.connect(self._on_guardar_cambios)

        footer_layout.addWidget(self.btn_cancelar)
        footer_layout.addWidget(self.btn_guardar)
        parent_layout.addLayout(footer_layout)

    def _cargar_categorias(self):
        """Carga las categorías disponibles desde el backend"""
        try:
            categorias = controller.listar_clasificaciones_controller()
            self.combo_categoria.addItem("sin categoría", None)
            for cat in categorias:
                self.combo_categoria.addItem(cat.nombre, cat.id)
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            # Fallback a datos simulados
            self.combo_categoria.addItem("sin categoría", None)
            self.combo_categoria.addItem("Electrónicos", 1)
            self.combo_categoria.addItem("Ropa", 2)
            self.combo_categoria.addItem("Alimentación", 3)
            self.combo_categoria.addItem("Hogar", 4)

    def _cargar_proveedores(self):
        """Carga los proveedores disponibles desde el backend"""
        try:
            proveedores = controller.listar_proveedores_controller()
            self.combo_proveedor.addItem("sin proveedor", None)
            for prov in proveedores:
                self.combo_proveedor.addItem(prov.nombre, prov.id)
        except Exception as e:
            print(f"Error cargando proveedores: {e}")
            # Fallback a datos simulados
            self.combo_proveedor.addItem("sin proveedor", None)
            self.combo_proveedor.addItem("Proveedor A", 1)
            self.combo_proveedor.addItem("Proveedor B", 2)
            self.combo_proveedor.addItem("Distribuidora XYZ", 3)

    def _cargar_datos_existentes(self):
        """Carga los datos del producto existente en el formulario"""
        if not self.producto_data:
            print("No hay datos del producto para cargar")
            return
            
        print(f"🔍 Cargando datos: {self.producto_data}")
            
        # Cargar nombre
        if "nombre" in self.producto_data:
            self.edit_nombre.setText(self.producto_data["nombre"])
            
        # Cargar costo (parsear desde formato "$2.000,00")
        if "costo" in self.producto_data:
            costo_num = self._parsear_precio(self.producto_data["costo"])
            self.edit_costo.setText(str(costo_num))
            
        # Determinar tipo de unidad basado en si el stock es entero o decimal
        stock_val = float(self.producto_data.get("stock", 0))
        if stock_val == int(stock_val):
            self.combo_unidad.setCurrentText("unidades")
        else:
            self.combo_unidad.setCurrentText("kilogramos")
                
        # Cargar margen (convertir 0.44 a 44%)
        if "margen" in self.producto_data and self.producto_data["margen"] is not None:
            margen_porcentaje = self._formatear_margen(self.producto_data["margen"])
            self.radio_margen.setChecked(True)
            self.edit_margen.setText(str(margen_porcentaje))
            self._toggle_margen_precio(True)
        else:
            # Si no hay margen, usar precio directo
            if "precio" in self.producto_data:
                precio_num = self._parsear_precio(self.producto_data["precio"])
                self.radio_precio.setChecked(True)
                self.edit_precio_venta.setText(str(precio_num))
                self._toggle_margen_precio(False)
            
        # Cargar categoría
        categoria = self.producto_data.get("categoria", "sin_categoria")
        # Mapear nombres de categorías del JSON a nombres amigables
        categoria_map = {
            "sin_categoria": "sin categoría",
            "electronicos": "Electrónicos", 
            "ropa": "Ropa",
            "alimentacion": "Alimentación",
            "hogar": "Hogar"
        }
        categoria_amigable = categoria_map.get(categoria, categoria)
        
        for i in range(self.combo_categoria.count()):
            if self.combo_categoria.itemText(i) == categoria_amigable:
                self.combo_categoria.setCurrentIndex(i)
                break
                
        # Proveedor - por ahora mantener "sin proveedor" hasta que tengamos esa info en el JSON
        self.combo_proveedor.setCurrentIndex(0)  # "sin proveedor"

    def _validar_formulario(self) -> bool:
        """Valida que todos los campos obligatorios estén completos"""
        nombre = self.edit_nombre.text().strip()
        if not nombre:
            return self._mostrar_error("El nombre es obligatorio.")

        if self.edit_costo.text().strip() == "":
            return self._mostrar_error("El costo es obligatorio.")
        
        try:
            float(self.edit_costo.text())
        except ValueError:
            return self._mostrar_error("El costo debe ser un número válido.")

        if self.radio_margen.isChecked():
            if self.edit_margen.text().strip() == "":
                return self._mostrar_error("Ingresá un margen de ganancia (en %).")
            try:
                float(self.edit_margen.text())
            except ValueError:
                return self._mostrar_error("El margen debe ser un número válido.")
        else:
            if self.edit_precio_venta.text().strip() == "":
                return self._mostrar_error("Ingresá el precio de venta.")
            try:
                float(self.edit_precio_venta.text())
            except ValueError:
                return self._mostrar_error("El precio de venta debe ser un número válido.")

        return True

    def _recopilar_datos(self) -> dict:
        """Recopila todos los datos del formulario para el controller"""
        datos = {
            "nombre": self.edit_nombre.text().strip(),
            "costo_unitario": float(self.edit_costo.text()),
            "unidad_medida": self.combo_unidad.currentText(),
        }
        
        # Manejar categoría
        categoria_id = self.combo_categoria.currentData()
        if categoria_id is not None:
            datos["categoria_id"] = categoria_id
        
        # Manejar proveedor  
        proveedor_id = self.combo_proveedor.currentData()
        if proveedor_id is not None:
            datos["proveedor_id"] = proveedor_id
        
        # Manejar precio/margen
        if self.radio_margen.isChecked():
            # Convertir porcentaje a decimal (ej: 44% -> 0.44)
            margen_porcentaje = float(self.edit_margen.text())
            datos["margen_ganancia"] = margen_porcentaje / 100.0
        else:
            datos["precio_venta"] = float(self.edit_precio_venta.text())
            
        return datos

    def _on_guardar_cambios(self):
        """Maneja el click en guardar cambios"""
        if not self._validar_formulario():
            return
        
        # Verificar que tenemos el ID del producto
        producto_id = self.producto_data.get('id')
        if not producto_id:
            self._mostrar_error("Error: No se puede identificar el producto a editar.")
            return
            
        try:
            datos_nuevos = self._recopilar_datos()
            
            print("=== GUARDANDO EN BASE DE DATOS ===")
            print(f"ID del producto: {producto_id}")
            print(f"Datos a actualizar: {datos_nuevos}")
            
            # Llamar al controller para editar el producto
            producto_actualizado = controller.editar_producto_controller(producto_id, datos_nuevos)
            
            if producto_actualizado:
                print(f"✅ Producto actualizado exitosamente: {producto_actualizado.nombre}")
                
                # 🔄 ACTUALIZAR JSON Y PANTALLAS (igual que en agregar_producto_dialog.py)
                try:
                    from aplicacion.backend.stock.crud import exportar_productos_json
                    print("Generando JSON actualizado...")
                    
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
                            # Verificar timestamp y tamaño
                            timestamp = os.path.getmtime(json_path)
                            size = os.path.getsize(json_path)
                            print(f"📅 JSON actualizado: timestamp={time.ctime(timestamp)}, size={size} bytes")
                            
                            # Pausa adicional para asegurar que el archivo se escribió completamente
                            time.sleep(0.2)
                            
                            # **DOBLE ACTUALIZACIÓN** para productos editados
                            print("🔄 Iniciando actualización de pantallas...")
                            actualizacion_exitosa = self._actualizar_pantallas_relacionadas()
                            
                            if actualizacion_exitosa:
                                # Pausa y segunda actualización para asegurar
                                time.sleep(0.1)
                                print("🔄 Segunda actualización para garantizar consistencia...")
                                self._actualizar_pantallas_relacionadas()
                            
                        else:
                            print(f"❌ JSON no encontrado en {json_path}")
                            
                    else:
                        print("⚠️ Advertencia: No se pudo actualizar el JSON de stock")
                except Exception as e:
                    print(f"⚠️ Error al exportar JSON: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Mostrar mensaje de éxito
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Cambios guardados")
                msg.setText("Los datos del producto han sido actualizados exitosamente.")
                msg.setInformativeText(f"Producto: {producto_actualizado.nombre}")
                
                # Aplicar estilo claro al mensaje
                msg.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
                msg.setStyleSheet("""
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
                """)
                
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
                
                # Cerrar el diálogo
                self.accept()
                
            else:
                self._mostrar_error("Error: No se pudo actualizar el producto.")
                
        except Exception as e:
            error_msg = f"Error al guardar los cambios: {str(e)}"
            print(f"❌ {error_msg}")
            self._mostrar_error(error_msg)

    def _mostrar_error(self, mensaje: str) -> bool:
        """Muestra un mensaje de error"""
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Error")
        box.setText(mensaje)

        # Aplicar estilo claro
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
        """)

        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.exec()
        return False

    def _confirmar_cancelar(self):
        """Muestra confirmación antes de cancelar"""
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Icon.Question)
        reply.setWindowTitle("Confirmar cancelación")
        reply.setText("¿Estás seguro que querés cancelar la edición?")
        reply.setInformativeText("Los cambios no guardados se perderán.")
        
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
        no_button = reply.addButton("No, continuar editando", QMessageBox.ButtonRole.NoRole)
        
        # Establecer el botón "No" como predeterminado (más seguro)
        reply.setDefaultButton(no_button)
        
        # Ejecutar el diálogo y verificar la respuesta
        reply.exec()
        
        if reply.clickedButton() == si_button:
            # Usuario confirmó la cancelación
            print("🚪 Usuario canceló la edición")
            self.reject()  # Cerrar diálogo
        else:
            # Usuario decidió continuar
            print("📝 Usuario continúa editando")

    def closeEvent(self, event):
        """
        Sobrescribe el evento de cierre para mostrar confirmación
        """
        reply = QMessageBox(self)
        reply.setIcon(QMessageBox.Icon.Question)
        reply.setWindowTitle("Confirmar cierre")
        reply.setText("¿Estás seguro que querés cancelar la edición?")
        reply.setInformativeText("Los cambios no guardados se perderán.")
        
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
        no_button = reply.addButton("No, continuar editando", QMessageBox.ButtonRole.NoRole)
        
        # Establecer el botón "No" como predeterminado (más seguro)
        reply.setDefaultButton(no_button)
        
        # Ejecutar el diálogo y verificar la respuesta
        reply.exec()
        
        if reply.clickedButton() == si_button:
            # Usuario confirmó el cierre
            event.accept()  # Permitir cerrar la ventana
            print("🚪 Usuario canceló la edición")
        else:
            # Usuario decidió continuar editando
            event.ignore()  # Ignorar el evento de cierre
            print("📝 Usuario continúa editando")

    def _actualizar_pantallas_relacionadas(self):
        """
        Actualiza las pantallas de productos y ventas si están disponibles.
        Copiado desde agregar_producto_dialog.py para mantener consistencia.
        """
        try:
            # Buscar en la jerarquía de widgets para encontrar ProductosScreen y VentasTab
            widget_actual = self.parent()
            productos_actualizado = False
            ventas_actualizado = False
            
            print("🔍 Buscando pantallas para actualizar...")
            
            # Recorrer hacia arriba en la jerarquía
            while widget_actual is not None:
                # Verificar si es ProductosScreen directamente
                if hasattr(widget_actual, 'reload_data') and hasattr(widget_actual, 'products_table'):
                    print("🔄 Actualizando tabla de productos...")
                    widget_actual.reload_data()
                    productos_actualizado = True
                    print("✅ Tabla de productos actualizada")
                
                # Verificar si es VentasTab directamente
                if hasattr(widget_actual, 'reload_data') and hasattr(widget_actual, 'search_input'):
                    print("🔄 Actualizando datos de ventas...")
                    widget_actual.reload_data()
                    ventas_actualizado = True
                    print("✅ Datos de ventas actualizados")
                
                # Si es un contenedor, buscar en sus hijos
                if hasattr(widget_actual, 'findChildren'):
                    try:
                        # Buscar ProductosScreen
                        from aplicacion.frontend.stock_ventanas.productos import ProductosScreen
                        productos_screens = widget_actual.findChildren(ProductosScreen)
                        if productos_screens and not productos_actualizado:
                            print(f"🔄 Encontrados {len(productos_screens)} ProductosScreen, actualizando...")
                            productos_screens[0].reload_data()
                            productos_actualizado = True
                            print("✅ Tabla de productos actualizada (findChildren)")
                    except ImportError:
                        pass  # Si no se puede importar, continuar
                    
                    try:
                        # Buscar VentasTab
                        from aplicacion.frontend.ventas import VentasTab
                        ventas_tabs = widget_actual.findChildren(VentasTab)
                        if ventas_tabs and not ventas_actualizado:
                            print(f"🔄 Encontrados {len(ventas_tabs)} VentasTab, actualizando...")
                            ventas_tabs[0].reload_data()
                            ventas_actualizado = True
                            print("✅ Datos de ventas actualizados (findChildren)")
                    except ImportError:
                        pass  # Si no se puede importar, continuar
                
                # Si ya actualizamos ambos, podemos parar
                if productos_actualizado and ventas_actualizado:
                    print("🎯 Ambas pantallas actualizadas exitosamente")
                    break
                
                # Subir un nivel en la jerarquía
                widget_actual = widget_actual.parent() if hasattr(widget_actual, 'parent') else None
            
            if not productos_actualizado:
                print("⚠️ No se encontró la tabla de productos para actualizar")
            if not ventas_actualizado:
                print("⚠️ No se encontró la pantalla de ventas para actualizar")
                
            resultado = productos_actualizado and ventas_actualizado
            print(f"📊 Resultado actualización: productos={productos_actualizado}, ventas={ventas_actualizado}, éxito_total={resultado}")
            return resultado
            
        except Exception as e:
            print(f"⚠️ Error al actualizar pantallas relacionadas: {e}")
            import traceback
            traceback.print_exc()
            return False