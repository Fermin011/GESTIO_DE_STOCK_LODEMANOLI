from aplicacion.backend.usuarios.roles import controller
import json

def imprimir_separador(titulo=""):
    print("\n" + "="*60)
    if titulo:
        print(f"  {titulo}")
        print("="*60)

def imprimir_permisos(permisos_dict, titulo="PERMISOS"):
    print(f"\n{titulo}:")
    print("-" * 40)
    for modulo, acciones in permisos_dict.items():
        print(f"📁 {modulo.upper()}:")
        for accion, valor in acciones.items():
            estado = "✅" if valor else "❌"
            print(f"  {estado} {accion}")
        print()

def menu_principal():
    while True:
        imprimir_separador("SISTEMA DE ROLES Y PERMISOS - TESTING")
        print("1️⃣  Gestión de Roles")
        print("2️⃣  Gestión de Permisos de Usuario")
        print("3️⃣  Plantillas de Permisos")
        print("4️⃣  Utilidades del Sistema")
        print("5️⃣  Configuración Inicial")
        print("6️⃣  Tests Avanzados")
        print("0️⃣  Salir")
        print("="*60)

        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            menu_gestion_roles()
        elif opcion == "2":
            menu_permisos_usuario()
        elif opcion == "3":
            menu_plantillas()
        elif opcion == "4":
            menu_utilidades()
        elif opcion == "5":
            menu_configuracion_inicial()
        elif opcion == "6":
            menu_tests_avanzados()
        elif opcion == "0":
            print("👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida.")

def menu_gestion_roles():
    while True:
        imprimir_separador("GESTIÓN DE ROLES")
        print("1. Crear rol personalizado")
        print("2. Editar rol existente")
        print("3. Ver rol por ID")
        print("4. Listar todos los roles")
        print("5. Eliminar rol")
        print("6. Clonar rol")
        print("7. Comparar dos roles")
        print("0. Volver al menú principal")

        opcion = input("\nElegí una opción: ").strip()

        if opcion == "1":
            crear_rol_personalizado()
        elif opcion == "2":
            editar_rol_existente()
        elif opcion == "3":
            ver_rol_por_id()
        elif opcion == "4":
            listar_todos_los_roles()
        elif opcion == "5":
            eliminar_rol()
        elif opcion == "6":
            clonar_rol()
        elif opcion == "7":
            comparar_roles()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def crear_rol_personalizado():
    imprimir_separador("CREAR ROL PERSONALIZADO")
    
    nombre = input("Nombre del nuevo rol: ").strip()
    if not nombre:
        print("❌ El nombre no puede estar vacío.")
        return
    
    print("\n¿Qué tipo de rol querés crear?")
    print("1. Rol vacío (sin permisos)")
    print("2. Basado en empleado básico")
    print("3. Basado en supervisor")
    print("4. Basado en administrador")
    print("5. Personalizado paso a paso")
    
    tipo = input("Elegí una opción: ").strip()
    
    if tipo == "1":
        permisos = controller.obtener_estructura_permisos_controller()
    elif tipo == "2":
        permisos = controller.obtener_permisos_empleado_basico_controller()
    elif tipo == "3":
        permisos = controller.obtener_permisos_supervisor_controller()
    elif tipo == "4":
        permisos = controller.obtener_permisos_admin_controller()
    elif tipo == "5":
        permisos = crear_permisos_personalizados()
    else:
        print("❌ Opción inválida.")
        return
    
    imprimir_permisos(permisos, f"PERMISOS PARA '{nombre}'")
    
    confirmar = input("\n¿Confirmar creación del rol? (s/n): ").strip().lower()
    if confirmar == 's':
        resultado = controller.crear_rol_controller(nombre, permisos)
        if resultado:
            print(f"✅ Rol '{nombre}' creado con ID: {resultado}")
        else:
            print("❌ Error al crear el rol.")
    else:
        print("❌ Creación cancelada.")

def crear_permisos_personalizados():
    permisos = controller.obtener_estructura_permisos_controller()
    
    print("\n🔧 CONFIGURACIÓN PERSONALIZADA DE PERMISOS")
    print("Para cada módulo y acción, ingresá 's' para SÍ o 'n' para NO")
    print("Presioná Enter para mantener el valor por defecto (No)")
    
    for modulo, acciones in permisos.items():
        print(f"\n📁 MÓDULO: {modulo.upper()}")
        for accion in acciones:
            respuesta = input(f"  ¿Permitir '{accion}'? (s/n): ").strip().lower()
            permisos[modulo][accion] = respuesta == 's'
    
    return permisos

def editar_rol_existente():
    imprimir_separador("EDITAR ROL EXISTENTE")
    
    listar_todos_los_roles()
    
    try:
        rol_id = int(input("\nID del rol a editar: ").strip())
        rol = controller.obtener_rol_controller(rol_id)
        
        if not rol:
            print("❌ Rol no encontrado.")
            return
        
        print(f"\n📝 Editando rol: {rol['nombre']}")
        imprimir_permisos(rol['permisos'], "PERMISOS ACTUALES")
        
        print("\n¿Cómo querés editar los permisos?")
        print("1. Modificar permisos específicos")
        print("2. Reemplazar con plantilla")
        print("3. Habilitar/deshabilitar módulo completo")
        
        opcion = input("Elegí una opción: ").strip()
        
        if opcion == "1":
            nuevos_permisos = modificar_permisos_especificos(rol['permisos'])
        elif opcion == "2":
            nuevos_permisos = seleccionar_plantilla()
        elif opcion == "3":
            nuevos_permisos = modificar_modulo_completo(rol['permisos'])
        else:
            print("❌ Opción inválida.")
            return
        
        if nuevos_permisos:
            imprimir_permisos(nuevos_permisos, "NUEVOS PERMISOS")
            confirmar = input("\n¿Confirmar cambios? (s/n): ").strip().lower()
            
            if confirmar == 's':
                if controller.editar_rol_controller(rol_id, nuevos_permisos):
                    print("✅ Rol editado correctamente.")
                else:
                    print("❌ Error al editar el rol.")
            else:
                print("❌ Edición cancelada.")
    
    except ValueError:
        print("❌ ID inválido.")

def modificar_permisos_especificos(permisos_actuales):
    permisos = permisos_actuales.copy()
    
    while True:
        print("\n🔧 MODIFICAR PERMISOS ESPECÍFICOS")
        print("Formato: modulo.accion (ej: ventas.crear)")
        print("Escribí 'fin' para terminar")
        
        entrada = input("Permiso a cambiar: ").strip()
        
        if entrada.lower() == 'fin':
            break
        
        if '.' not in entrada:
            print("❌ Formato inválido. Usa: modulo.accion")
            continue
        
        modulo, accion = entrada.split('.', 1)
        
        if modulo not in permisos:
            print(f"❌ Módulo '{modulo}' no existe.")
            continue
        
        if accion not in permisos[modulo]:
            print(f"❌ Acción '{accion}' no existe en el módulo '{modulo}'.")
            continue
        
        valor_actual = permisos[modulo][accion]
        nuevo_valor = not valor_actual
        permisos[modulo][accion] = nuevo_valor
        
        estado = "✅ Habilitado" if nuevo_valor else "❌ Deshabilitado"
        print(f"🔄 {modulo}.{accion} → {estado}")
    
    return permisos

def modificar_modulo_completo(permisos_actuales):
    permisos = permisos_actuales.copy()
    
    print("\n📁 MÓDULOS DISPONIBLES:")
    for i, modulo in enumerate(permisos.keys(), 1):
        print(f"{i}. {modulo}")
    
    try:
        seleccion = int(input("\nSeleccionar módulo: ")) - 1
        modulos = list(permisos.keys())
        
        if 0 <= seleccion < len(modulos):
            modulo = modulos[seleccion]
            
            print(f"\n¿Qué hacer con el módulo '{modulo}'?")
            print("1. Habilitar todo")
            print("2. Deshabilitar todo")
            
            accion = input("Elegí una opción: ").strip()
            
            if accion == "1":
                for permiso in permisos[modulo]:
                    permisos[modulo][permiso] = True
                print(f"✅ Todos los permisos de '{modulo}' habilitados.")
            elif accion == "2":
                for permiso in permisos[modulo]:
                    permisos[modulo][permiso] = False
                print(f"❌ Todos los permisos de '{modulo}' deshabilitados.")
            else:
                print("❌ Opción inválida.")
                return None
        else:
            print("❌ Selección inválida.")
            return None
    
    except ValueError:
        print("❌ Número inválido.")
        return None
    
    return permisos

def seleccionar_plantilla():
    print("\n📋 PLANTILLAS DISPONIBLES:")
    print("1. Empleado básico")
    print("2. Supervisor")
    print("3. Administrador")
    print("4. Sin permisos")
    
    opcion = input("Elegí una plantilla: ").strip()
    
    if opcion == "1":
        return controller.obtener_permisos_empleado_basico_controller()
    elif opcion == "2":
        return controller.obtener_permisos_supervisor_controller()
    elif opcion == "3":
        return controller.obtener_permisos_admin_controller()
    elif opcion == "4":
        return controller.obtener_estructura_permisos_controller()
    else:
        print("❌ Opción inválida.")
        return None

def ver_rol_por_id():
    try:
        rol_id = int(input("ID del rol a ver: ").strip())
        rol = controller.obtener_rol_controller(rol_id)
        
        if rol:
            imprimir_separador(f"ROL: {rol['nombre']} (ID: {rol['id']})")
            imprimir_permisos(rol['permisos'])
            
            print("PERMISOS RAW (JSON):")
            print(rol['permisos_raw'])
        else:
            print("❌ Rol no encontrado.")
    except ValueError:
        print("❌ ID inválido.")

def listar_todos_los_roles():
    roles = controller.listar_roles_controller()
    
    if roles:
        imprimir_separador("TODOS LOS ROLES")
        for rol in roles:
            print(f"🔹 ID: {rol['id']} | Nombre: {rol['nombre']}")
        print()
    else:
        print("❌ No hay roles registrados.")

def eliminar_rol():
    listar_todos_los_roles()
    
    try:
        rol_id = int(input("ID del rol a eliminar: ").strip())
        
        # Mostrar información del rol antes de eliminar
        rol = controller.obtener_rol_controller(rol_id)
        if not rol:
            print("❌ Rol no encontrado.")
            return
        
        print(f"\n⚠️  ELIMINAR ROL: {rol['nombre']}")
        confirmar = input("¿Estás seguro? (s/n): ").strip().lower()
        
        if confirmar == 's':
            exito, mensaje = controller.eliminar_rol_controller(rol_id)
            if exito:
                print(f"✅ {mensaje}")
            else:
                print(f"❌ {mensaje}")
        else:
            print("❌ Eliminación cancelada.")
    
    except ValueError:
        print("❌ ID inválido.")

def clonar_rol():
    listar_todos_los_roles()
    
    try:
        rol_id = int(input("ID del rol a clonar: ").strip())
        nuevo_nombre = input("Nombre del nuevo rol: ").strip()
        
        if not nuevo_nombre:
            print("❌ El nombre no puede estar vacío.")
            return
        
        resultado = controller.clonar_rol_controller(rol_id, nuevo_nombre)
        if resultado:
            print(f"✅ Rol clonado correctamente. Nuevo ID: {resultado}")
        else:
            print("❌ Error al clonar el rol.")
    
    except ValueError:
        print("❌ ID inválido.")

def comparar_roles():
    listar_todos_los_roles()
    
    try:
        rol_id_1 = int(input("ID del primer rol: ").strip())
        rol_id_2 = int(input("ID del segundo rol: ").strip())
        
        comparacion = controller.comparar_roles_controller(rol_id_1, rol_id_2)
        
        if comparacion:
            imprimir_separador("COMPARACIÓN DE ROLES")
            print(f"ROL 1: {comparacion['rol1']['nombre']} (ID: {comparacion['rol1']['id']})")
            print(f"ROL 2: {comparacion['rol2']['nombre']} (ID: {comparacion['rol2']['id']})")
            
            print("\n🔍 DIFERENCIAS ENCONTRADAS:")
            if not any(comparacion['diferencias'].values()):
                print("✅ Los roles tienen permisos idénticos.")
            else:
                for modulo, diferencias in comparacion['diferencias'].items():
                    if diferencias:
                        print(f"\n📁 {modulo.upper()}:")
                        for accion, valores in diferencias.items():
                            rol1_estado = "✅" if valores['rol1'] else "❌"
                            rol2_estado = "✅" if valores['rol2'] else "❌"
                            print(f"  {accion}: {rol1_estado} vs {rol2_estado}")
        else:
            print("❌ Error al comparar roles.")
    
    except ValueError:
        print("❌ ID inválido.")

def menu_permisos_usuario():
    while True:
        imprimir_separador("GESTIÓN DE PERMISOS DE USUARIO")
        print("1. Ver permisos de usuario")
        print("2. Verificar permiso específico")
        print("3. Asignar rol a usuario")
        print("4. Estadísticas de uso")
        print("0. Volver al menú principal")

        opcion = input("\nElegí una opción: ").strip()

        if opcion == "1":
            ver_permisos_usuario()
        elif opcion == "2":
            verificar_permiso_especifico()
        elif opcion == "3":
            asignar_rol_usuario()
        elif opcion == "4":
            mostrar_estadisticas()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def ver_permisos_usuario():
    try:
        usuario_id = int(input("ID del usuario: ").strip())
        permisos = controller.obtener_permisos_usuario_controller(usuario_id)
        
        if permisos:
            imprimir_separador(f"PERMISOS DEL USUARIO {usuario_id}")
            imprimir_permisos(permisos)
        else:
            print("❌ Usuario no encontrado o sin permisos.")
    except ValueError:
        print("❌ ID inválido.")

def verificar_permiso_especifico():
    try:
        usuario_id = int(input("ID del usuario: ").strip())
        modulo = input("Módulo (ej: ventas): ").strip()
        accion = input("Acción (ej: crear): ").strip()
        
        tiene_permiso = controller.validar_permiso_usuario_controller(usuario_id, modulo, accion)
        
        estado = "✅ SÍ" if tiene_permiso else "❌ NO"
        print(f"\n🔍 Usuario {usuario_id} puede '{accion}' en '{modulo}': {estado}")
    except ValueError:
        print("❌ ID inválido.")

def asignar_rol_usuario():
    listar_todos_los_roles()
    
    try:
        usuario_id = int(input("\nID del usuario: ").strip())
        rol_id = int(input("ID del rol a asignar: ").strip())
        
        exito, mensaje = controller.asignar_rol_usuario_controller(usuario_id, rol_id)
        
        if exito:
            print(f"✅ {mensaje}")
        else:
            print(f"❌ {mensaje}")
    except ValueError:
        print("❌ ID inválido.")

def mostrar_estadisticas():
    estadisticas = controller.obtener_estadisticas_roles_controller()
    
    if 'error' in estadisticas:
        print(f"❌ Error: {estadisticas['error']}")
        return
    
    imprimir_separador("ESTADÍSTICAS DEL SISTEMA")
    print(f"👥 Total de usuarios: {estadisticas['total_usuarios']}")
    print(f"🏷️  Total de roles: {estadisticas['total_roles']}")
    print(f"⚠️  Usuarios sin rol: {estadisticas['usuarios_sin_rol']}")
    
    print("\n📊 DETALLE POR ROL:")
    for detalle in estadisticas['roles_detalle']:
        print(f"  🔹 {detalle['rol']}: {detalle['usuarios_asignados']} usuarios ({detalle['porcentaje_uso']:.1f}%)")

def menu_plantillas():
    while True:
        imprimir_separador("PLANTILLAS DE PERMISOS")
        print("1. Ver plantilla de Administrador")
        print("2. Ver plantilla de Empleado Básico")
        print("3. Ver plantilla de Supervisor")
        print("4. Ver estructura base (sin permisos)")
        print("5. Listar módulos disponibles")
        print("0. Volver al menú principal")

        opcion = input("\nElegí una opción: ").strip()

        if opcion == "1":
            permisos = controller.obtener_permisos_admin_controller()
            imprimir_permisos(permisos, "PLANTILLA ADMINISTRADOR")
        elif opcion == "2":
            permisos = controller.obtener_permisos_empleado_basico_controller()
            imprimir_permisos(permisos, "PLANTILLA EMPLEADO BÁSICO")
        elif opcion == "3":
            permisos = controller.obtener_permisos_supervisor_controller()
            imprimir_permisos(permisos, "PLANTILLA SUPERVISOR")
        elif opcion == "4":
            permisos = controller.obtener_estructura_permisos_controller()
            imprimir_permisos(permisos, "ESTRUCTURA BASE (SIN PERMISOS)")
        elif opcion == "5":
            mostrar_modulos_disponibles()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def mostrar_modulos_disponibles():
    modulos = controller.listar_modulos_disponibles_controller()
    
    imprimir_separador("MÓDULOS Y ACCIONES DISPONIBLES")
    for modulo in modulos:
        print(f"📁 {modulo['nombre'].upper()}:")
        for accion in modulo['acciones']:
            print(f"  • {accion}")
        print()

def menu_utilidades():
    while True:
        imprimir_separador("UTILIDADES DEL SISTEMA")
        print("1. Crear roles por defecto")
        print("2. Ver estadísticas completas")
        print("3. Exportar configuración de rol")
        print("4. Verificar integridad del sistema")
        print("0. Volver al menú principal")

        opcion = input("\nElegí una opción: ").strip()

        if opcion == "1":
            resultado = controller.crear_roles_por_defecto_controller()
            print(f"ℹ️  {resultado}")
        elif opcion == "2":
            mostrar_estadisticas()
        elif opcion == "3":
            exportar_configuracion_rol()
        elif opcion == "4":
            verificar_integridad()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def exportar_configuracion_rol():
    listar_todos_los_roles()
    
    try:
        rol_id = int(input("\nID del rol a exportar: ").strip())
        rol = controller.obtener_rol_controller(rol_id)
        
        if rol:
            archivo = f"rol_{rol['nombre'].lower().replace(' ', '_')}_config.json"
            
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump({
                    'nombre': rol['nombre'],
                    'permisos': rol['permisos']
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuración exportada a: {archivo}")
        else:
            print("❌ Rol no encontrado.")
    except ValueError:
        print("❌ ID inválido.")
    except Exception as e:
        print(f"❌ Error al exportar: {e}")

def verificar_integridad():
    print("🔍 Verificando integridad del sistema...")
    
    # Verificar estructura de roles
    roles = controller.listar_roles_controller()
    estructura_base = controller.obtener_estructura_permisos_controller()
    
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
        print("⚠️  PROBLEMAS ENCONTRADOS:")
        for problema in problemas:
            print(f"  • {problema}")
    else:
        print("✅ Sistema íntegro. No se encontraron problemas.")

def menu_configuracion_inicial():
    while True:
        imprimir_separador("CONFIGURACIÓN INICIAL")
        print("1. Crear roles por defecto")
        print("2. Crear rol de administrador")
        print("3. Crear rol de empleado básico") 
        print("4. Crear rol de supervisor")
        print("5. Setup completo del sistema")
        print("0. Volver al menú principal")

        opcion = input("\nElegí una opción: ").strip()

        if opcion == "1":
            resultado = controller.crear_roles_por_defecto_controller()
            print(f"ℹ️  {resultado}")
        elif opcion == "2":
            crear_rol_admin()
        elif opcion == "3":
            crear_rol_empleado()
        elif opcion == "4":
            crear_rol_supervisor()
        elif opcion == "5":
            setup_completo()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def crear_rol_admin():
    nombre = input("Nombre del rol administrador [Administrador]: ").strip()
    if not nombre:
        nombre = "Administrador"
    
    permisos = controller.obtener_permisos_admin_controller()
    resultado = controller.crear_rol_controller(nombre, permisos)
    
    if resultado:
        print(f"✅ Rol '{nombre}' creado con ID: {resultado}")
    else:
        print("❌ Error al crear el rol.")

def crear_rol_empleado():
    nombre = input("Nombre del rol empleado [Empleado]: ").strip()
    if not nombre:
        nombre = "Empleado"
    
    permisos = controller.obtener_permisos_empleado_basico_controller()
    resultado = controller.crear_rol_controller(nombre, permisos)
    
    if resultado:
        print(f"✅ Rol '{nombre}' creado con ID: {resultado}")
    else:
        print("❌ Error al crear el rol.")

def crear_rol_supervisor():
    nombre = input("Nombre del rol supervisor [Supervisor]: ").strip()
    if not nombre:
        nombre = "Supervisor"
    
    permisos = controller.obtener_permisos_supervisor_controller()
    resultado = controller.crear_rol_controller(nombre, permisos)
    
    if resultado:
        print(f"✅ Rol '{nombre}' creado con ID: {resultado}")
    else:
        print("❌ Error al crear el rol.")

def setup_completo():
    print("🚀 CONFIGURACIÓN COMPLETA DEL SISTEMA")
    print("Se crearán los roles por defecto y se verificará la integridad.")
    
    confirmar = input("¿Continuar? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Setup cancelado.")
        return
    
    # Crear roles por defecto
    resultado = controller.crear_roles_por_defecto_controller()
    print(f"1️⃣  {resultado}")
    
    # Verificar integridad
    print("2️⃣  Verificando integridad...")
    verificar_integridad()
    
    # Mostrar estadísticas
    print("3️⃣  Estadísticas del sistema:")
    mostrar_estadisticas()
    
    print("\n✅ Setup completo finalizado.")

def menu_tests_avanzados():
    while True:
        imprimir_separador("TESTS AVANZADOS")
        print("1. Test de rendimiento")
        print("2. Test de consistencia")
        print("3. Simulación de usuarios")
        print("4. Test de carga masiva")
        print("0. Volver al menú principal")

        opcion = input("\nElegí una opción: ").strip()

        if opcion == "1":
            test_rendimiento()
        elif opcion == "2":
            test_consistencia()
        elif opcion == "3":
            simulacion_usuarios()
        elif opcion == "4":
            test_carga_masiva()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida.")

def test_rendimiento():
    import time
    
    print("⏱️  TEST DE RENDIMIENTO")
    
    # Test 1: Listar roles
    inicio = time.time()
    roles = controller.listar_roles_controller()
    tiempo_listar = time.time() - inicio
    print(f"Listar {len(roles)} roles: {tiempo_listar:.4f}s")
    
    # Test 2: Obtener permisos de usuario (si hay roles)
    if roles:
        inicio = time.time()
        for _ in range(100):
            controller.obtener_permisos_usuario_controller(1)
        tiempo_permisos = time.time() - inicio
        print(f"100 consultas de permisos: {tiempo_permisos:.4f}s")
    
    # Test 3: Validaciones de permisos
    if roles:
        inicio = time.time()
        for _ in range(1000):
            controller.validar_permiso_usuario_controller(1, "ventas", "crear")
        tiempo_validaciones = time.time() - inicio
        print(f"1000 validaciones de permisos: {tiempo_validaciones:.4f}s")

def test_consistencia():
    print("🔍 TEST DE CONSISTENCIA")
    
    # Verificar que todos los roles tengan la estructura completa
    roles = controller.listar_roles_controller()
    estructura_base = controller.obtener_estructura_permisos_controller()
    
    inconsistencias = 0
    
    for rol in roles:
        for modulo in estructura_base:
            if modulo not in rol['permisos']:
                print(f"❌ Rol '{rol['nombre']}' falta módulo '{modulo}'")
                inconsistencias += 1
            else:
                for accion in estructura_base[modulo]:
                    if accion not in rol['permisos'][modulo]:
                        print(f"❌ Rol '{rol['nombre']}' falta acción '{modulo}.{accion}'")
                        inconsistencias += 1
    
    if inconsistencias == 0:
        print("✅ Todos los roles son consistentes.")
    else:
        print(f"⚠️  Se encontraron {inconsistencias} inconsistencias.")

def simulacion_usuarios():
    print("👥 SIMULACIÓN DE USUARIOS")
    
    # Simular diferentes tipos de usuarios
    usuarios_simulados = [
        {"id": 1, "tipo": "admin", "rol_id": 1},
        {"id": 2, "tipo": "empleado", "rol_id": 2},
        {"id": 3, "tipo": "supervisor", "rol_id": 3},
    ]
    
    acciones_comunes = [
        ("ventas", "ver"),
        ("ventas", "crear"),
        ("stock", "ver"),
        ("reportes", "generar"),
        ("usuarios", "gestionar")
    ]
    
    for usuario in usuarios_simulados:
        print(f"\n👤 Usuario {usuario['id']} ({usuario['tipo']}):")
        for modulo, accion in acciones_comunes:
            puede = controller.validar_permiso_usuario_controller(usuario['id'], modulo, accion)
            estado = "✅ Puede" if puede else "❌ No puede"
            print(f"  {estado} {modulo}.{accion}")

def test_carga_masiva():
    print("📊 TEST DE CARGA MASIVA")
    
    cantidad = input("¿Cuántos roles de prueba crear? [10]: ").strip()
    try:
        cantidad = int(cantidad) if cantidad else 10
    except ValueError:
        cantidad = 10
    
    import time
    
    print(f"Creando {cantidad} roles de prueba...")
    inicio = time.time()
    
    creados = 0
    for i in range(cantidad):
        nombre = f"TestRole_{i+1}"
        permisos = controller.obtener_permisos_empleado_basico_controller()
        
        if controller.crear_rol_controller(nombre, permisos):
            creados += 1
    
    tiempo_total = time.time() - inicio
    print(f"✅ Creados {creados}/{cantidad} roles en {tiempo_total:.2f}s")
    print(f"📈 Promedio: {tiempo_total/cantidad:.4f}s por rol")

if __name__ == "__main__":
    menu_principal()

# Para ejecutar:
# python -m aplicacion.backend.usuarios.roles.test_roles

