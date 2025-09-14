# aplicacion/frontend/administrador.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox,
    QMessageBox, QTextEdit, QGroupBox, QScrollArea,
    QSplitter, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QProgressBar, QFrame, QGridLayout, QInputDialog, QRadioButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QIcon, QPixmap
import json

# ===== Paleta tomada de perfil.py =====
# (importo las constantes para mantener la misma estética del módulo de perfil)
from aplicacion.frontend.perfil import (
    BG_DARK, FRAME_BG, CARD_BG, CARD_SUCCESS, CARD_ERROR,
    TEXT_WHITE, TEXT_DARK, TEXT_MUTED, TEXT_SUCCESS, TEXT_WARNING, TEXT_ERROR,
    TEXT_INFO, ACCENT_BLUE, ACCENT_GREEN, ACCENT_PURPLE
)

# ===== QSS propio del Administrador, usando la paleta de Perfil =====
ADMIN_QSS = f"""
/* Fondo y tipografía base */
QWidget {{
    background: {BG_DARK};
    font-family: 'Segoe UI', Arial, sans-serif;
    color: {TEXT_WHITE};
}}

/* Título principal */
QLabel.H1 {{
    color: {TEXT_WHITE};
    font-size: 28px;
    font-weight: 700;
    padding: 14px 16px;
    border-radius: 10px;
    background: {FRAME_BG};
    border: 1px solid #4F545C;
}}

QGroupBox {{
    color: {TEXT_WHITE};
    font-weight: 600;
    border: 2px solid #4F545C;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px 0 8px;
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid #4F545C;
    border-radius: 6px;
    background: {FRAME_BG};
    margin-top: 5px;
}}
QTabBar::tab {{
    background: #4F545C;
    color: {TEXT_WHITE};
    padding: 12px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}}
QTabBar::tab:selected {{
    background: {ACCENT_PURPLE};
}}
QTabBar::tab:hover {{
    background: #5F5F5F;
}}

/* Tablas */
QTableWidget {{
    background: {FRAME_BG};
    color: {TEXT_WHITE};
    gridline-color: #4F545C;
    alternate-background-color: #3B3F46;
    selection-background-color: {ACCENT_PURPLE};
    selection-color: {TEXT_WHITE};
    border: 1px solid #4F545C;
    border-radius: 6px;
}}
QHeaderView::section {{
    background: #4F545C;
    color: {TEXT_WHITE};
    padding: 6px 8px;
    border: 1px solid #4F545C;
    font-weight: 600;
}}

/* Árbol de permisos */
QTreeWidget {{
    background: {FRAME_BG};
    color: {TEXT_WHITE};
    border: 1px solid #4F545C;
    border-radius: 6px;
    selection-background-color: {ACCENT_PURPLE};
    selection-color: {TEXT_WHITE};
}}

/* Entradas de texto */
QLineEdit {{
    background: {CARD_BG};
    border: 1px solid #D0D0D0;
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_DARK};
    font-weight: 500;
}}
QLineEdit:focus {{
    border-color: {ACCENT_PURPLE};
    border-width: 2px;
}}

/* Área de logs */
QTextEdit.LogArea {{
    background: {FRAME_BG};
    border: 1px solid #4F545C;
    border-radius: 6px;
    color: {TEXT_WHITE};
    font-family: 'Consolas', monospace;
    font-size: 11px;
}}
"""

# ===== Imports del backend =====
from aplicacion.backend.usuarios.roles import controller as roles_controller
from aplicacion.backend.usuarios.usuarios import controller as usuarios_controller


class AdministradorTab(QWidget):
    def __init__(self):
        super().__init__()
        # Aplico estilos unificados con Perfil
        self.setStyleSheet(ADMIN_QSS)
        self.init_ui()
        self.cargar_datos_iniciales()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Título principal (usa clase H1 del QSS)
        title = QLabel("⚙️ PANEL DE ADMINISTRACIÓN")
        title.setObjectName("H1")
        title.setProperty("class", "H1")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Widget de pestañas
        self.tab_widget = QTabWidget()

        # Pestañas
        self.setup_gestion_roles_tab()
        self.setup_gestion_usuarios_tab()
        self.setup_asignacion_roles_tab()
        self.setup_permisos_tab()
        self.setup_utilidades_tab()

        layout.addWidget(self.tab_widget)

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales al abrir el panel"""
        self.actualizar_tabla_roles()
        self.actualizar_tabla_usuarios()
        self.actualizar_combo_usuarios_asignacion()
        self.actualizar_combo_roles_asignacion()

    # ===================== PESTAÑA GESTIÓN DE ROLES =====================
    def setup_gestion_roles_tab(self):
        roles_widget = QWidget()
        layout = QVBoxLayout(roles_widget)

        # Barra de herramientas
        toolbar = QHBoxLayout()

        # Botones (mismos textos/acciones; colores de la paleta Perfil)
        btn_crear_rol = QPushButton("➕ Crear Rol")
        btn_crear_rol.clicked.connect(self.crear_rol_dialog)
        btn_crear_rol.setStyleSheet(self.get_button_style("#27ae60"))  # success

        btn_editar_rol = QPushButton("✏️ Editar Rol")
        btn_editar_rol.clicked.connect(self.editar_rol_dialog)
        btn_editar_rol.setStyleSheet(self.get_button_style("#f39c12"))  # warning

        btn_eliminar_rol = QPushButton("🗑️ Eliminar Rol")
        btn_eliminar_rol.clicked.connect(self.eliminar_rol)
        btn_eliminar_rol.setStyleSheet(self.get_button_style("#e74c3c"))  # error

        btn_clonar_rol = QPushButton("📋 Clonar Rol")
        btn_clonar_rol.clicked.connect(self.clonar_rol_dialog)
        btn_clonar_rol.setStyleSheet(self.get_button_style("#8e44ad"))  # purple

        btn_comparar_roles = QPushButton("⚖️ Comparar Roles")
        btn_comparar_roles.clicked.connect(self.comparar_roles_dialog)
        btn_comparar_roles.setStyleSheet(self.get_button_style("#34495e"))  # azul/gris → azul

        btn_actualizar_roles = QPushButton("🔄 Actualizar")
        btn_actualizar_roles.clicked.connect(self.actualizar_tabla_roles)
        btn_actualizar_roles.setStyleSheet(self.get_button_style("#3498db"))  # blue

        toolbar.addWidget(btn_crear_rol)
        toolbar.addWidget(btn_editar_rol)
        toolbar.addWidget(btn_eliminar_rol)
        toolbar.addWidget(btn_clonar_rol)
        toolbar.addWidget(btn_comparar_roles)
        toolbar.addStretch()
        toolbar.addWidget(btn_actualizar_roles)

        layout.addLayout(toolbar)

        # Tabla de roles
        self.tabla_roles = QTableWidget()
        self.tabla_roles.setColumnCount(3)
        self.tabla_roles.setHorizontalHeaderLabels(["ID", "Nombre", "Permisos Activos"])
        self.tabla_roles.horizontalHeader().setStretchLastSection(True)
        self.tabla_roles.setAlternatingRowColors(True)
        self.tabla_roles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        # Señal con parámetro → lambda para que no rompa el slot sin args
        self.tabla_roles.itemDoubleClicked.connect(lambda *_: self.ver_detalle_rol())

        layout.addWidget(self.tabla_roles)

        self.tab_widget.addTab(roles_widget, "🛡️ Gestión de Roles")

    def actualizar_tabla_roles(self):
        """Actualizar la tabla de roles con datos del backend"""
        try:
            roles = roles_controller.listar_roles_controller()
            self.tabla_roles.setRowCount(len(roles))

            for row, rol in enumerate(roles):
                permisos_activos = sum(
                    sum(acciones.values()) for acciones in rol['permisos'].values()
                )
                self.tabla_roles.setItem(row, 0, QTableWidgetItem(str(rol['id'])))
                self.tabla_roles.setItem(row, 1, QTableWidgetItem(rol['nombre']))
                self.tabla_roles.setItem(row, 2, QTableWidgetItem(str(permisos_activos)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar roles: {str(e)}")

    def crear_rol_dialog(self):
        """Dialog para crear un nuevo rol"""
        dialog = CrearRolDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_tabla_roles()

    def editar_rol_dialog(self):
        """Dialog para editar un rol existente"""
        row = self.tabla_roles.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un rol para editar")
            return

        rol_id = int(self.tabla_roles.item(row, 0).text())
        dialog = EditarRolDialog(self, rol_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_tabla_roles()

    def eliminar_rol(self):
        """Eliminar rol seleccionado"""
        row = self.tabla_roles.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un rol para eliminar")
            return

        rol_id = int(self.tabla_roles.item(row, 0).text())
        rol_nombre = self.tabla_roles.item(row, 1).text()

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar el rol '{rol_nombre}'?\n\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                exito, mensaje = roles_controller.eliminar_rol_controller(rol_id)
                if exito:
                    QMessageBox.information(self, "Éxito", mensaje)
                    self.actualizar_tabla_roles()
                else:
                    QMessageBox.warning(self, "Error", mensaje)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar rol: {str(e)}")

    def clonar_rol_dialog(self):
        """Dialog para clonar un rol"""
        row = self.tabla_roles.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un rol para clonar")
            return

        rol_id = int(self.tabla_roles.item(row, 0).text())
        rol_nombre = self.tabla_roles.item(row, 1).text()

        # QLineEdit.getText no existe → QInputDialog.getText
        nuevo_nombre, ok = QInputDialog.getText(
            self,
            "Clonar Rol",
            f"Nombre para el clon de '{rol_nombre}':",
            text=f"{rol_nombre}_copia"
        )

        if ok and nuevo_nombre.strip():
            try:
                resultado = roles_controller.clonar_rol_controller(rol_id, nuevo_nombre.strip())
                if resultado:
                    QMessageBox.information(self, "Éxito", f"Rol clonado correctamente. Nuevo ID: {resultado}")
                    self.actualizar_tabla_roles()
                else:
                    QMessageBox.warning(self, "Error", "Error al clonar el rol")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al clonar rol: {str(e)}")

    def comparar_roles_dialog(self):
        """Dialog para comparar dos roles"""
        dialog = CompararRolesDialog(self)
        dialog.exec()

    def ver_detalle_rol(self):
        """Ver detalles completos de un rol"""
        row = self.tabla_roles.currentRow()
        if row == -1:
            return

        rol_id = int(self.tabla_roles.item(row, 0).text())
        dialog = DetalleRolDialog(self, rol_id)
        dialog.exec()

    # ===================== PESTAÑA GESTIÓN DE USUARIOS =====================
    def setup_gestion_usuarios_tab(self):
        usuarios_widget = QWidget()
        layout = QVBoxLayout(usuarios_widget)

        toolbar = QHBoxLayout()

        btn_crear_usuario = QPushButton("➕ Crear Usuario")
        btn_crear_usuario.clicked.connect(self.crear_usuario_dialog)
        btn_crear_usuario.setStyleSheet(self.get_button_style("#27ae60"))  # success

        btn_editar_usuario = QPushButton("✏️ Editar Usuario")
        btn_editar_usuario.clicked.connect(self.editar_usuario_dialog)
        btn_editar_usuario.setStyleSheet(self.get_button_style("#f39c12"))  # warning

        btn_ver_permisos_usuario = QPushButton("👁️ Ver Permisos")
        btn_ver_permisos_usuario.clicked.connect(self.ver_permisos_usuario)
        btn_ver_permisos_usuario.setStyleSheet(self.get_button_style("#8e44ad"))  # purple

        btn_actualizar_usuarios = QPushButton("🔄 Actualizar")
        btn_actualizar_usuarios.clicked.connect(self.actualizar_tabla_usuarios)
        btn_actualizar_usuarios.setStyleSheet(self.get_button_style("#3498db"))  # blue

        toolbar.addWidget(btn_crear_usuario)
        toolbar.addWidget(btn_editar_usuario)
        toolbar.addWidget(btn_ver_permisos_usuario)
        toolbar.addStretch()
        toolbar.addWidget(btn_actualizar_usuarios)

        layout.addLayout(toolbar)

        # Tabla
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(4)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Usuario", "Rol ID", "Rol Nombre"])
        self.tabla_usuarios.horizontalHeader().setStretchLastSection(True)
        self.tabla_usuarios.setAlternatingRowColors(True)
        self.tabla_usuarios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        layout.addWidget(self.tabla_usuarios)

        self.tab_widget.addTab(usuarios_widget, "👥 Gestión de Usuarios")

    def actualizar_tabla_usuarios(self):
        """Actualizar la tabla de usuarios"""
        try:
            usuarios = usuarios_controller.listar_usuarios_controller()
            roles = {rol['id']: rol['nombre'] for rol in roles_controller.listar_roles_controller()}

            self.tabla_usuarios.setRowCount(len(usuarios))

            for row, usuario in enumerate(usuarios):
                rol_nombre = roles.get(usuario.rol_id, "Sin Rol") if usuario.rol_id else "Sin Rol"
                self.tabla_usuarios.setItem(row, 0, QTableWidgetItem(str(usuario.id)))
                self.tabla_usuarios.setItem(row, 1, QTableWidgetItem(usuario.nombre_usuario))
                self.tabla_usuarios.setItem(row, 2, QTableWidgetItem(str(usuario.rol_id) if usuario.rol_id else ""))
                self.tabla_usuarios.setItem(row, 3, QTableWidgetItem(rol_nombre))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar usuarios: {str(e)}")

    def crear_usuario_dialog(self):
        """Dialog para crear usuario"""
        dialog = CrearUsuarioDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_tabla_usuarios()

    def editar_usuario_dialog(self):
        """Dialog para editar usuario"""
        row = self.tabla_usuarios.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un usuario para editar")
            return

        usuario_id = int(self.tabla_usuarios.item(row, 0).text())
        dialog = EditarUsuarioDialog(self, usuario_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.actualizar_tabla_usuarios()

    def ver_permisos_usuario(self):
        """Ver permisos de usuario seleccionado"""
        row = self.tabla_usuarios.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un usuario para ver sus permisos")
            return

        usuario_id = int(self.tabla_usuarios.item(row, 0).text())
        dialog = PermisosUsuarioDialog(self, usuario_id)
        dialog.exec()

    # ===================== PESTAÑA ASIGNACIÓN DE ROLES =====================
    def setup_asignacion_roles_tab(self):
        asignacion_widget = QWidget()
        layout = QVBoxLayout(asignacion_widget)

        group_asignacion = QGroupBox("Asignar Rol a Usuario")
        group_layout = QFormLayout(group_asignacion)

        self.combo_usuarios_asignacion = QComboBox()
        self.combo_roles_asignacion = QComboBox()

        group_layout.addRow("Usuario:", self.combo_usuarios_asignacion)
        group_layout.addRow("Rol:", self.combo_roles_asignacion)

        btn_asignar = QPushButton("✅ Asignar Rol")
        btn_asignar.clicked.connect(self.asignar_rol_usuario)
        btn_asignar.setStyleSheet(self.get_button_style("#27ae60"))  # success
        group_layout.addRow("", btn_asignar)

        layout.addWidget(group_asignacion)

        group_actuales = QGroupBox("Asignaciones Actuales")
        actuales_layout = QVBoxLayout(group_actuales)

        self.tabla_asignaciones = QTableWidget()
        self.tabla_asignaciones.setColumnCount(3)
        self.tabla_asignaciones.setHorizontalHeaderLabels(["Usuario", "Rol Actual", "Acciones"])
        self.tabla_asignaciones.horizontalHeader().setStretchLastSection(True)

        actuales_layout.addWidget(self.tabla_asignaciones)
        layout.addWidget(group_actuales)
        layout.addStretch()

        self.tab_widget.addTab(asignacion_widget, "🔄 Asignación de Roles")

    def actualizar_combo_usuarios_asignacion(self):
        """Actualizar combo de usuarios"""
        self.combo_usuarios_asignacion.clear()
        try:
            usuarios = usuarios_controller.listar_usuarios_controller()
            for usuario in usuarios:
                self.combo_usuarios_asignacion.addItem(
                    f"{usuario.nombre_usuario} (ID: {usuario.id})",
                    usuario.id
                )
        except Exception as e:
            print(f"Error cargando usuarios: {e}")

    def actualizar_combo_roles_asignacion(self):
        """Actualizar combo de roles"""
        self.combo_roles_asignacion.clear()
        try:
            roles = roles_controller.listar_roles_controller()
            for rol in roles:
                self.combo_roles_asignacion.addItem(
                    f"{rol['nombre']} (ID: {rol['id']})",
                    rol['id']
                )
        except Exception as e:
            print(f"Error cargando roles: {e}")

    def asignar_rol_usuario(self):
        """Asignar rol seleccionado a usuario seleccionado"""
        if self.combo_usuarios_asignacion.currentIndex() == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un usuario")
            return

        if self.combo_roles_asignacion.currentIndex() == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un rol")
            return

        usuario_id = self.combo_usuarios_asignacion.currentData()
        rol_id = self.combo_roles_asignacion.currentData()

        try:
            exito, mensaje = roles_controller.asignar_rol_usuario_controller(usuario_id, rol_id)
            if exito:
                QMessageBox.information(self, "Éxito", mensaje)
                self.actualizar_tabla_usuarios()
                self.actualizar_tabla_asignaciones()
            else:
                QMessageBox.warning(self, "Error", mensaje)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al asignar rol: {str(e)}")

    def actualizar_tabla_asignaciones(self):
        """Actualizar tabla de asignaciones"""
        try:
            usuarios = usuarios_controller.listar_usuarios_controller()
            roles = {rol['id']: rol['nombre'] for rol in roles_controller.listar_roles_controller()}

            self.tabla_asignaciones.setRowCount(len(usuarios))

            for row, usuario in enumerate(usuarios):
                rol_nombre = roles.get(usuario.rol_id, "Sin Rol") if usuario.rol_id else "Sin Rol"

                self.tabla_asignaciones.setItem(row, 0, QTableWidgetItem(usuario.nombre_usuario))
                self.tabla_asignaciones.setItem(row, 1, QTableWidgetItem(rol_nombre))

                # Botón para cambiar rol
                btn_cambiar = QPushButton("Cambiar")
                btn_cambiar.setProperty("usuario_id", usuario.id)
                btn_cambiar.clicked.connect(self.cambiar_rol_rapido)
                btn_cambiar.setStyleSheet(self.get_button_style("#3498db"))  # blue
                self.tabla_asignaciones.setCellWidget(row, 2, btn_cambiar)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar asignaciones: {str(e)}")

    def cambiar_rol_rapido(self):
        """Cambio rápido de rol desde la tabla"""
        sender = self.sender()
        usuario_id = sender.property("usuario_id")

        roles = roles_controller.listar_roles_controller()
        rol_names = [f"{rol['nombre']} (ID: {rol['id']})" for rol in roles]

        item, ok = QInputDialog.getItem(
            self, "Cambiar Rol", "Seleccione nuevo rol:", rol_names, 0, False
        )

        if ok and item:
            rol_id = int(item.split("ID: ")[1].rstrip(")"))
            try:
                exito, mensaje = roles_controller.asignar_rol_usuario_controller(usuario_id, rol_id)
                if exito:
                    QMessageBox.information(self, "Éxito", mensaje)
                    self.actualizar_tabla_usuarios()
                    self.actualizar_tabla_asignaciones()
                else:
                    QMessageBox.warning(self, "Error", mensaje)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cambiar rol: {str(e)}")

    # ===================== PESTAÑA VISUALIZACIÓN DE PERMISOS =====================
    def setup_permisos_tab(self):
        permisos_widget = QWidget()
        layout = QVBoxLayout(permisos_widget)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Ver permisos de:"))

        self.combo_tipo_permisos = QComboBox()
        self.combo_tipo_permisos.addItems(["Usuarios", "Roles", "Plantillas"])
        self.combo_tipo_permisos.currentTextChanged.connect(self.cambiar_tipo_permisos)
        controls_layout.addWidget(self.combo_tipo_permisos)

        self.combo_seleccion_permisos = QComboBox()
        controls_layout.addWidget(self.combo_seleccion_permisos)

        btn_ver_permisos = QPushButton("👁️ Ver Permisos")
        btn_ver_permisos.clicked.connect(self.mostrar_permisos_detalle)
        btn_ver_permisos.setStyleSheet(self.get_button_style("#3498db"))  # blue
        controls_layout.addWidget(btn_ver_permisos)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Área de visualización
        self.tree_permisos = QTreeWidget()
        self.tree_permisos.setHeaderLabels(["Módulo/Acción", "Estado"])
        layout.addWidget(self.tree_permisos)

        self.tab_widget.addTab(permisos_widget, "👁️ Visualización de Permisos")
        self.cambiar_tipo_permisos()

    def cambiar_tipo_permisos(self):
        """Cambiar el tipo de permisos a mostrar"""
        self.combo_seleccion_permisos.clear()

        tipo = self.combo_tipo_permisos.currentText()

        if tipo == "Usuarios":
            usuarios = usuarios_controller.listar_usuarios_controller()
            for usuario in usuarios:
                self.combo_seleccion_permisos.addItem(
                    f"{usuario.nombre_usuario} (ID: {usuario.id})",
                    ("usuario", usuario.id)
                )
        elif tipo == "Roles":
            roles = roles_controller.listar_roles_controller()
            for rol in roles:
                self.combo_seleccion_permisos.addItem(
                    f"{rol['nombre']} (ID: {rol['id']})",
                    ("rol", rol['id'])
                )
        elif tipo == "Plantillas":
            plantillas = [
                ("Administrador", "admin"),
                ("Empleado Básico", "empleado"),
                ("Supervisor", "supervisor"),
                ("Estructura Base", "base")
            ]
            for nombre, codigo in plantillas:
                self.combo_seleccion_permisos.addItem(nombre, ("plantilla", codigo))

    def mostrar_permisos_detalle(self):
        """Mostrar permisos detallados en el tree widget"""
        if self.combo_seleccion_permisos.currentIndex() == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un elemento")
            return

        tipo, identificador = self.combo_seleccion_permisos.currentData()

        try:
            permisos = None

            if tipo == "usuario":
                permisos = roles_controller.obtener_permisos_usuario_controller(identificador)
            elif tipo == "rol":
                rol = roles_controller.obtener_rol_controller(identificador)
                permisos = rol['permisos'] if rol else None
            elif tipo == "plantilla":
                if identificador == "admin":
                    permisos = roles_controller.obtener_permisos_admin_controller()
                elif identificador == "empleado":
                    permisos = roles_controller.obtener_permisos_empleado_basico_controller()
                elif identificador == "supervisor":
                    permisos = roles_controller.obtener_permisos_supervisor_controller()
                elif identificador == "base":
                    permisos = roles_controller.obtener_estructura_permisos_controller()

            if permisos:
                self.poblar_tree_permisos(permisos)
            else:
                QMessageBox.warning(self, "Error", "No se pudieron cargar los permisos")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar permisos: {str(e)}")

    def poblar_tree_permisos(self, permisos):
        """Poblar el tree widget con los permisos"""
        self.tree_permisos.clear()

        for modulo, acciones in permisos.items():
            modulo_item = QTreeWidgetItem(self.tree_permisos)
            modulo_item.setText(0, f"📁 {modulo.upper()}")
            modulo_item.setText(1, "")

            for accion, permitido in acciones.items():
                accion_item = QTreeWidgetItem(modulo_item)
                estado_icon = "✅" if permitido else "❌"
                estado_text = "Permitido" if permitido else "Denegado"

                accion_item.setText(0, f"   {accion}")
                accion_item.setText(1, f"{estado_icon} {estado_text}")

                # Fondo según estado (usa paleta Perfil)
                if permitido:
                    accion_item.setBackground(0, self.get_color(CARD_SUCCESS))
                    accion_item.setBackground(1, self.get_color(CARD_SUCCESS))
                else:
                    accion_item.setBackground(0, self.get_color(CARD_ERROR))
                    accion_item.setBackground(1, self.get_color(CARD_ERROR))

        self.tree_permisos.expandAll()

    # ===================== PESTAÑA UTILIDADES =====================
    def setup_utilidades_tab(self):
        utilidades_widget = QWidget()
        layout = QVBoxLayout(utilidades_widget)

        group_config = QGroupBox("Configuración Inicial del Sistema")
        config_layout = QGridLayout(group_config)

        btn_roles_defecto = QPushButton("🏗️ Crear Roles por Defecto")
        btn_roles_defecto.clicked.connect(self.crear_roles_defecto)
        btn_roles_defecto.setStyleSheet(self.get_button_style("#27ae60"))  # success

        btn_verificar_integridad = QPushButton("🔍 Verificar Integridad")
        btn_verificar_integridad.clicked.connect(self.verificar_integridad)
        btn_verificar_integridad.setStyleSheet(self.get_button_style("#3498db"))  # blue

        btn_estadisticas = QPushButton("📊 Ver Estadísticas")
        btn_estadisticas.clicked.connect(self.mostrar_estadisticas)
        btn_estadisticas.setStyleSheet(self.get_button_style("#8e44ad"))  # purple

        btn_exportar_config = QPushButton("💾 Exportar Configuración")
        btn_exportar_config.clicked.connect(self.exportar_configuracion)
        btn_exportar_config.setStyleSheet(self.get_button_style("#f39c12"))  # warning

        config_layout.addWidget(btn_roles_defecto, 0, 0)
        config_layout.addWidget(btn_verificar_integridad, 0, 1)
        config_layout.addWidget(btn_estadisticas, 1, 0)
        config_layout.addWidget(btn_exportar_config, 1, 1)

        layout.addWidget(group_config)

        group_logs = QGroupBox("Resultados y Logs")
        logs_layout = QVBoxLayout(group_logs)

        self.text_logs = QTextEdit()
        self.text_logs.setReadOnly(True)
        self.text_logs.setMaximumHeight(200)
        self.text_logs.setObjectName("LogArea")
        self.text_logs.setProperty("class", "LogArea")
        logs_layout.addWidget(self.text_logs)

        layout.addWidget(group_logs)
        layout.addStretch()

        self.tab_widget.addTab(utilidades_widget, "🛠️ Utilidades")

    def crear_roles_defecto(self):
        """Crear roles por defecto"""
        try:
            resultado = roles_controller.crear_roles_por_defecto_controller()
            self.text_logs.append(f"✅ Roles por defecto: {resultado}")
            self.actualizar_tabla_roles()
        except Exception as e:
            self.text_logs.append(f"❌ Error creando roles: {str(e)}")

    def verificar_integridad(self):
        """Verificar integridad del sistema"""
        self.text_logs.append("🔍 Verificando integridad del sistema...")

        try:
            roles = roles_controller.listar_roles_controller()
            estructura_base = roles_controller.obtener_estructura_permisos_controller()

            problemas = []

            for rol in roles:
                for modulo in estructura_base:
                    if modulo not in rol['permisos']:
                        problemas.append(f"Rol '{rol['nombre']}' falta módulo '{modulo}'")
                    else:
                        for accion in estructura_base[modulo]:
                            if accion not in rol['permisos'][modulo]:
                                problemas.append(f"Rol '{rol['nombre']}' falta acción '{modulo}.{accion}'")

            if problemas:
                self.text_logs.append("⚠️ Problemas encontrados:")
                for problema in problemas:
                    self.text_logs.append(f"  • {problema}")
            else:
                self.text_logs.append("✅ Sistema íntegro. No se encontraron problemas.")

        except Exception as e:
            self.text_logs.append(f"❌ Error verificando integridad: {str(e)}")

    def mostrar_estadisticas(self):
        """Mostrar estadísticas del sistema"""
        try:
            estadisticas = roles_controller.obtener_estadisticas_roles_controller()

            if 'error' in estadisticas:
                self.text_logs.append(f"❌ Error: {estadisticas['error']}")
                return

            self.text_logs.append("📊 ESTADÍSTICAS DEL SISTEMA")
            self.text_logs.append(f"👥 Total de usuarios: {estadisticas['total_usuarios']}")
            self.text_logs.append(f"🛡️ Total de roles: {estadisticas['total_roles']}")
            self.text_logs.append(f"⚠️ Usuarios sin rol: {estadisticas['usuarios_sin_rol']}")
            self.text_logs.append("")
            self.text_logs.append("📋 DETALLE POR ROL:")

            for detalle in estadisticas['roles_detalle']:
                self.text_logs.append(
                    f"  🔹 {detalle['rol']}: {detalle['usuarios_asignados']} usuarios ({detalle['porcentaje_uso']:.1f}%)"
                )

            self.text_logs.append("")

        except Exception as e:
            self.text_logs.append(f"❌ Error obteniendo estadísticas: {str(e)}")

    def exportar_configuracion(self):
        """Exportar configuración completa"""
        try:
            from PyQt6.QtWidgets import QFileDialog

            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Configuración",
                "configuracion_roles.json",
                "JSON files (*.json)"
            )

            if filename:
                roles = roles_controller.listar_roles_controller()
                usuarios = usuarios_controller.listar_usuarios_controller()

                config = {
                    "roles": roles,
                    "usuarios": [
                        {
                            "id": u.id,
                            "nombre_usuario": u.nombre_usuario,
                            "rol_id": u.rol_id
                        } for u in usuarios
                    ],
                    "estructura_permisos": roles_controller.obtener_estructura_permisos_controller(),
                    "export_date": str(QDateTime.currentDateTime().toString())
                }

                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                self.text_logs.append(f"✅ Configuración exportada a: {filename}")

        except Exception as e:
            self.text_logs.append(f"❌ Error exportando: {str(e)}")

    # ===================== MÉTODOS DE ESTILO =====================
    def get_button_style(self, base_color_hex: str) -> str:
        """
        Mantengo la API original pero mapeo los colores a la paleta de Perfil.
        """
        palette_map = {
            "#27ae60": TEXT_SUCCESS,   # success
            "#f39c12": TEXT_WARNING,   # warning
            "#e74c3c": TEXT_ERROR,     # error
            "#8e44ad": ACCENT_PURPLE,  # purple
            "#34495e": ACCENT_BLUE,    # usamos azul para destacar
            "#3498db": ACCENT_BLUE,    # blue
            "#9b59b6": ACCENT_PURPLE   # purple
        }
        color = palette_map.get(base_color_hex, ACCENT_BLUE)

        darker_map = {
            TEXT_SUCCESS: "#45A049",
            TEXT_WARNING: "#E68900",
            TEXT_ERROR:   "#D32F2F",
            ACCENT_PURPLE: "#7B1FA2",
            ACCENT_BLUE:  "#4752C4"
        }
        darker = darker_map.get(color, "#3C45A3")
        pressed = "#3C45A3" if color == ACCENT_BLUE else darker

        return f"""
            QPushButton {{
                background-color: {color};
                color: {TEXT_WHITE};
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {darker};
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
        """

    def get_color(self, hex_color):
        """Convertir hex a QColor"""
        from PyQt6.QtGui import QColor
        return QColor(hex_color)


# ===================== DIALOGS AUXILIARES =====================
class CrearRolDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Nuevo Rol")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.edit_nombre = QLineEdit()
        form_layout.addRow("Nombre del rol:", self.edit_nombre)
        layout.addLayout(form_layout)

        group_tipo = QGroupBox("Permisos Base")
        tipo_layout = QVBoxLayout(group_tipo)

        self.radio_vacio = QRadioButton("Rol vacío (sin permisos)")
        self.radio_empleado = QRadioButton("Basado en Empleado Básico")
        self.radio_supervisor = QRadioButton("Basado en Supervisor")
        self.radio_admin = QRadioButton("Basado en Administrador")
        self.radio_personalizado = QRadioButton("Personalizado")

        self.radio_vacio.setChecked(True)

        tipo_layout.addWidget(self.radio_vacio)
        tipo_layout.addWidget(self.radio_empleado)
        tipo_layout.addWidget(self.radio_supervisor)
        tipo_layout.addWidget(self.radio_admin)
        tipo_layout.addWidget(self.radio_personalizado)

        layout.addWidget(group_tipo)

        buttons_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_crear = QPushButton("Crear Rol")

        btn_cancelar.clicked.connect(self.reject)
        btn_crear.clicked.connect(self.crear_rol)
        btn_cancelar.setStyleSheet("padding: 8px 16px;")
        btn_crear.setStyleSheet(AdministradorTab.get_button_style(self, "#27ae60"))

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_crear)

        layout.addLayout(buttons_layout)

    def crear_rol(self):
        nombre = self.edit_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre no puede estar vacío")
            return

        try:
            if self.radio_vacio.isChecked():
                permisos = roles_controller.obtener_estructura_permisos_controller()
            elif self.radio_empleado.isChecked():
                permisos = roles_controller.obtener_permisos_empleado_basico_controller()
            elif self.radio_supervisor.isChecked():
                permisos = roles_controller.obtener_permisos_supervisor_controller()
            elif self.radio_admin.isChecked():
                permisos = roles_controller.obtener_permisos_admin_controller()
            elif self.radio_personalizado.isChecked():
                dialog = PersonalizarPermisosDialog(self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    permisos = dialog.get_permisos()
                else:
                    return

            resultado = roles_controller.crear_rol_controller(nombre, permisos)
            if resultado:
                QMessageBox.information(self, "Éxito", f"Rol '{nombre}' creado correctamente. ID: {resultado}")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error al crear el rol")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class EditarRolDialog(QDialog):
    def __init__(self, parent=None, rol_id=None):
        super().__init__(parent)
        self.rol_id = rol_id
        self.setWindowTitle("Editar Rol")
        self.setModal(True)
        self.resize(700, 600)
        self.init_ui()
        self.cargar_rol()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(self.lbl_info)

        scroll = QScrollArea()
        permisos_widget = QWidget()
        self.permisos_layout = QVBoxLayout(permisos_widget)
        scroll.setWidget(permisos_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

        buttons_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar = QPushButton("Guardar Cambios")

        btn_cancelar.clicked.connect(self.reject)
        btn_guardar.clicked.connect(self.guardar_cambios)
        btn_guardar.setStyleSheet(AdministradorTab.get_button_style(self, "#27ae60"))
        btn_cancelar.setStyleSheet("padding: 8px 16px;")

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_guardar)

        layout.addLayout(buttons_layout)

        self.checkboxes = {}

    def cargar_rol(self):
        try:
            rol = roles_controller.obtener_rol_controller(self.rol_id)
            if not rol:
                QMessageBox.critical(self, "Error", "Rol no encontrado")
                self.reject()
                return

            self.lbl_info.setText(f"Editando rol: {rol['nombre']} (ID: {rol['id']})")
            permisos = rol['permisos']

            for modulo, acciones in permisos.items():
                group = QGroupBox(f"📁 {modulo.upper()}")
                group_layout = QVBoxLayout(group)

                self.checkboxes[modulo] = {}
                for accion, permitido in acciones.items():
                    checkbox = QCheckBox(accion)
                    checkbox.setChecked(permitido)
                    self.checkboxes[modulo][accion] = checkbox
                    group_layout.addWidget(checkbox)

                self.permisos_layout.addWidget(group)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando rol: {str(e)}")
            self.reject()

    def guardar_cambios(self):
        try:
            nuevos_permisos = {}
            for modulo, checkboxes_modulo in self.checkboxes.items():
                nuevos_permisos[modulo] = {}
                for accion, checkbox in checkboxes_modulo.items():
                    nuevos_permisos[modulo][accion] = checkbox.isChecked()

            if roles_controller.editar_rol_controller(self.rol_id, nuevos_permisos):
                QMessageBox.information(self, "Éxito", "Rol actualizado correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error al actualizar el rol")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class PersonalizarPermisosDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Personalizar Permisos")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Configure los permisos específicos para el rol:"))

        scroll = QScrollArea()
        permisos_widget = QWidget()
        self.permisos_layout = QVBoxLayout(permisos_widget)
        scroll.setWidget(permisos_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

        self.crear_checkboxes_permisos()

        buttons_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_aceptar = QPushButton("Aceptar")

        btn_cancelar.clicked.connect(self.reject)
        btn_aceptar.clicked.connect(self.accept)
        btn_aceptar.setStyleSheet(AdministradorTab.get_button_style(self, "#8e44ad"))
        btn_cancelar.setStyleSheet("padding: 8px 16px;")

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_aceptar)

        layout.addLayout(buttons_layout)

    def crear_checkboxes_permisos(self):
        estructura = roles_controller.obtener_estructura_permisos_controller()
        self.checkboxes = {}

        for modulo, acciones in estructura.items():
            group = QGroupBox(f"📁 {modulo.upper()}")
            group_layout = QVBoxLayout(group)

            self.checkboxes[modulo] = {}
            for accion in acciones:
                checkbox = QCheckBox(accion)
                checkbox.setChecked(False)
                self.checkboxes[modulo][accion] = checkbox
                group_layout.addWidget(checkbox)

            self.permisos_layout.addWidget(group)

    def get_permisos(self):
        permisos = {}
        for modulo, checkboxes_modulo in self.checkboxes.items():
            permisos[modulo] = {}
            for accion, checkbox in checkboxes_modulo.items():
                permisos[modulo][accion] = checkbox.isChecked()
        return permisos


class CompararRolesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparar Roles")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        seleccion_layout = QHBoxLayout()
        seleccion_layout.addWidget(QLabel("Rol 1:"))
        self.combo_rol1 = QComboBox()
        seleccion_layout.addWidget(self.combo_rol1)

        seleccion_layout.addWidget(QLabel("Rol 2:"))
        self.combo_rol2 = QComboBox()
        seleccion_layout.addWidget(self.combo_rol2)

        btn_comparar = QPushButton("⚖️ Comparar")
        btn_comparar.clicked.connect(self.comparar_roles)
        btn_comparar.setStyleSheet(AdministradorTab.get_button_style(self, "#3498db"))
        seleccion_layout.addWidget(btn_comparar)

        layout.addLayout(seleccion_layout)

        self.cargar_roles()

        self.text_resultado = QTextEdit()
        self.text_resultado.setReadOnly(True)
        layout.addWidget(self.text_resultado)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet("padding: 8px 16px;")
        layout.addWidget(btn_cerrar)

    def cargar_roles(self):
        try:
            roles = roles_controller.listar_roles_controller()
            for rol in roles:
                texto = f"{rol['nombre']} (ID: {rol['id']})"
                self.combo_rol1.addItem(texto, rol['id'])
                self.combo_rol2.addItem(texto, rol['id'])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando roles: {str(e)}")

    def comparar_roles(self):
        if self.combo_rol1.currentIndex() == -1 or self.combo_rol2.currentIndex() == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione ambos roles")
            return

        rol1_id = self.combo_rol1.currentData()
        rol2_id = self.combo_rol2.currentData()

        if rol1_id == rol2_id:
            QMessageBox.warning(self, "Advertencia", "Seleccione roles diferentes")
            return

        try:
            comparacion = roles_controller.comparar_roles_controller(rol1_id, rol2_id)

            if comparacion:
                self.mostrar_resultado_comparacion(comparacion)
            else:
                QMessageBox.warning(self, "Error", "Error al comparar roles")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def mostrar_resultado_comparacion(self, comparacion):
        resultado = f"""
📊 COMPARACIÓN DE ROLES
{'='*50}

🛡️ ROL 1: {comparacion['rol1']['nombre']} (ID: {comparacion['rol1']['id']})
🛡️ ROL 2: {comparacion['rol2']['nombre']} (ID: {comparacion['rol2']['id']})

"""
        if not any(comparacion['diferencias'].values()):
            resultado += "✅ Los roles tienen permisos idénticos."
        else:
            resultado += "🔍 DIFERENCIAS ENCONTRADAS:\n\n"
            for modulo, diferencias in comparacion['diferencias'].items():
                if diferencias:
                    resultado += f"📁 {modulo.upper()}:\n"
                    for accion, valores in diferencias.items():
                        rol1_estado = "✅" if valores['rol1'] else "❌"
                        rol2_estado = "✅" if valores['rol2'] else "❌"
                        resultado += f"   • {accion}: {rol1_estado} vs {rol2_estado}\n"
                    resultado += "\n"

        self.text_resultado.setText(resultado)


class DetalleRolDialog(QDialog):
    def __init__(self, parent=None, rol_id=None):
        super().__init__(parent)
        self.rol_id = rol_id
        self.setWindowTitle("Detalle del Rol")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        self.cargar_detalle()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 16px; margin: 10px;")
        layout.addWidget(self.lbl_info)

        self.tree_permisos = QTreeWidget()
        self.tree_permisos.setHeaderLabels(["Módulo/Acción", "Estado"])
        layout.addWidget(self.tree_permisos)

        group_json = QGroupBox("JSON Raw (para desarrolladores)")
        json_layout = QVBoxLayout(group_json)
        self.text_json = QTextEdit()
        self.text_json.setMaximumHeight(150)
        self.text_json.setReadOnly(True)
        self.text_json.setObjectName("LogArea")
        self.text_json.setProperty("class", "LogArea")
        json_layout.addWidget(self.text_json)
        layout.addWidget(group_json)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet("padding: 8px 16px;")
        layout.addWidget(btn_cerrar)

    def cargar_detalle(self):
        try:
            rol = roles_controller.obtener_rol_controller(self.rol_id)
            if not rol:
                QMessageBox.critical(self, "Error", "Rol no encontrado")
                self.reject()
                return

            permisos_activos = sum(sum(acciones.values()) for acciones in rol['permisos'].values())
            total_permisos = sum(len(acciones) for acciones in rol['permisos'].values())

            self.lbl_info.setText(
                f"🛡️ {rol['nombre']} (ID: {rol['id']})\n"
                f"📊 Permisos activos: {permisos_activos}/{total_permisos}"
            )

            self.poblar_tree_permisos(rol['permisos'])
            self.text_json.setText(rol['permisos_raw'])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            self.reject()

    def poblar_tree_permisos(self, permisos):
        self.tree_permisos.clear()

        for modulo, acciones in permisos.items():
            modulo_item = QTreeWidgetItem(self.tree_permisos)
            modulo_item.setText(0, f"📁 {modulo.upper()}")
            modulo_item.setText(1, "")

            for accion, permitido in acciones.items():
                accion_item = QTreeWidgetItem(modulo_item)
                estado_icon = "✅" if permitido else "❌"
                estado_text = "Permitido" if permitido else "Denegado"
                accion_item.setText(0, f"   {accion}")
                accion_item.setText(1, f"{estado_icon} {estado_text}")

        self.tree_permisos.expandAll()


class CrearUsuarioDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Crear Usuario")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.edit_usuario = QLineEdit()
        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_email = QLineEdit()

        form_layout.addRow("Nombre de usuario:", self.edit_usuario)
        form_layout.addRow("Contraseña:", self.edit_password)
        form_layout.addRow("Email:", self.edit_email)

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_crear = QPushButton("Crear Usuario")

        btn_cancelar.clicked.connect(self.reject)
        btn_crear.clicked.connect(self.crear_usuario)
        btn_crear.setStyleSheet(AdministradorTab.get_button_style(self, "#27ae60"))
        btn_cancelar.setStyleSheet("padding: 8px 16px;")

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_crear)

        layout.addLayout(buttons_layout)

    def crear_usuario(self):
        usuario = self.edit_usuario.text().strip()
        password = self.edit_password.text().strip()
        email = self.edit_email.text().strip()

        if not all([usuario, password, email]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return

        try:
            resultado = usuarios_controller.registrar_usuario_controller(usuario, password, email)
            if resultado:
                QMessageBox.information(self, "Éxito", "Usuario creado correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error al crear usuario")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class EditarUsuarioDialog(QDialog):
    def __init__(self, parent=None, usuario_id=None):
        super().__init__(parent)
        self.usuario_id = usuario_id
        self.setWindowTitle("Editar Usuario")
        self.setModal(True)
        self.resize(400, 250)
        self.init_ui()
        self.cargar_usuario()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("font-weight: bold; margin: 10px;")
        layout.addWidget(self.lbl_info)

        form_layout = QFormLayout()

        self.edit_password = QLineEdit()
        self.edit_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_password.setPlaceholderText("Dejar vacío para no cambiar")

        form_layout.addRow("Nueva contraseña:", self.edit_password)

        layout.addLayout(form_layout)

        buttons_layout = QHBoxLayout()
        btn_cancelar = QPushButton("Cancelar")
        btn_guardar = QPushButton("Guardar Cambios")

        btn_cancelar.clicked.connect(self.reject)
        btn_guardar.clicked.connect(self.guardar_cambios)
        btn_guardar.setStyleSheet(AdministradorTab.get_button_style(self, "#27ae60"))
        btn_cancelar.setStyleSheet("padding: 8px 16px;")

        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancelar)
        buttons_layout.addWidget(btn_guardar)

        layout.addLayout(buttons_layout)

    def cargar_usuario(self):
        try:
            usuario = usuarios_controller.obtener_usuario_controller(self.usuario_id)
            if usuario:
                self.lbl_info.setText(f"Editando usuario: {usuario.nombre_usuario} (ID: {usuario.id})")
            else:
                QMessageBox.critical(self, "Error", "Usuario no encontrado")
                self.reject()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            self.reject()

    def guardar_cambios(self):
        password = self.edit_password.text().strip()

        if not password:
            QMessageBox.warning(self, "Advertencia", "Ingrese una nueva contraseña")
            return

        try:
            datos = {"password": password}
            resultado = usuarios_controller.editar_usuario_controller(self.usuario_id, datos)

            if resultado:
                QMessageBox.information(self, "Éxito", "Usuario actualizado correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Error al actualizar usuario")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")


class PermisosUsuarioDialog(QDialog):
    def __init__(self, parent=None, usuario_id=None):
        super().__init__(parent)
        self.usuario_id = usuario_id
        self.setWindowTitle("Permisos del Usuario")
        self.setModal(True)
        self.resize(600, 500)
        self.init_ui()
        self.cargar_permisos()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(self.lbl_info)

        self.tree_permisos = QTreeWidget()
        self.tree_permisos.setHeaderLabels(["Módulo/Acción", "Estado"])
        layout.addWidget(self.tree_permisos)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet("padding: 8px 16px;")
        layout.addWidget(btn_cerrar)

    def cargar_permisos(self):
        try:
            usuario = usuarios_controller.obtener_usuario_controller(self.usuario_id)
            if not usuario:
                QMessageBox.critical(self, "Error", "Usuario no encontrado")
                self.reject()
                return

            permisos = roles_controller.obtener_permisos_usuario_controller(self.usuario_id)

            rol_info = "Administrador" if usuario.rol_id == 1 else f"Rol ID: {usuario.rol_id}"
            permisos_activos = sum(sum(acciones.values()) for acciones in permisos.values()) if permisos else 0

            self.lbl_info.setText(
                f"👤 Usuario: {usuario.nombre_usuario}\n"
                f"🛡️ {rol_info}\n"
                f"📊 Permisos activos: {permisos_activos}"
            )

            if permisos:
                self.poblar_tree_permisos(permisos)
            else:
                self.tree_permisos.clear()
                item = QTreeWidgetItem(self.tree_permisos)
                item.setText(0, "⚠️ Usuario sin permisos")
                item.setText(1, "")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")
            self.reject()

    def poblar_tree_permisos(self, permisos):
        self.tree_permisos.clear()

        for modulo, acciones in permisos.items():
            modulo_item = QTreeWidgetItem(self.tree_permisos)
            modulo_item.setText(0, f"📁 {modulo.upper()}")
            modulo_item.setText(1, "")

            for accion, permitido in acciones.items():
                accion_item = QTreeWidgetItem(modulo_item)
                estado_icon = "✅" if permitido else "❌"
                estado_text = "Permitido" if permitido else "Denegado"

                accion_item.setText(0, f"   {accion}")
                accion_item.setText(1, f"{estado_icon} {estado_text}")

                if permitido:
                    accion_item.setBackground(0, self.get_color(CARD_SUCCESS))
                    accion_item.setBackground(1, self.get_color(CARD_SUCCESS))
                else:
                    accion_item.setBackground(0, self.get_color(CARD_ERROR))
                    accion_item.setBackground(1, self.get_color(CARD_ERROR))

        self.tree_permisos.expandAll()
