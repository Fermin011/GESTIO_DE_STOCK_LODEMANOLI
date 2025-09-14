from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFrame, QGridLayout, QGraphicsOpacityEffect, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtGui import QIcon
from pathlib import Path
from aplicacion.frontend.stock_ventanas.categorias import CategoriasScreen


BASE_DIR = Path(__file__).resolve().parent

class StockTab(QWidget):
    def __init__(self):
        super().__init__()

        self.stack = QStackedWidget()
        self.tabs = {}

        self.main_widget = QWidget()
        self.init_ui()

        self.stack.addWidget(self.main_widget)
        self.tabs["GESTION DE STOCK"] = {"widget": self.main_widget, "closeable": False}

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.create_tab_bar()
        main_layout.addWidget(self.tab_bar)
        main_layout.addWidget(self.stack)
        self._categorias_screen = None  


        self.setLayout(main_layout)

    def create_tab_bar(self):
        self.tab_bar = QFrame()
        self.tab_bar.setFixedHeight(50)
        self.tab_bar.setStyleSheet("""
            QFrame {
                background-color: #3C3C3C;
                border-bottom: 2px solid #2D2D2D;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)

        self.tab_layout = QHBoxLayout(self.tab_bar)
        self.tab_layout.setContentsMargins(10, 0, 10, 0)
        self.tab_layout.setSpacing(2)

        self.create_tab_button("GESTION DE STOCK", False)
        self.tab_layout.addStretch()

    def create_tab_button(self, name, closeable=True):
        tab_container = QFrame()
        tab_container.setFixedHeight(35)
        tab_container.setStyleSheet("""
            QFrame {
                background-color: #5A5A5A;
                border: 1px solid #6A6A6A;
                border-radius: 14px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #6A6A6A;
            }
        """)

        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(10, 5, 5, 5)
        tab_layout.setSpacing(5)

        tab_label = QLabel(name)
        tab_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
        """)
        tab_label.mousePressEvent = lambda event: self.switch_to_tab(name)
        tab_layout.addWidget(tab_label)

        if closeable:
            close_btn = QPushButton()
            close_btn.setFixedSize(20, 20)
            BASE_DIR = Path(__file__).resolve().parent
            close_btn.setIcon(QIcon(str(BASE_DIR / "iconos" / "close_black.png")))
            close_btn.setIconSize(close_btn.size())
            close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #FF4444; /* circulo rojo */
                }
            """)

            # Al hacer hover cambiamos el icono a blanco
            def enterEvent(e):
                close_btn.setIcon(QIcon(str(BASE_DIR / "iconos" / "close_white.png")))
            def leaveEvent(e):
                close_btn.setIcon(QIcon(str(BASE_DIR / "iconos" / "close_black.png")))

            close_btn.enterEvent = enterEvent
            close_btn.leaveEvent = leaveEvent

            close_btn.clicked.connect(lambda: self.close_tab(name))
            tab_layout.addWidget(close_btn)

        if name == "GESTION DE STOCK":
            self.set_active_tab(tab_container)

        if name not in self.tabs:
            self.tabs[name] = {}
        self.tabs[name]["tab_button"] = tab_container

        self.tab_layout.insertWidget(self.tab_layout.count() - 1, tab_container)

    def set_active_tab(self, active_tab):
        for tab_info in self.tabs.values():
            if "tab_button" in tab_info:
                tab_info["tab_button"].setStyleSheet("""
                    QFrame {
                        background-color: #5A5A5A;
                        border: 1px solid #6A6A6A;
                        border-radius: 14px;
                        margin: 2px;
                    }
                    QFrame:hover {
                        background-color: #6A6A6A;
                    }
                """)

        active_tab.setStyleSheet("""
            QFrame {
                background-color: #21ABDE;
                border: 1px solid #1B8BB4;
                border-radius: 14px;
                margin: 2px;
            }
        """)

    def switch_to_tab(self, tab_name):
        if tab_name in self.tabs and "widget" in self.tabs[tab_name]:
            widget = self.tabs[tab_name]["widget"]
            self.stack.setCurrentWidget(widget)
            self.set_active_tab(self.tabs[tab_name]["tab_button"])

    def close_tab(self, tab_name):
        if tab_name in self.tabs and self.tabs[tab_name].get("closeable", True):
            widget = self.tabs[tab_name]["widget"]
            self.stack.removeWidget(widget)
            widget.deleteLater()

            tab_button = self.tabs[tab_name]["tab_button"]
            self.tab_layout.removeWidget(tab_button)
            tab_button.deleteLater()

            del self.tabs[tab_name]
            self.switch_to_tab("GESTION DE STOCK")

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title_label = QLabel("GESTION DE STOCK")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #4A4A4A;
                border: 2px solid #5A5A5A;
                border-radius: 10px;
            }
        """)

        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)

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

        try:
            pixmap = QPixmap(str(BASE_DIR / "Lo de manoli.png"))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(54, 54, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                icon_label.setStyleSheet("""
                    QLabel {
                        background-color: #21AFBD;
                        border-radius: 30px;
                        border: 3px solid #FFFFFF;
                    }
                """)
        except Exception as e:
            print(f"Error al cargar 'Lo de manoli.png': {e}")
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #21AFBD;
                    border-radius: 30px;
                    border: 3px solid #FFFFFF;
                }
            """)

        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_container.addStretch()
        icon_container.addWidget(icon_label)
        icon_container.addStretch()

        buttons_layout = QGridLayout()
        buttons_layout.setHorizontalSpacing(220)
        buttons_layout.setVerticalSpacing(110)

        self.create_main_buttons(buttons_layout)

        content_layout.addLayout(icon_container)
        content_layout.addStretch()
        content_layout.addLayout(buttons_layout)
        content_layout.addStretch()

        main_layout.addWidget(title_label)
        main_layout.addWidget(content_frame)

        self.main_widget.setLayout(main_layout)

    def create_main_buttons(self, layout):
        buttons_data = [
            ("PRODUCTOS", 0, 0, "productos.png"),
            ("CATEGORIAS", 0, 1, "categorias.png"),
            ("PROVEEDORES", 1, 0, "proveedores.png"),
            ("VENCIMIENTOS", 1, 1, "vencimientos.png")
        ]

        button_width = 580
        button_height = 310

        for text, row, col, icon_file in buttons_data:
            button = QPushButton()
            button.setFixedSize(button_width, button_height)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #21ABDE;
                    border: 2px solid #1B8BB4;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #26C4FF;
                    border: 2px solid #21ABDE;
                }
                QPushButton:pressed {
                    background-color: #1B8BB4;
                    border: 2px solid #156A91;
                }
            """)

            icon_label = QLabel(button)
            try:
                icon_path = str(BASE_DIR / "iconos" / icon_file)
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    icon_label.resize(button.size())
                    opacity_effect = QGraphicsOpacityEffect()
                    opacity_effect.setOpacity(0.5)
                    icon_label.setGraphicsEffect(opacity_effect)
                    icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            except Exception as e:
                print(f"Error al cargar icono {icon_path}: {e}")

            text_label = QLabel(text, button)
            text_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            text_label.setStyleSheet("""
                QLabel {
                    color: black;
                    background-color: transparent;
                    border: none;
                }
            """)
            text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            text_label.setGeometry(0, button_height - 60, button_width, 50)
            text_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            if text == "PRODUCTOS":
                button.clicked.connect(self.open_productos)
            elif text == "CATEGORIAS":
                button.clicked.connect(self.open_categorias)
            elif text == "PROVEEDORES":
                button.clicked.connect(self.open_proveedores)
            elif text == "VENCIMIENTOS":
                button.clicked.connect(self.open_vencimientos)

            layout.addWidget(button, row, col)

        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 20, 50, 20)

    def open_productos(self):
        print("Abriendo gestion de productos...")
        if "PRODUCTOS" in self.tabs:
            self.switch_to_tab("PRODUCTOS")
        else:
            from aplicacion.frontend.stock_ventanas.productos import ProductosScreen
            productos_screen = ProductosScreen()
            self.stack.addWidget(productos_screen)
            self.create_tab_button("PRODUCTOS", True)
            self.tabs["PRODUCTOS"] = {
                "widget": productos_screen,
                "closeable": True,
                "tab_button": self.tabs["PRODUCTOS"]["tab_button"]
            }
            self.switch_to_tab("PRODUCTOS")

    def open_categorias(self):
        print("Abriendo gestion de categorias...")
        if "CATEGORIAS" in self.tabs:
            self.switch_to_tab("CATEGORIAS")
        else:
            categorias_screen = CategoriasScreen()
            self.stack.addWidget(categorias_screen)
            self.create_tab_button("CATEGORIAS", True)
            self.tabs["CATEGORIAS"] = {
                "widget": categorias_screen,
                "closeable": True,
                "tab_button": self.tabs["CATEGORIAS"]["tab_button"]
            }
            self.switch_to_tab("CATEGORIAS")

    def open_proveedores(self):
        print("Abriendo gestión de proveedores...")
        if "PROVEEDORES" in self.tabs:
            self.switch_to_tab("PROVEEDORES")
        else:
            # import local para no tocar los imports globales
            from aplicacion.frontend.stock_ventanas.proveedores import ProveedoresScreen
            proveedores_screen = ProveedoresScreen()
            self.stack.addWidget(proveedores_screen)
            self.create_tab_button("PROVEEDORES", True)
            self.tabs["PROVEEDORES"] = {
                "widget": proveedores_screen,
                "closeable": True,
                "tab_button": self.tabs["PROVEEDORES"]["tab_button"]
            }
            self.switch_to_tab("PROVEEDORES")


    def open_vencimientos(self):
        print("Abriendo gestion de vencimientos...")
        if "VENCIMIENTOS" in self.tabs:
            self.switch_to_tab("VENCIMIENTOS")
        else:
            # import local para no tocar los imports globales
            from aplicacion.frontend.stock_ventanas.vencimientos import VencimientosScreen
            vencimientos_screen = VencimientosScreen()
            self.stack.addWidget(vencimientos_screen)
            self.create_tab_button("VENCIMIENTOS", True)
            self.tabs["VENCIMIENTOS"] = {
                "widget": vencimientos_screen,
                "closeable": True,
                "tab_button": self.tabs["VENCIMIENTOS"]["tab_button"]
            }
            self.switch_to_tab("VENCIMIENTOS")


    def set_icon(self, icon_path):
        try:
            icon_label = self.findChild(QLabel)
            if icon_label and icon_label.styleSheet().contains("border-radius: 30px"):
                pixmap = QPixmap(icon_path)
                scaled_pixmap = pixmap.scaled(54, 54,
                                              Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
        except Exception as e:
            print(f"Error al cargar el icono: {e}")