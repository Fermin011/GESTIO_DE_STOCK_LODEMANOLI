# aplicacion/frontend/stock_ventanas/agregar_stock.py
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QPushButton, QMessageBox
)

# Importar el controller del backend
from aplicacion.backend.stock.controller import agregar_stock_controller, obtener_producto_controller
from aplicacion.backend.stock.controller import modificar_stock_controller, obtener_producto_controller


class ModificarStockDialog(QDialog):
    """
    Ventana emergente para cambiar el stock de un producto.
    Ahora guarda los cambios en la base de datos usando el backend.
    """
    def __init__(self, parent=None, id_producto: int = None, nombre_producto: str = "", stock_actual: Optional[float] = None):
        super().__init__(parent)
        self.setModal(True)
        self.setWindowTitle("Editar producto")
        self.setFixedSize(720, 520)

        self._nuevo_stock: Optional[float] = None
        self._id_producto = id_producto
        self._nombre = nombre_producto
        self._stock_actual = stock_actual
        self._stock_guardado = False  # Flag para saber si se guardó exitosamente

        self._build_ui()

    # ---------------- UI ----------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Título grande (verde)
        title = QLabel("EDITAR PRODUCTO")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Arial", 24, QFont.Weight.Black))
        title.setStyleSheet("color: #22C55E;")  # verde
        root.addWidget(title)

        # Mostrar nombre del producto si está disponible
        if self._nombre:
            product_label = QLabel(f"Producto: {self._nombre}")
            product_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            product_label.setFont(QFont("Arial", 14, QFont.Weight.Normal))
            product_label.setStyleSheet("color: #666666; margin: 10px 0;")
            root.addWidget(product_label)

        # Marco exterior gris
        outer = QFrame()
        outer.setObjectName("outer")
        outer.setStyleSheet("""
            QFrame#outer {
                background-color: #4A4A4A;
                border: 2px solid #5A5A5A;
                border-radius: 18px;
            }
        """)
        root.addWidget(outer, 1)

        outer_l = QVBoxLayout(outer)
        outer_l.setContentsMargins(26, 26, 26, 26)
        outer_l.setSpacing(22)

        # Card blanca interna
        card = QFrame()
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: #FFFFFF;
                border: 2px solid #D0D0D0;
                border-radius: 16px;
            }
        """)
        outer_l.addWidget(card, 1)

        card_l = QHBoxLayout(card)
        card_l.setContentsMargins(28, 28, 28, 28)
        card_l.setSpacing(20)

        # Mostrar stock actual
        if self._stock_actual is not None:
            stock_actual_label = QLabel(f"Stock actual: {self._stock_actual}")
            stock_actual_label.setStyleSheet("color: #888888; font-size: 14px;")
            stock_actual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            outer_l.insertWidget(0, stock_actual_label)

        # Label "STOCK:"
        lbl = QLabel("NUEVO STOCK:")
        lbl.setStyleSheet("color: #111111;")
        lbl.setFont(QFont("Arial", 20, QFont.Weight.Black))
        card_l.addWidget(lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        # Input numérico
        self.txt_stock = QLineEdit()
        self.txt_stock.setValidator(QDoubleValidator(0.0, 10_000_000.0, 3))
        self.txt_stock.setFixedSize(140, 52)
        self.txt_stock.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.txt_stock.setStyleSheet("""
            QLineEdit {
                color: #111111; background: #FFFFFF;
                border: 2px solid #6A6A6A; border-radius: 12px;
                font-size: 20px; padding: 6px 10px;
            }
            QLineEdit:focus { border: 2px solid #21AFBD; }
        """)
        if self._stock_actual is not None:
            self.txt_stock.setText(str(self._stock_actual))
        card_l.addWidget(self.txt_stock, 0, Qt.AlignmentFlag.AlignVCenter)

        # Ayuda a la derecha (gris clarito)
        helper = QLabel("en unidades o kilos\nsegún corresponda")
        helper.setStyleSheet("color: #888888;")
        helper.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        card_l.addWidget(helper, 1)

        # Botonera inferior
        btns = QHBoxLayout()
        btns.setContentsMargins(6, 0, 6, 0)
        btns.setSpacing(24)

        btn_cancel = QPushButton("CANCELAR")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setFixedSize(280, 70)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B; color: #0B0B0B;
                border: 2px solid #E94C4C; border-radius: 32px;
                font-weight: 900; font-size: 18px;
            }
            QPushButton:hover { background-color: #FF8383; }
            QPushButton:pressed { background-color: #E94C4C; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("GUARDAR")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.setFixedSize(280, 70)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71; color: #0B0B0B;
                border: 2px solid #27AE60; border-radius: 32px;
                font-weight: 900; font-size: 18px;
            }
            QPushButton:hover { background-color: #45D882; }
            QPushButton:pressed { background-color: #27AE60; }
        """)
        btn_ok.clicked.connect(self._accept_form)

        btns.addStretch(1)
        btns.addWidget(btn_cancel)
        btns.addWidget(btn_ok)
        btns.addStretch(1)

        outer_l.addLayout(btns)

    # ------------- API -------------

    def _accept_form(self):
        """Guarda el nuevo stock en la base de datos"""
        if self._id_producto is None:
            self._mostrar_error("Error", "No se puede actualizar: ID de producto no válido.")
            return

        text = self.txt_stock.text().strip()
        if text == "":
            self._mostrar_error("Error", "Debe ingresar un valor de stock válido.")
            return

        try:
            nuevo_stock = float(text)
            if nuevo_stock < 0:
                self._mostrar_error("Error", "El stock no puede ser negativo.")
                return
        except ValueError:
            self._mostrar_error("Error", "Debe ingresar un número válido.")
            return

        # Verificar si el producto existe y obtener stock actual real
        try:
            producto_actual = obtener_producto_controller(self._id_producto)
            if not producto_actual:
                self._mostrar_error("Error", "No se encontró el producto en la base de datos.")
                return
                
            stock_actual_real = producto_actual.cantidad or 0
            
        except Exception as e:
            self._mostrar_error("Error", f"Error al verificar el producto: {str(e)}")
            return

        # Calcular la diferencia (puede ser positiva o negativa)
        diferencia = nuevo_stock - stock_actual_real

        # Si no hay cambios, solo cerrar
        if diferencia == 0:
            self._mostrar_info("Sin cambios", "El stock ya tiene el valor ingresado.")
            self._nuevo_stock = nuevo_stock
            self._stock_guardado = True
            self.accept()
            return

        # Confirmar el cambio con el usuario
        if diferencia > 0:
            mensaje = f"Se agregará {diferencia} unidades al stock.\n"
            mensaje += f"Stock actual: {stock_actual_real}\n"
            mensaje += f"Nuevo stock: {nuevo_stock}\n\n¿Confirmar?"
        else:
            mensaje = f"Se reducirá el stock en {abs(diferencia)} unidades.\n"
            mensaje += f"Stock actual: {stock_actual_real}\n"
            mensaje += f"Nuevo stock: {nuevo_stock}\n\n¿Confirmar?"

        respuesta = self._mostrar_confirmacion("Confirmar cambio", mensaje)
        if not respuesta:
            return

        # Intentar actualizar el stock usando la nueva función
        try:
            producto_actualizado = modificar_stock_controller(self._id_producto, diferencia)
            
            if producto_actualizado:
                self._nuevo_stock = producto_actualizado.cantidad
                self._stock_guardado = True
                
                print(f"Stock actualizado exitosamente: {producto_actualizado.nombre} -> {producto_actualizado.cantidad}")
                
                # Regenerar JSON y actualizar pantallas
                try:
                    from aplicacion.backend.stock.crud import exportar_productos_json
                    print("Generando JSON actualizado...")
                    
                    import time
                    time.sleep(0.2)
                    
                    json_exportado = exportar_productos_json()
                    if json_exportado:
                        print("JSON de stock actualizado exitosamente")
                        
                        # Verificar que el archivo realmente se escribió
                        import os
                        from pathlib import Path
                        base_dir = Path(__file__).resolve().parent.parent.parent
                        json_path = base_dir / "frontend" / "json" / "stock.json"
                        
                        if json_path.exists():
                            timestamp = os.path.getmtime(json_path)
                            size = os.path.getsize(json_path)
                            print(f"JSON actualizado: timestamp={time.ctime(timestamp)}, size={size} bytes")
                            
                            time.sleep(0.2)
                            
                            print("Iniciando actualización de pantallas...")
                            actualizacion_exitosa = self._actualizar_pantallas_relacionadas()
                            
                            if actualizacion_exitosa:
                                print("Pantallas actualizadas exitosamente")
                            
                        else:
                            print(f"JSON no encontrado en {json_path}")
                            
                    else:
                        print("Advertencia: No se pudo actualizar el JSON de stock")
                except Exception as e:
                    print(f"Error al exportar JSON: {e}")
                    import traceback
                    traceback.print_exc()
                
                self._mostrar_info("Éxito", 
                    f"Stock actualizado correctamente.\n"
                    f"Nuevo stock: {producto_actualizado.cantidad} {producto_actualizado.unidad_medida}")
                self.accept()
            else:
                self._mostrar_error("Error", "No se pudo actualizar el stock. Producto no encontrado.")
                
        except ValueError as ve:
            # Error específico para stock negativo
            self._mostrar_error("Stock insuficiente", str(ve))
        except Exception as e:
            self._mostrar_error("Error", f"Error al actualizar el stock: {str(e)}")

    def _mostrar_error(self, titulo: str, mensaje: str):
        """Muestra un mensaje de error"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.exec()

    def _mostrar_info(self, titulo: str, mensaje: str):
        """Muestra un mensaje de información"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.exec()

    def _mostrar_confirmacion(self, titulo: str, mensaje: str) -> bool:
        """Muestra un mensaje de confirmación y retorna True si el usuario acepta"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(titulo)
        msg_box.setText(mensaje)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        return msg_box.exec() == QMessageBox.StandardButton.Yes

    def get_nuevo_stock(self) -> Optional[float]:
        """Devuelve el valor del nuevo stock si se guardó exitosamente."""
        return self._nuevo_stock if self._stock_guardado else None

    def fue_guardado(self) -> bool:
        """Retorna True si el stock fue guardado exitosamente en la base de datos."""
        return self._stock_guardado

    def _actualizar_pantallas_relacionadas(self):
        """
        Actualiza las pantallas de productos y ventas si están disponibles.
        Copiado desde editar_datos.py para mantener consistencia.
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
                
            resultado = productos_actualizado or ventas_actualizado  # Al menos una debe actualizarse
            print(f"📊 Resultado actualización: productos={productos_actualizado}, ventas={ventas_actualizado}, éxito={resultado}")
            return resultado
            
        except Exception as e:
            print(f"⚠️ Error al actualizar pantallas relacionadas: {e}")
            import traceback
            traceback.print_exc()
            return False