# roles.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import importlib
from typing import Any, Dict, List, Optional

# Qt (PyQt6)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
)


# --------------------------------------------------------------------------------------
# Helpers de carga de controller (soporta varias rutas comunes del proyecto)
# --------------------------------------------------------------------------------------

def _load_controller_module():
    candidates = [
        "aplicacion.controller",
        "aplicacion.controllers",
        "controller",
    ]
    for mod in candidates:
        try:
            return importlib.import_module(mod)
        except Exception:
            continue
    return None


controller = _load_controller_module()


# --------------------------------------------------------------------------------------
# Normalizadores: soportan que el backend devuelva ORM o dict
# --------------------------------------------------------------------------------------

def _user_to_dict(u: Any) -> Dict[str, Any]:
    """
    Normaliza un usuario (dict u objeto ORM) a:
        {"id": int, "nombre_usuario": str, "rol_id": Optional[int]}
    """
    if isinstance(u, dict):
        return {
            "id": u.get("id"),
            "nombre_usuario": u.get("nombre_usuario") or u.get("nombre") or "",
            "rol_id": u.get("rol_id"),
        }

    # Objeto ORM
    uid = getattr(u, "id", None)
    uname = getattr(u, "nombre_usuario", getattr(u, "nombre", ""))

    rid = getattr(u, "rol_id", None)
    # Intento leer relación u.rol si existe
    try:
        if rid is None and getattr(u, "rol", None) is not None:
            rid = getattr(u.rol, "id", None)
    except Exception:
        pass

    return {"id": uid, "nombre_usuario": uname or "", "rol_id": rid}


def _role_to_dict(r: Any) -> Dict[str, Any]:
    """
    Normaliza un rol (dict u objeto ORM) a:
        {"id": int, "nombre": str, "permisos": Optional[list|str]}
    """
    if isinstance(r, dict):
        return {
            "id": r.get("id"),
            "nombre": r.get("nombre", ""),
            "permisos": r.get("permisos"),
        }

    return {
        "id": getattr(r, "id", None),
        "nombre": getattr(r, "nombre", str(r)),
        "permisos": getattr(r, "permisos", None),
    }


# --------------------------------------------------------------------------------------
# Fachada: llamadas seguras a funciones del controller
# --------------------------------------------------------------------------------------

class RolesService:
    def _require(self):
        if controller is None:
            raise RuntimeError(
                "No se pudo importar el módulo 'controller'. Revisa el import en roles.py."
            )

    # ------- ROLES -------
    def listar_roles(self) -> List[Dict[str, Any]]:
        self._require()
        fn = getattr(controller, "listar_roles_controller", None)
        if fn is None:
            # fallback a listar_todos_roles_controller
            fn = getattr(controller, "listar_todos_roles_controller", None)
        if fn is None:
            raise RuntimeError("No existe listar_roles_controller en controller.")
        raw = fn() or []
        return [_role_to_dict(x) for x in raw]

    def crear_rol(self, nombre: str, permisos: Optional[List[str]] = None) -> Any:
        self._require()
        fn = getattr(controller, "crear_rol_controller", None)
        if fn is None:
            raise RuntimeError("No existe crear_rol_controller en controller.")
        return fn(nombre, permisos)

    def actualizar_rol(self, rol_id: int, nombre: str, permisos: Optional[List[str]]):
        self._require()
        fn = getattr(controller, "actualizar_rol_controller", None)
        if fn is None:
            # nombre alternativo
            fn = getattr(controller, "editar_rol_controller", None)
        if fn is None:
            raise RuntimeError("No existe actualizar_rol_controller en controller.")
        return fn(rol_id, nombre, permisos)

    def eliminar_rol(self, rol_id: int):
        self._require()
        fn = getattr(controller, "eliminar_rol_controller", None)
        if fn is None:
            raise RuntimeError("No existe eliminar_rol_controller en controller.")
        return fn(rol_id)

    # ------- USUARIOS -------
    def listar_usuarios(self) -> List[Dict[str, Any]]:
        self._require()
        fn = getattr(controller, "listar_usuarios_controller", None)
        if fn is None:
            raise RuntimeError("No existe listar_usuarios_controller en controller.")
        raw = fn() or []
        return [_user_to_dict(x) for x in raw]

    def asignar_rol_usuario(self, usuario_id: int, rol_id: Optional[int]):
        self._require()
        fn = getattr(controller, "asignar_rol_usuario_controller", None)
        if fn is None:
            raise RuntimeError(
                "No existe asignar_rol_usuario_controller en controller."
            )
        return fn(usuario_id, rol_id)


svc = RolesService()


# --------------------------------------------------------------------------------------
# Panel CRUD de Roles
# --------------------------------------------------------------------------------------

class RolesCrudPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._roles: List[Dict[str, Any]] = []
        self._selected_row: Optional[int] = None
        self._build_ui()
        self.reload_roles()

    # ---- UI ----
    def _build_ui(self):
        root = QVBoxLayout(self)

        # Formulario
        form_group = QGroupBox("Crear / Editar rol")
        form_layout = QFormLayout(form_group)

        self.input_nombre = QLineEdit()
        self.input_permisos = QLineEdit()
        self.input_permisos.setPlaceholderText(
            "Permisos separados por coma, ej: ventas.ver,ventas.editar"
        )

        form_layout.addRow(QLabel("Nombre:"), self.input_nombre)
        form_layout.addRow(QLabel("Permisos:"), self.input_permisos)

        btns = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar")
        self.btn_nuevo = QPushButton("Nuevo")
        btns.addWidget(self.btn_guardar)
        btns.addWidget(self.btn_nuevo)
        form_layout.addRow(btns)

        root.addWidget(form_group)

        # Tabla
        table_group = QGroupBox("Roles")
        tlay = QVBoxLayout(table_group)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Permisos", "Acciones"])
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tlay.addWidget(self.table)

        root.addWidget(table_group)

        # Conexiones
        self.btn_guardar.clicked.connect(self._on_save)
        self.btn_nuevo.clicked.connect(self._on_new)
        self.table.cellClicked.connect(self._on_cell_clicked)

    # ---- Datos ----
    def reload_roles(self):
        try:
            self._roles = svc.listar_roles()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar roles:\n{e}")
            self._roles = []

        self._render_table()

    def _render_table(self):
        self.table.setRowCount(0)
        for r in self._roles:
            row = self.table.rowCount()
            self.table.insertRow(row)

            rid = r.get("id")
            nombre = r.get("nombre", "")
            permisos = r.get("permisos")
            if isinstance(permisos, (list, tuple)):
                permisos_text = ", ".join(permisos)
            else:
                permisos_text = ""
                if isinstance(permisos, str) and permisos.strip():
                    try:
                        parsed = json.loads(permisos)
                        if isinstance(parsed, list):
                            permisos_text = ", ".join(parsed)
                        else:
                            permisos_text = permisos
                    except Exception:
                        permisos_text = permisos

            self.table.setItem(row, 0, QTableWidgetItem(str(rid)))
            self.table.setItem(row, 1, QTableWidgetItem(nombre))
            self.table.setItem(row, 2, QTableWidgetItem(permisos_text))

            # acciones: Editar / Eliminar
            w = QWidget()
            lay = QHBoxLayout(w)
            lay.setContentsMargins(0, 0, 0, 0)
            btn_edit = QPushButton("Editar")
            btn_del = QPushButton("Eliminar")
            btn_edit.setProperty("row", row)
            btn_del.setProperty("row", row)
            btn_edit.clicked.connect(self._click_edit_row)
            btn_del.clicked.connect(self._click_delete_row)
            lay.addWidget(btn_edit)
            lay.addWidget(btn_del)
            lay.addStretch()
            self.table.setCellWidget(row, 3, w)

    # ---- Acciones ----
    def _on_new(self):
        self._selected_row = None
        self.input_nombre.clear()
        self.input_permisos.clear()
        self.input_nombre.setFocus()

    def _on_save(self):
        nombre = self.input_nombre.text().strip()
        permisos_raw = self.input_permisos.text().strip()
        permisos = [p.strip() for p in permisos_raw.split(",") if p.strip()] if permisos_raw else []

        if not nombre:
            QMessageBox.warning(self, "Validación", "El nombre del rol es obligatorio.")
            return

        try:
            if self._selected_row is None:
                # Crear
                svc.crear_rol(nombre, permisos or None)
            else:
                # Editar
                rid = self._roles[self._selected_row].get("id")
                svc.actualizar_rol(rid, nombre, permisos or None)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el rol:\n{e}")
            return

        self._on_new()
        self.reload_roles()

    def _on_cell_clicked(self, row: int, col: int):
        # Si clic en fila normal, precarga para editar
        if 0 <= row < len(self._roles):
            self._selected_row = row
            r = self._roles[row]
            self.input_nombre.setText(r.get("nombre", ""))

            # normaliza permisos para mostrar
            permisos = r.get("permisos")
            permisos_text = ""
            if isinstance(permisos, list):
                permisos_text = ", ".join(permisos)
            elif isinstance(permisos, str) and permisos.strip():
                try:
                    parsed = json.loads(permisos)
                    if isinstance(parsed, list):
                        permisos_text = ", ".join(parsed)
                    else:
                        permisos_text = permisos
                except Exception:
                    permisos_text = permisos
            self.input_permisos.setText(permisos_text)

    def _click_edit_row(self):
        btn = self.sender()
        row = btn.property("row")
        if row is None:
            return
        self._on_cell_clicked(int(row), 0)

    def _click_delete_row(self):
        btn = self.sender()
        row = btn.property("row")
        if row is None:
            return
        row = int(row)
        if not (0 <= row < len(self._roles)):
            return

        rid = self._roles[row].get("id")
        nombre = self._roles[row].get("nombre", "")

        if QMessageBox.question(
            self,
            "Eliminar rol",
            f"¿Seguro que quieres eliminar el rol '{nombre}' (ID {rid})?",
        ) != QMessageBox.StandardButton.Yes:
            return

        try:
            svc.eliminar_rol(rid)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el rol:\n{e}")
            return

        self.reload_roles()


# --------------------------------------------------------------------------------------
# Panel de Usuarios ↔ Roles (asignación/cambio)
# --------------------------------------------------------------------------------------

class UsersRolesPanel(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._usuarios: List[Dict[str, Any]] = []
        self._roles: List[Dict[str, Any]] = []
        self._roles_by_id: Dict[Any, str] = {}
        self._build_ui()
        self.reload_all()

    # ---- UI ----
    def _build_ui(self):
        root = QVBoxLayout(self)

        header = QHBoxLayout()
        header.addWidget(QLabel("Usuarios y roles"))
        header.addStretch()
        self.btn_refresh = QPushButton("Refrescar")
        header.addWidget(self.btn_refresh)
        root.addLayout(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Usuario", "Rol actual", "Nuevo rol", "Acción"]
        )
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.ResizeToContents
        )
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        root.addWidget(self.table)

        self.btn_refresh.clicked.connect(self.reload_all)

    # ---- Datos ----
    def reload_all(self):
        try:
            self._usuarios = svc.listar_usuarios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar usuarios:\n{e}")
            self._usuarios = []

        try:
            self._roles = svc.listar_roles()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar roles:\n{e}")
            self._roles = []

        self._roles_by_id = {r["id"]: r.get("nombre", "") for r in self._roles if r.get("id") is not None}
        self._render_table(self._usuarios)

    def _render_table(self, usuarios: List[Dict[str, Any]]):
        self.table.setRowCount(0)

        for u in usuarios:
            row = self.table.rowCount()
            self.table.insertRow(row)

            uid = u.get("id")
            uname = u.get("nombre_usuario") or ""
            rid = u.get("rol_id")
            rol_nombre = self._roles_by_id.get(rid, "— sin rol —")

            # ID
            self.table.setItem(row, 0, QTableWidgetItem(str(uid) if uid is not None else ""))

            # Usuario
            self.table.setItem(row, 1, QTableWidgetItem(uname))

            # Rol actual
            self.table.setItem(row, 2, QTableWidgetItem(rol_nombre))

            # Combo de nuevo rol
            combo = QComboBox()
            combo.addItem("— seleccionar —", None)
            for r in self._roles:
                combo.addItem(r.get("nombre", ""), r.get("id"))
            # preselecciona el actual si lo hay
            if rid is not None:
                idx = combo.findData(rid)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
            self.table.setCellWidget(row, 3, combo)

            # Botón asignar
            btn = QPushButton("Asignar")
            btn.setProperty("usuario_id", uid)
            btn.setProperty("row", row)
            btn.clicked.connect(self._on_assign_clicked)
            self.table.setCellWidget(row, 4, btn)

    # ---- Acción asignar ----
    def _on_assign_clicked(self):
        btn: QPushButton = self.sender()  # type: ignore
        row = int(btn.property("row"))
        uid = btn.property("usuario_id")

        combo: QComboBox = self.table.cellWidget(row, 3)  # type: ignore
        rol_id = combo.currentData()

        if rol_id is None:
            if QMessageBox.question(
                self,
                "Quitar rol",
                "No hay rol seleccionado. ¿Deseas dejar al usuario sin rol?",
            ) != QMessageBox.StandardButton.Yes:
                return

        try:
            svc.asignar_rol_usuario(uid, rol_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo asignar el rol:\n{e}")
            return

        # Actualiza UI: rol actual y cache local
        self._usuarios[row]["rol_id"] = rol_id
        nuevo_nombre = self._roles_by_id.get(rol_id, "— sin rol —")
        self.table.setItem(row, 2, QTableWidgetItem(nuevo_nombre))
        QMessageBox.information(self, "Ok", "Rol actualizado correctamente.")


# --------------------------------------------------------------------------------------
# Tab contenedor
# --------------------------------------------------------------------------------------

class RolesTab(QWidget):
    """
    Pestaña principal de Roles:
      - CRUD de Roles
      - Usuarios ↔ Roles (asignación)
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)

        # Panel superior: CRUD roles
        self._panel_roles = RolesCrudPanel()
        root.addWidget(self._panel_roles)

        # Separador
        sep = QHBoxLayout()
        sep.addItem(QSpacerItem(0, 16, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        root.addLayout(sep)

        # Panel inferior: Usuarios ↔ Roles
        self._panel_users = UsersRolesPanel()
        root.addWidget(self._panel_users)

        # Botón de refresco global
        footer = QHBoxLayout()
        footer.addStretch()
        btn_refresh_all = QPushButton("Refrescar todo")
        btn_refresh_all.clicked.connect(self._refresh_all)
        footer.addWidget(btn_refresh_all)
        root.addLayout(footer)

    def _refresh_all(self):
        self._panel_roles.reload_roles()
        self._panel_users.reload_all()
