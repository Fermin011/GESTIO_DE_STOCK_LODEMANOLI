from aplicacion.backend.costos import controller
from datetime import date, datetime

def mostrar_resumen_general():
    """Muestra un resumen general de todos los costos e impuestos"""
    print("\n=== RESUMEN GENERAL DE COSTOS ===")
    
    resultado = controller.obtener_resumen_completo_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        costos = data["costos_operativos"]
        impuestos = data["impuestos"]
        general = data["resumen_general"]
        
        print("-" * 70)
        print("📊 COSTOS OPERATIVOS:")
        print(f"   • Cantidad: {costos['cantidad']}")
        print(f"   • Total: ${costos['total']:,.2f}")
        print(f"   • Recurrentes: ${costos['recurrentes']:,.2f}")
        print(f"   • Una vez: ${costos['una_vez']:,.2f}")
        
        print("\n💰 IMPUESTOS:")
        print(f"   • Cantidad total: {impuestos['cantidad']}")
        print(f"   • Impuestos fijos: {impuestos['cantidad_fijo']} (${impuestos['total_fijo']:,.2f})")
        print(f"   • Impuestos porcentaje: {impuestos['cantidad_porcentaje']} ({impuestos['total_porcentaje']:.1f}%)")
        
        print(f"\n🎯 RESUMEN GENERAL:")
        print(f"   • Total costos fijos: ${general['total_costos_fijos']:,.2f}")
        print(f"   • Total porcentajes: {general['porcentajes_aplicables']:.1f}%")
        print("-" * 70)
    else:
        print(f"❌ {resultado['message']}")

def mostrar_costos_operativos():
    """Muestra todos los costos operativos activos"""
    resultado = controller.listar_costos_activos_controller()
    
    if resultado["success"]:
        costos = resultado["data"]["costos"]
        resumen = resultado["data"]["resumen"]
        
        print("\n=== COSTOS OPERATIVOS ACTIVOS ===")
        print("-" * 80)
        print(f"{'ID':<5} {'Nombre':<25} {'Monto':<12} {'Fecha Inicio':<12} {'Recurrente':<10} {'Estado':<8}")
        print("-" * 80)
        
        for costo in costos:
            recurrente = "Sí" if costo['recurrente'] else "No"
            estado = "Activo" if costo['activo'] else "Inactivo"
            print(f"{costo['id']:<5} {costo['nombre']:<25} ${costo['monto']:<11,.0f} {costo['fecha_inicio']:<12} {recurrente:<10} {estado:<8}")
        
        print("-" * 80)
        print(f"📊 RESUMEN:")
        print(f"   • Total costos: {resumen['cantidad_costos']}")
        print(f"   • Monto total: ${resumen['total_costos']:,.2f}")
        print(f"   • Costos recurrentes: ${resumen['costos_recurrentes']:,.2f}")
        print(f"   • Costos una vez: ${resumen['costos_una_vez']:,.2f}")
        print("-" * 80)
    else:
        print(f"❌ {resultado['message']}")

def mostrar_impuestos():
    """Muestra todos los impuestos activos"""
    resultado = controller.listar_impuestos_activos_controller()
    
    if resultado["success"]:
        impuestos = resultado["data"]["impuestos"]
        resumen = resultado["data"]["resumen"]
        
        print("\n=== IMPUESTOS ACTIVOS ===")
        print("-" * 70)
        print(f"{'ID':<5} {'Nombre':<25} {'Tipo':<12} {'Valor':<12} {'Estado':<8}")
        print("-" * 70)
        
        for impuesto in impuestos:
            if impuesto['tipo'] == 'porcentaje':
                valor_display = f"{impuesto['valor']:.1f}%"
            else:
                valor_display = f"${impuesto['valor']:,.2f}"
            
            estado = "Activo" if impuesto['activo'] else "Inactivo"
            print(f"{impuesto['id']:<5} {impuesto['nombre']:<25} {impuesto['tipo']:<12} {valor_display:<12} {estado:<8}")
        
        print("-" * 70)
        print(f"📊 RESUMEN:")
        print(f"   • Total impuestos: {resumen['cantidad_impuestos']}")
        print(f"   • Impuestos fijos: {resumen['impuestos_fijo']} (${resumen['total_fijo']:,.2f})")
        print(f"   • Impuestos porcentaje: {resumen['impuestos_porcentaje']} ({resumen['total_porcentaje']:.1f}%)")
        print("-" * 70)
    else:
        print(f"❌ {resultado['message']}")

def crear_costo_operativo():
    """Maneja la creación de un nuevo costo operativo"""
    print("\n=== CREAR COSTO OPERATIVO ===")
    
    try:
        nombre = input("Nombre del costo: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            return
        
        monto_input = input("Monto: $").strip()
        monto = float(monto_input) if monto_input else None
        
        if monto is None or monto < 0:
            print("❌ Debe ingresar un monto válido mayor o igual a 0")
            return
        
        fecha_input = input("Fecha de inicio (YYYY-MM-DD) [Enter para hoy]: ").strip()
        fecha_inicio = fecha_input if fecha_input else date.today().isoformat()
        
        recurrente_input = input("¿Es recurrente? (s/N): ").lower().strip()
        recurrente = recurrente_input in ['s', 'si', 'y', 'yes']
        
        print(f"\n📋 Resumen:")
        print(f"   • Nombre: {nombre}")
        print(f"   • Monto: ${monto:,.2f}")
        print(f"   • Fecha inicio: {fecha_inicio}")
        print(f"   • Recurrente: {'Sí' if recurrente else 'No'}")
        
        confirmar = input(f"\n¿Crear este costo operativo? (s/N): ").lower()
        if confirmar != 's':
            print("Operación cancelada.")
            return
        
        resultado = controller.crear_costo_operativo_controller(
            nombre=nombre,
            monto=monto,
            fecha_inicio=fecha_inicio,
            recurrente=recurrente
        )
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\n✅ Costo operativo creado exitosamente!")
            print(f"   ID: {data['id']}")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Monto: ${data['monto']:,.2f}")
        else:
            print(f"❌ Error: {resultado['message']}")
            
    except ValueError:
        print("❌ Entrada inválida. Operación cancelada.")

def crear_impuesto():
    """Maneja la creación de un nuevo impuesto"""
    print("\n=== CREAR IMPUESTO ===")
    
    try:
        nombre = input("Nombre del impuesto: ").strip()
        if not nombre:
            print("❌ El nombre es obligatorio")
            return
        
        print("\nTipos disponibles:")
        print("1. porcentaje - Impuesto como porcentaje (ej: 21% IVA)")
        print("2. fijo - Impuesto como monto fijo (ej: $500 tasa municipal)")
        
        tipo_opcion = input("Seleccionar tipo (1 o 2): ").strip()
        
        if tipo_opcion == "1":
            tipo = "porcentaje"
            valor_input = input("Valor del porcentaje (0-100): ").strip()
            try:
                valor = float(valor_input)
                if valor < 0 or valor > 100:
                    print("❌ El porcentaje debe estar entre 0 y 100")
                    return
            except ValueError:
                print("❌ Valor de porcentaje inválido")
                return
        elif tipo_opcion == "2":
            tipo = "fijo"
            valor_input = input("Monto fijo: $").strip()
            try:
                valor = float(valor_input)
                if valor < 0:
                    print("❌ El monto fijo no puede ser negativo")
                    return
            except ValueError:
                print("❌ Monto inválido")
                return
        else:
            print("❌ Opción inválida")
            return
        
        print(f"\n📋 Resumen:")
        print(f"   • Nombre: {nombre}")
        print(f"   • Tipo: {tipo}")
        if tipo == "porcentaje":
            print(f"   • Valor: {valor:.1f}%")
        else:
            print(f"   • Valor: ${valor:,.2f}")
        
        confirmar = input(f"\n¿Crear este impuesto? (s/N): ").lower()
        if confirmar != 's':
            print("Operación cancelada.")
            return
        
        resultado = controller.crear_impuesto_controller(
            nombre=nombre,
            tipo=tipo,
            valor=valor
        )
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\n✅ Impuesto creado exitosamente!")
            print(f"   ID: {data['id']}")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Tipo: {data['tipo']}")
            if data['tipo'] == 'porcentaje':
                print(f"   Valor: {data['valor']:.1f}%")
            else:
                print(f"   Valor: ${data['valor']:,.2f}")
        else:
            print(f"❌ Error: {resultado['message']}")
            
    except ValueError:
        print("❌ Entrada inválida. Operación cancelada.")

def actualizar_costo_operativo():
    """Actualiza un costo operativo existente"""
    print("\n=== ACTUALIZAR COSTO OPERATIVO ===")
    
    # Mostrar costos disponibles
    mostrar_costos_operativos()
    
    try:
        costo_id = int(input("\nID del costo a actualizar: ").strip())
        
        print("Dejá en blanco los campos que no quieras cambiar:")
        
        nombre = input("Nuevo nombre: ").strip()
        nombre = nombre if nombre else None
        
        monto_input = input("Nuevo monto: $").strip()
        monto = float(monto_input) if monto_input else None
        
        fecha_input = input("Nueva fecha inicio (YYYY-MM-DD): ").strip()
        fecha_inicio = fecha_input if fecha_input else None
        
        recurrente_input = input("¿Es recurrente? (s/n/Enter para no cambiar): ").lower().strip()
        if recurrente_input in ['s', 'si']:
            recurrente = True
        elif recurrente_input in ['n', 'no']:
            recurrente = False
        else:
            recurrente = None
        
        activo_input = input("¿Está activo? (s/n/Enter para no cambiar): ").lower().strip()
        if activo_input in ['s', 'si']:
            activo = True
        elif activo_input in ['n', 'no']:
            activo = False
        else:
            activo = None
        
        # Verificar que al menos un campo se va a cambiar
        if all(x is None for x in [nombre, monto, fecha_inicio, recurrente, activo]):
            print("⚠️  No se especificaron cambios.")
            return
        
        resultado = controller.actualizar_costo_operativo_controller(
            costo_id=costo_id,
            nombre=nombre,
            monto=monto,
            fecha_inicio=fecha_inicio,
            recurrente=recurrente,
            activo=activo
        )
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\n✅ Costo operativo actualizado!")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Monto: ${data['monto']:,.2f}")
            print(f"   Recurrente: {'Sí' if data['recurrente'] else 'No'}")
            print(f"   Estado: {'Activo' if data['activo'] else 'Inactivo'}")
        else:
            print(f"❌ Error: {resultado['message']}")
            
    except ValueError:
        print("❌ ID inválido. Operación cancelada.")

def actualizar_impuesto():
    """Actualiza un impuesto existente"""
    print("\n=== ACTUALIZAR IMPUESTO ===")
    
    # Mostrar impuestos disponibles
    mostrar_impuestos()
    
    try:
        impuesto_id = int(input("\nID del impuesto a actualizar: ").strip())
        
        print("Dejá en blanco los campos que no quieras cambiar:")
        
        nombre = input("Nuevo nombre: ").strip()
        nombre = nombre if nombre else None
        
        tipo_input = input("Nuevo tipo (porcentaje/fijo): ").strip()
        tipo = tipo_input if tipo_input in ['porcentaje', 'fijo'] else None
        
        valor_input = input("Nuevo valor: ").strip()
        valor = float(valor_input) if valor_input else None
        
        activo_input = input("¿Está activo? (s/n/Enter para no cambiar): ").lower().strip()
        if activo_input in ['s', 'si']:
            activo = True
        elif activo_input in ['n', 'no']:
            activo = False
        else:
            activo = None
        
        # Verificar que al menos un campo se va a cambiar
        if all(x is None for x in [nombre, tipo, valor, activo]):
            print("⚠️  No se especificaron cambios.")
            return
        
        resultado = controller.actualizar_impuesto_controller(
            impuesto_id=impuesto_id,
            nombre=nombre,
            tipo=tipo,
            valor=valor,
            activo=activo
        )
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\n✅ Impuesto actualizado!")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Tipo: {data['tipo']}")
            if data['tipo'] == 'porcentaje':
                print(f"   Valor: {data['valor']:.1f}%")
            else:
                print(f"   Valor: ${data['valor']:,.2f}")
            print(f"   Estado: {'Activo' if data['activo'] else 'Inactivo'}")
        else:
            print(f"❌ Error: {resultado['message']}")
            
    except ValueError:
        print("❌ ID inválido. Operación cancelada.")

def eliminar_costo_operativo():
    """Desactiva un costo operativo"""
    print("\n=== ELIMINAR COSTO OPERATIVO ===")
    
    # Mostrar costos disponibles
    mostrar_costos_operativos()
    
    try:
        costo_id = int(input("\nID del costo a eliminar: ").strip())
        
        confirmar = input("¿Confirmar eliminación? (escribí 'ELIMINAR'): ")
        
        if confirmar != 'ELIMINAR':
            print("Operación cancelada.")
            return
        
        resultado = controller.eliminar_costo_operativo_controller(costo_id)
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\n✅ Costo operativo desactivado!")
            print(f"   ID: {data['id']}")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Monto: ${data['monto']:,.2f}")
        else:
            print(f"❌ Error: {resultado['message']}")
            
    except ValueError:
        print("❌ ID inválido. Operación cancelada.")

def eliminar_impuesto():
    """Desactiva un impuesto"""
    print("\n=== ELIMINAR IMPUESTO ===")
    
    # Mostrar impuestos disponibles
    mostrar_impuestos()
    
    try:
        impuesto_id = int(input("\nID del impuesto a eliminar: ").strip())
        
        confirmar = input("¿Confirmar eliminación? (escribí 'ELIMINAR'): ")
        
        if confirmar != 'ELIMINAR':
            print("Operación cancelada.")
            return
        
        resultado = controller.eliminar_impuesto_controller(impuesto_id)
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\n✅ Impuesto desactivado!")
            print(f"   ID: {data['id']}")
            print(f"   Nombre: {data['nombre']}")
            print(f"   Tipo: {data['tipo']}")
            if data['tipo'] == 'porcentaje':
                print(f"   Valor: {data['valor']:.1f}%")
            else:
                print(f"   Valor: ${data['valor']:,.2f}")
        else:
            print(f"❌ Error: {resultado['message']}")
            
    except ValueError:
        print("❌ ID inválido. Operación cancelada.")

def gestion_costos_operativos():
    """Submenú para gestión de costos operativos"""
    while True:
        print("\n=== GESTIÓN COSTOS OPERATIVOS ===")
        print("1. Ver costos operativos")
        print("2. Crear nuevo costo")
        print("3. Actualizar costo existente")
        print("4. Eliminar costo")
        print("5. Volver al menú principal")
        
        opcion = input("Elegí una opción: ")
        
        if opcion == "1":
            mostrar_costos_operativos()
        elif opcion == "2":
            crear_costo_operativo()
        elif opcion == "3":
            actualizar_costo_operativo()
        elif opcion == "4":
            eliminar_costo_operativo()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")

def gestion_impuestos():
    """Submenú para gestión de impuestos"""
    while True:
        print("\n=== GESTIÓN IMPUESTOS ===")
        print("1. Ver impuestos")
        print("2. Crear nuevo impuesto")
        print("3. Actualizar impuesto existente")
        print("4. Eliminar impuesto")
        print("5. Volver al menú principal")
        
        opcion = input("Elegí una opción: ")
        
        if opcion == "1":
            mostrar_impuestos()
        elif opcion == "2":
            crear_impuesto()
        elif opcion == "3":
            actualizar_impuesto()
        elif opcion == "4":
            eliminar_impuesto()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")

def mostrar_registros_eliminados():
    """Muestra información sobre los registros marcados como eliminados"""
    print("\n=== REGISTROS MARCADOS COMO ELIMINADOS ===")
    
    resultado = controller.contar_registros_eliminados_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        total = data["total"]
        costos_count = data["costos_eliminados"]
        impuestos_count = data["impuestos_eliminados"]
        
        print(f"📊 {resultado['message']}")
        
        if total == 0:
            print("✅ No hay registros eliminados para limpiar")
            return
        
        print(f"\n📋 Distribución:")
        print(f"   • Costos operativos eliminados: {costos_count}")
        print(f"   • Impuestos eliminados: {impuestos_count}")
        print(f"   • TOTAL: {total}")
        
        # Mostrar ejemplos de costos operativos
        if data["ejemplos_costos"]:
            print(f"\n💼 Ejemplos de costos operativos eliminados:")
            print("-" * 60)
            print(f"{'Nombre':<25} {'Monto':<12} {'Recurrente':<12}")
            print("-" * 60)
            
            for ejemplo in data["ejemplos_costos"]:
                recurrente = "Sí" if ejemplo['recurrente'] else "No"
                print(f"{ejemplo['nombre']:<25} ${ejemplo['monto']:<11,.0f} {recurrente:<12}")
            
            if costos_count > len(data["ejemplos_costos"]):
                print(f"... y {costos_count - len(data['ejemplos_costos'])} más")
        
        # Mostrar ejemplos de impuestos
        if data["ejemplos_impuestos"]:
            print(f"\n💰 Ejemplos de impuestos eliminados:")
            print("-" * 50)
            print(f"{'Nombre':<20} {'Tipo':<12} {'Valor':<12}")
            print("-" * 50)
            
            for ejemplo in data["ejemplos_impuestos"]:
                if ejemplo['tipo'] == 'porcentaje':
                    valor_display = f"{ejemplo['valor']:.1f}%"
                else:
                    valor_display = f"${ejemplo['valor']:,.2f}"
                
                print(f"{ejemplo['nombre']:<20} {ejemplo['tipo']:<12} {valor_display:<12}")
            
            if impuestos_count > len(data["ejemplos_impuestos"]):
                print(f"... y {impuestos_count - len(data['ejemplos_impuestos'])} más")
        
        print(f"\n⚠️  Estos {total} registros pueden ser eliminados permanentemente")
    else:
        print(f"❌ {resultado['message']}")

def limpiar_costos_operativos_eliminados():
    """Ejecuta la limpieza permanente de costos operativos eliminados"""
    print("\n=== LIMPIEZA COSTOS OPERATIVOS ELIMINADOS ===")
    
    # Verificar qué se va a eliminar
    contador = controller.contar_registros_eliminados_controller()
    
    if not contador["success"]:
        print(f"❌ Error al verificar registros: {contador['message']}")
        return
    
    costos_count = contador["data"]["costos_eliminados"]
    
    if costos_count == 0:
        print("✅ No hay costos operativos eliminados para limpiar")
        return
    
    print(f"⚠️  Se encontraron {costos_count} costos operativos marcados como eliminados")
    
    # Mostrar algunos ejemplos
    ejemplos = contador["data"]["ejemplos_costos"]
    if ejemplos:
        print(f"\n📋 Algunos costos que serán eliminados:")
        for ejemplo in ejemplos:
            print(f"   • {ejemplo['nombre']}: ${ejemplo['monto']:,.2f} ({'Recurrente' if ejemplo['recurrente'] else 'Una vez'})")
    
    print(f"\n🚨 ADVERTENCIA:")
    print(f"   • Esta operación eliminará PERMANENTEMENTE {costos_count} costos operativos")
    print(f"   • Los datos NO se podrán recuperar")
    print(f"   • Solo se eliminarán registros con activo=False")
    
    # Confirmación doble
    confirmar1 = input(f"\n¿Continuar con la eliminación? (escribí 'CONFIRMAR'): ")
    
    if confirmar1 != 'CONFIRMAR':
        print("Operación cancelada.")
        return
    
    confirmar2 = input(f"¿Estás SEGURO de eliminar {costos_count} costos? (escribí 'ELIMINAR PERMANENTE'): ")
    
    if confirmar2 != 'ELIMINAR PERMANENTE':
        print("Operación cancelada.")
        return
    
    print(f"\n🔄 Eliminando costos operativos...")
    
    # Ejecutar la limpieza
    resultado = controller.limpiar_costos_operativos_eliminados_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\n✅ {resultado['message']}")
        print(f"📊 Costos operativos eliminados: {data['registros_eliminados']}")
        
        if data['detalles']:
            print(f"   • Nombres eliminados:")
            for detalle in data['detalles'][:5]:  # Mostrar máximo 5
                print(f"     - {detalle['nombre']}: ${detalle['monto']:,.2f}")
            
            if len(data['detalles']) > 5:
                print(f"     ... y {len(data['detalles']) - 5} más")
        
        print(f"\n🎉 Limpieza de costos operativos completada!")
    else:
        print(f"❌ Error en la limpieza: {resultado['message']}")

def limpiar_impuestos_eliminados():
    """Ejecuta la limpieza permanente de impuestos eliminados"""
    print("\n=== LIMPIEZA IMPUESTOS ELIMINADOS ===")
    
    # Verificar qué se va a eliminar
    contador = controller.contar_registros_eliminados_controller()
    
    if not contador["success"]:
        print(f"❌ Error al verificar registros: {contador['message']}")
        return
    
    impuestos_count = contador["data"]["impuestos_eliminados"]
    
    if impuestos_count == 0:
        print("✅ No hay impuestos eliminados para limpiar")
        return
    
    print(f"⚠️  Se encontraron {impuestos_count} impuestos marcados como eliminados")
    
    # Mostrar algunos ejemplos
    ejemplos = contador["data"]["ejemplos_impuestos"]
    if ejemplos:
        print(f"\n📋 Algunos impuestos que serán eliminados:")
        for ejemplo in ejemplos:
            if ejemplo['tipo'] == 'porcentaje':
                valor_display = f"{ejemplo['valor']:.1f}%"
            else:
                valor_display = f"${ejemplo['valor']:,.2f}"
            print(f"   • {ejemplo['nombre']} ({ejemplo['tipo']}): {valor_display}")
    
    print(f"\n🚨 ADVERTENCIA:")
    print(f"   • Esta operación eliminará PERMANENTEMENTE {impuestos_count} impuestos")
    print(f"   • Los datos NO se podrán recuperar")
    print(f"   • Solo se eliminarán registros con activo=False")
    
    # Confirmación doble
    confirmar1 = input(f"\n¿Continuar con la eliminación? (escribí 'CONFIRMAR'): ")
    
    if confirmar1 != 'CONFIRMAR':
        print("Operación cancelada.")
        return
    
    confirmar2 = input(f"¿Estás SEGURO de eliminar {impuestos_count} impuestos? (escribí 'ELIMINAR PERMANENTE'): ")
    
    if confirmar2 != 'ELIMINAR PERMANENTE':
        print("Operación cancelada.")
        return
    
    print(f"\n🔄 Eliminando impuestos...")
    
    # Ejecutar la limpieza
    resultado = controller.limpiar_impuestos_eliminados_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\n✅ {resultado['message']}")
        print(f"📊 Impuestos eliminados: {data['registros_eliminados']}")
        
        if data['detalles']:
            print(f"   • Nombres eliminados:")
            for detalle in data['detalles'][:5]:  # Mostrar máximo 5
                if detalle['tipo'] == 'porcentaje':
                    valor_display = f"{detalle['valor']:.1f}%"
                else:
                    valor_display = f"${detalle['valor']:,.2f}"
                print(f"     - {detalle['nombre']}: {valor_display}")
            
            if len(data['detalles']) > 5:
                print(f"     ... y {len(data['detalles']) - 5} más")
        
        print(f"\n🎉 Limpieza de impuestos completada!")
    else:
        print(f"❌ Error en la limpieza: {resultado['message']}")

def limpiar_todos_los_eliminados():
    """Ejecuta la limpieza permanente de TODOS los registros eliminados"""
    print("\n=== LIMPIEZA COMPLETA DE REGISTROS ELIMINADOS ===")
    
    # Verificar qué se va a eliminar
    contador = controller.contar_registros_eliminados_controller()
    
    if not contador["success"]:
        print(f"❌ Error al verificar registros: {contador['message']}")
        return
    
    data = contador["data"]
    total = data["total"]
    costos_count = data["costos_eliminados"]
    impuestos_count = data["impuestos_eliminados"]
    
    if total == 0:
        print("✅ No hay registros eliminados para limpiar")
        return
    
    print(f"⚠️  Se encontraron {total} registros marcados como eliminados:")
    print(f"   • Costos operativos: {costos_count}")
    print(f"   • Impuestos: {impuestos_count}")
    
    print(f"\n🚨 ADVERTENCIA CRÍTICA:")
    print(f"   • Esta operación eliminará PERMANENTEMENTE TODOS los registros eliminados")
    print(f"   • Se eliminarán {total} registros de ambas tablas")
    print(f"   • Los datos NO se podrán recuperar JAMÁS")
    print(f"   • Solo se eliminarán registros con activo=False")
    
    # Confirmación triple para operación crítica
    confirmar1 = input(f"\n¿Continuar con la eliminación COMPLETA? (escribí 'CONFIRMAR'): ")
    
    if confirmar1 != 'CONFIRMAR':
        print("Operación cancelada.")
        return
    
    confirmar2 = input(f"¿Estás SEGURO de eliminar {total} registros? (escribí 'ELIMINAR TODO'): ")
    
    if confirmar2 != 'ELIMINAR TODO':
        print("Operación cancelada.")
        return
    
    confirmar3 = input(f"ÚLTIMA CONFIRMACIÓN - ¿Eliminar {total} registros PERMANENTEMENTE? (escribí 'SÍ, ELIMINAR TODO'): ")
    
    if confirmar3 != 'SÍ, ELIMINAR TODO':
        print("Operación cancelada.")
        return
    
    print(f"\n🔄 Eliminando TODOS los registros marcados como eliminados...")
    
    # Ejecutar la limpieza completa
    resultado = controller.limpiar_todos_los_eliminados_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\n✅ {resultado['message']}")
        print(f"📊 Resumen de la limpieza:")
        print(f"   • Costos operativos eliminados: {data['costos_eliminados']}")
        print(f"   • Impuestos eliminados: {data['impuestos_eliminados']}")
        print(f"   • TOTAL ELIMINADO: {data['total_eliminados']}")
        
        print(f"\n🎉 ¡Limpieza completa terminada exitosamente!")
        print(f"🗄️  Base de datos optimizada - {data['total_eliminados']} registros liberados")
    else:
        print(f"❌ Error en la limpieza: {resultado['message']}")

def menu_limpieza():
    """Submenú para operaciones de limpieza"""
    while True:
        print("\n=== LIMPIEZA DE REGISTROS ELIMINADOS ===")
        print("1. Ver registros eliminados")
        print("2. Limpiar solo costos operativos")
        print("3. Limpiar solo impuestos")
        print("4. Limpiar TODOS los registros eliminados")
        print("5. Volver al menú principal")
        
        opcion = input("Elegí una opción: ")
        
        if opcion == "1":
            mostrar_registros_eliminados()
        elif opcion == "2":
            limpiar_costos_operativos_eliminados()
        elif opcion == "3":
            limpiar_impuestos_eliminados()
        elif opcion == "4":
            limpiar_todos_los_eliminados()
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")

def menu_costos():
    """Menú principal del sistema de costos"""
    while True:
        print("\n" + "="*60)
        print("💰 SISTEMA DE GESTIÓN DE COSTOS E IMPUESTOS")
        print("="*60)
        print("1. Ver resumen general")
        print("2. Ver costos operativos")
        print("3. Ver impuestos")
        print("4. Gestionar costos operativos")
        print("5. Gestionar impuestos")
        print("6. Crear costo operativo rápido")
        print("7. Crear impuesto rápido")
        print("8. Limpieza de registros eliminados")
        print("9. Salir")
        print("="*60)

        opcion = input("Elegí una opción: ")

        if opcion == "1":
            mostrar_resumen_general()

        elif opcion == "2":
            mostrar_costos_operativos()

        elif opcion == "3":
            mostrar_impuestos()

        elif opcion == "4":
            gestion_costos_operativos()

        elif opcion == "5":
            gestion_impuestos()

        elif opcion == "6":
            crear_costo_operativo()

        elif opcion == "7":
            crear_impuesto()

        elif opcion == "8":
            menu_limpieza()

        elif opcion == "9":
            print("👋 Saliendo del sistema de costos.")
            break

        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu_costos()

# Ejecutar con: python -m aplicacion.backend.costos.test_costos