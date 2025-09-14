"""
Sistema de gestión de permisos para integración con el frontend
"""

from aplicacion.backend.usuarios.roles import controller
import json
from functools import wraps
from PyQt6.QtWidgets import QMessageBox, QWidget

class PermisosManager:
    """
    Clase principal para manejar permisos de usuarios en el frontend
    """
    
    def __init__(self, user_info):
        """
        Inicializar el gestor de permisos
        
        Args:
            user_info (dict): Información del usuario logueado con keys: id, nombre_usuario, rol_id
        """
        self.user_info = user_info
        self.usuario_id = user_info.get('id')
        self.rol_id = user_info.get('rol_id')
        self.is_admin = self.rol_id == 1
        
        # Cargar permisos del usuario
        self._cargar_permisos()
    
    def _cargar_permisos(self):
        """Cargar permisos desde la base de datos"""
        try:
            if self.is_admin:
                self.permisos = controller.obtener_permisos_admin_controller()
            else:
                self.permisos = controller.obtener_permisos_usuario_controller(self.usuario_id)
                
            if not self.permisos:
                self.permisos = controller.obtener_estructura_permisos_controller()
                
        except Exception as e:
            print(f"Error cargando permisos: {e}")
            self.permisos = controller.obtener_estructura_permisos_controller()
    
    def recargar_permisos(self):
        """Recargar permisos desde la base de datos"""
        self._cargar_permisos()
    
    # ================== VERIFICACIÓN DE PERMISOS ==================
    
    def tiene_permiso(self, modulo, accion):
        """
        Verificar si el usuario tiene un permiso específico
        
        Args:
            modulo (str): Módulo a verificar (ej: 'ventas', 'stock')
            accion (str): Acción a verificar (ej: 'ver', 'crear', 'editar')
        
        Returns:
            bool: True si tiene el permiso, False en caso contrario
        """
        if self.is_admin:
            return True
        
        return self.permisos.get(modulo, {}).get(accion, False)
    
    def permisos_modulo(self, modulo):
        """
        Obtener todos los permisos de un módulo específico
        
        Args:
            modulo (str): Nombre del módulo
        
        Returns:
            dict: Diccionario con todos los permisos del módulo
        """
        return self.permisos.get(modulo, {})
    
    def modulos_permitidos(self):
        """
        Obtener lista de módulos donde el usuario tiene al menos un permiso
        
        Returns:
            list: Lista de nombres de módulos
        """
        modulos = []
        for modulo, acciones in self.permisos.items():
            if any(acciones.values()):
                modulos.append(modulo)
        return modulos
    
    def puede_acceder_modulo(self, modulo):
        """
        Verificar si el usuario puede acceder a un módulo (tiene al menos un permiso)
        
        Args:
            modulo (str): Nombre del módulo
        
        Returns:
            bool: True si puede acceder, False en caso contrario
        """
        if self.is_admin:
            return True
        
        permisos_modulo = self.permisos.get(modulo, {})
        return any(permisos_modulo.values())
    
    # ================== VERIFICACIONES ESPECÍFICAS ==================
    
    # Ventas
    def puede_ver_ventas(self):
        return self.tiene_permiso('ventas', 'ver')
    
    def puede_crear_ventas(self):
        return self.tiene_permiso('ventas', 'crear')
    
    def puede_editar_ventas(self):
        return self.tiene_permiso('ventas', 'editar')
    
    def puede_eliminar_ventas(self):
        return self.tiene_permiso('ventas', 'eliminar')
    
    def puede_descontar_stock(self):
        return self.tiene_permiso('ventas', 'descontar_stock')
    
    # Stock
    def puede_ver_stock(self):
        return self.tiene_permiso('stock', 'ver')
    
    def puede_agregar_stock(self):
        return self.tiene_permiso('stock', 'agregar')
    
    def puede_editar_stock(self):
        return self.tiene_permiso('stock', 'editar')
    
    def puede_eliminar_stock(self):
        return self.tiene_permiso('stock', 'eliminar')
    
    def puede_ver_costos(self):
        return self.tiene_permiso('stock', 'ver_costos')
    
    def puede_editar_precios(self):
        return self.tiene_permiso('stock', 'editar_precios')
    
    # Reportes
    def puede_ver_reportes(self):
        return self.tiene_permiso('reportes', 'ver')
    
    def puede_generar_reportes(self):
        return self.tiene_permiso('reportes', 'generar')
    
    def puede_exportar_reportes(self):
        return self.tiene_permiso('reportes', 'exportar')
    
    def puede_ver_ganancias(self):
        return self.tiene_permiso('reportes', 'ver_ganancias')
    
    # Usuarios
    def puede_ver_usuarios(self):
        return self.tiene_permiso('usuarios', 'ver')
    
    def puede_crear_usuarios(self):
        return self.tiene_permiso('usuarios', 'crear')
    
    def puede_editar_usuarios(self):
        return self.tiene_permiso('usuarios', 'editar')
    
    def puede_eliminar_usuarios(self):
        return self.tiene_permiso('usuarios', 'eliminar')
    
    def puede_gestionar_roles(self):
        return self.tiene_permiso('usuarios', 'gestionar_roles')
    
    # Caja
    def puede_abrir_caja(self):
        return self.tiene_permiso('caja', 'abrir')
    
    def puede_cerrar_caja(self):
        return self.tiene_permiso('caja', 'cerrar')
    
    def puede_ver_movimientos_caja(self):
        return self.tiene_permiso('caja', 'ver_movimientos')
    
    def puede_editar_montos_caja(self):
        return self.tiene_permiso('caja', 'editar_montos')
    
    # Configuración
    def puede_ver_configuracion(self):
        return self.tiene_permiso('configuracion', 'ver')
    
    def puede_editar_configuracion(self):
        return self.tiene_permiso('configuracion', 'editar')
    
    def puede_hacer_backup(self):
        return self.tiene_permiso('configuracion', 'backup')
    
    def puede_restaurar_backup(self):
        return self.tiene_permiso('configuracion', 'restore')
    
    # ================== UTILIDADES PARA FRONTEND ==================
    
    def configurar_widget_permisos(self, widget, permisos_requeridos):
        """
        Configurar un widget basado en permisos
        
        Args:
            widget: Widget de PyQt6 a configurar
            permisos_requeridos (dict): {'modulo': 'accion'} o {'modulo': ['accion1', 'accion2']}
        """
        puede_acceder = True
        
        for modulo, acciones in permisos_requeridos.items():
            if isinstance(acciones, str):
                acciones = [acciones]
            
            # Verificar si tiene al menos uno de los permisos requeridos
            tiene_alguno = any(self.tiene_permiso(modulo, accion) for accion in acciones)
            
            if not tiene_alguno:
                puede_acceder = False
                break
        
        # Configurar widget
        if hasattr(widget, 'setEnabled'):
            widget.setEnabled(puede_acceder)
        
        if hasattr(widget, 'setVisible') and not puede_acceder:
            widget.setVisible(False)
    
    def configurar_botones_toolbar(self, toolbar_buttons):
        """
        Configurar múltiples botones de toolbar
        
        Args:
            toolbar_buttons (dict): {'nombre_boton': (widget, modulo, accion)}
        """
        for nombre, (widget, modulo, accion) in toolbar_buttons.items():
            enabled = self.tiene_permiso(modulo, accion)
            widget.setEnabled(enabled)
            
            if not enabled:
                # Cambiar tooltip para indicar falta de permisos
                if hasattr(widget, 'setToolTip'):
                    widget.setToolTip(f"Sin permisos para {modulo}.{accion}")
    
    def configurar_menu_contextual(self, menu_items):
        """
        Configurar elementos de menú contextual
        
        Args:
            menu_items (list): Lista de (QAction, modulo, accion)
        """
        for action, modulo, accion in menu_items:
            enabled = self.tiene_permiso(modulo, accion)
            action.setEnabled(enabled)
            action.setVisible(enabled)
    
    def obtener_tabs_permitidos(self, configuracion_tabs):
        """
        Obtener lista de tabs que el usuario puede ver
        
        Args:
            configuracion_tabs (dict): {'nombre_tab': {'modulo': 'accion'}}
        
        Returns:
            list: Lista de nombres de tabs permitidos
        """
        tabs_permitidos = []
        
        for tab_name, permisos in configuracion_tabs.items():
            puede_ver = True
            
            for modulo, accion in permisos.items():
                if not self.tiene_permiso(modulo, accion):
                    puede_ver = False
                    break
            
            if puede_ver:
                tabs_permitidos.append(tab_name)
        
        return tabs_permitidos
    
    # ================== INFORMACIÓN DE DEBUGGING ==================
    
    def debug_info(self):
        """Obtener información de debug sobre permisos"""
        return {
            'usuario_id': self.usuario_id,
            'rol_id': self.rol_id,
            'is_admin': self.is_admin,
            'permisos_totales': sum(
                sum(acciones.values()) for acciones in self.permisos.values()
            ),
            'modulos_con_acceso': self.modulos_permitidos(),
            'permisos_completos': self.permisos
        }
    
    def imprimir_permisos(self):
        """Imprimir permisos del usuario en consola (para debugging)"""
        print(f"\n🔐 PERMISOS USUARIO {self.usuario_id} (ROL {self.rol_id})")
        print("=" * 50)
        
        for modulo, acciones in self.permisos.items():
            print(f"\n📁 {modulo.upper()}:")
            for accion, permitido in acciones.items():
                estado = "✅" if permitido else "❌"
                print(f"  {estado} {accion}")


# ================== DECORADORES ==================

def requiere_permiso(modulo, accion, mensaje_error=None):
    """
    Decorador para métodos que requieren permisos específicos
    
    Args:
        modulo (str): Módulo requerido
        accion (str): Acción requerida
        mensaje_error (str, optional): Mensaje personalizado de error
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Verificar si la clase tiene un PermisosManager
            if not hasattr(self, 'permisos') or not isinstance(self.permisos, PermisosManager):
                print(f"Advertencia: {self.__class__.__name__} no tiene PermisosManager configurado")
                return func(self, *args, **kwargs)
            
            # Verificar permisos
            if not self.permisos.tiene_permiso(modulo, accion):
                mensaje = mensaje_error or f"Sin permisos para {modulo}.{accion}"
                
                # Si la clase hereda de QWidget, mostrar mensaje
                if isinstance(self, QWidget):
                    QMessageBox.warning(self, "Sin permisos", mensaje)
                else:
                    print(f"⚠️  {mensaje}")
                
                return None
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


def requiere_admin(mensaje_error=None):
    """
    Decorador para métodos que requieren ser administrador
    
    Args:
        mensaje_error (str, optional): Mensaje personalizado de error
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'permisos') or not isinstance(self.permisos, PermisosManager):
                print(f"Advertencia: {self.__class__.__name__} no tiene PermisosManager configurado")
                return func(self, *args, **kwargs)
            
            if not self.permisos.is_admin:
                mensaje = mensaje_error or "Esta función requiere permisos de administrador"
                
                if isinstance(self, QWidget):
                    QMessageBox.warning(self, "Acceso Denegado", mensaje)
                else:
                    print(f"⚠️  {mensaje}")
                
                return None
            
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


# ================== CLASE BASE PARA WIDGETS ==================

class BaseWidgetConPermisos:
    """
    Clase base para widgets que necesitan manejo de permisos
    """
    
    def __init__(self, user_info):
        self.user_info = user_info
        self.permisos = PermisosManager(user_info)
        self.setup_access_control()
    
    def setup_access_control(self):
        """Override este método para configurar controles de acceso específicos"""
        pass
    
    def recargar_permisos(self):
        """Recargar permisos y reconfigurar controles"""
        self.permisos.recargar_permisos()
        self.setup_access_control()
    
    def ejecutar_con_permiso(self, modulo, accion, callback, *args, **kwargs):
        """
        Ejecutar función solo si tiene permisos
        
        Args:
            modulo (str): Módulo requerido
            accion (str): Acción requerida
            callback: Función a ejecutar
            *args, **kwargs: Argumentos para la función
        """
        if self.permisos.tiene_permiso(modulo, accion):
            return callback(*args, **kwargs)
        else:
            if hasattr(self, 'parent') and hasattr(self.parent(), 'show'):
                QMessageBox.warning(
                    self.parent(), 
                    "Sin permisos", 
                    f"No tiene permisos para: {modulo}.{accion}"
                )
            else:
                print(f"⚠️  Sin permisos para: {modulo}.{accion}")
            return None


# ================== FUNCIONES UTILITARIAS ==================

def crear_permisos_manager(user_info):
    """
    Factory function para crear un PermisosManager
    
    Args:
        user_info (dict): Información del usuario
    
    Returns:
        PermisosManager: Instancia configurada
    """
    return PermisosManager(user_info)


def verificar_permisos_rapido(user_info, modulo, accion):
    """
    Verificación rápida de permisos sin crear instancia completa
    
    Args:
        user_info (dict): Información del usuario
        modulo (str): Módulo a verificar
        accion (str): Acción a verificar
    
    Returns:
        bool: True si tiene el permiso
    """
    if user_info.get('rol_id') == 1:  # Admin
        return True
    
    return controller.validar_permiso_usuario_controller(
        user_info.get('id'), modulo, accion
    )


# ================== EJEMPLO DE USO ==================

if __name__ == "__main__":
    # Ejemplo de uso básico
    user_info = {"id": 1, "nombre_usuario": "admin", "rol_id": 1}
    permisos = PermisosManager(user_info)
    
    # Verificar permisos
    print("¿Puede crear ventas?", permisos.puede_crear_ventas())
    print("¿Puede ver reportes?", permisos.puede_ver_reportes())
    
    # Debug info
    permisos.imprimir_permisos()
    
    # Información de debug
    debug = permisos.debug_info()
    print(f"\nPermisos totales: {debug['permisos_totales']}")
    print(f"Módulos con acceso: {debug['modulos_con_acceso']}")