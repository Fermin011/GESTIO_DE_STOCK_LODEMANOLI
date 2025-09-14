from aplicacion.backend.caja import controller
from datetime import date, datetime, timedelta

def mostrar_caja_hoy():
    resultado = controller.consultar_caja_hoy_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        print("\n=== CIERRE DE CAJA HOY ===")
        print("-" * 60)
        print(f"Fecha: {data['fecha']}")
        print(f"Hora cierre: {data['hora_cierre']}")
        print(f"Efectivo: ${data['monto_efectivo']:,.2f}")
        print(f"Transferencia: ${data['monto_transferencia']:,.2f}")
        print(f"TOTAL: ${data['monto_total']:,.2f}")
        print(f"Usuario: {data['usuario_nombre'] or 'Sin asignar'}")
        if data['observaciones']:
            print(f"Observaciones: {data['observaciones']}")
        print("-" * 60)
    else:
        print(f"{resultado['message']}")

def mostrar_cierres_semana():
    resultado = controller.listar_cierres_semana_controller()
    
    if resultado["success"]:
        cierres = resultado["data"]["cierres"]
        resumen = resultado["data"]["resumen"]
        
        print("\n=== CIERRES DE LA SEMANA ===")
        print("-" * 80)
        print(f"{'Fecha':<12} {'Efectivo':<12} {'Transfer.':<12} {'Total':<12} {'Usuario':<15}")
        print("-" * 80)
        
        for cierre in cierres:
            usuario = cierre['usuario_nombre'] or 'Sin usuario'
            print(f"{cierre['fecha']:<12} ${cierre['monto_efectivo']:<11,.0f} ${cierre['monto_transferencia']:<11,.0f} ${cierre['monto_total']:<11,.0f} {usuario:<15}")
        
        print("-" * 80)
        print(f"RESUMEN:")
        print(f"   Dias trabajados: {resumen['cantidad_cierres']}")
        print(f"   Total efectivo: ${resumen['total_efectivo']:,.2f}")
        print(f"   Total transferencias: ${resumen['total_transferencia']:,.2f}")
        print(f"   TOTAL GENERAL: ${resumen['total_general']:,.2f}")
        print(f"   Promedio diario: ${resumen['promedio_diario']:,.2f}")
        print("-" * 80)
    else:
        print(f"{resultado['message']}")

def mostrar_cierres_mes():
    resultado = controller.listar_cierres_mes_actual_controller()
    
    if resultado["success"]:
        cierres = resultado["data"]["cierres"]
        resumen = resultado["data"]["resumen"]
        
        print("\n=== CIERRES DEL MES ACTUAL ===")
        print(f"Total de dias: {resumen['cantidad_cierres']}")
        print(f"Total del mes: ${resumen['total_general']:,.2f}")
        print(f"Promedio diario: ${resumen['promedio_diario']:,.2f}")
        
        if len(cierres) <= 10:
            print(f"\nTodos los cierres:")
            print("-" * 50)
            for cierre in cierres:
                print(f"  {cierre['fecha']}: ${cierre['monto_total']:,.2f}")
        else:
            print(f"\nUltimos 10 cierres:")
            print("-" * 50)
            for cierre in cierres[:10]:
                print(f"  {cierre['fecha']}: ${cierre['monto_total']:,.2f}")
            print(f"  ... y {len(cierres) - 10} mas")
        print("-" * 50)
    else:
        print(f"{resultado['message']}")

def registrar_caja_hoy():
    print("\n=== REGISTRAR CAJA DE HOY ===")
    
    validacion = controller.validar_puede_registrar_caja_controller()
    
    if not validacion["puede_registrar"]:
        print(f"{validacion['message']}")
        if validacion.get("cierre_existente"):
            data = validacion["cierre_existente"]
            print(f"   Total registrado: ${data['monto_total']:,.2f}")
        return
    
    try:
        print("Ingresa los montos (deja vacio para $0):")
        
        efectivo_input = input("Monto en efectivo: $").strip()
        efectivo = float(efectivo_input) if efectivo_input else None
        
        transferencia_input = input("Monto por transferencia: $").strip()
        transferencia = float(transferencia_input) if transferencia_input else None
        
        usuario_id = int(input("ID de usuario: ").strip())
        observaciones = input("Observaciones (opcional): ").strip()
        
        resultado = controller.registrar_caja_hoy_controller(
            monto_efectivo=efectivo,
            monto_transferencia=transferencia,
            usuario_id=usuario_id,
            observaciones=observaciones
        )
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\nCaja registrada exitosamente!")
            print(f"   Fecha: {data['fecha']}")
            print(f"   Efectivo: ${data['monto_efectivo']:,.2f}")
            print(f"   Transferencia: ${data['monto_transferencia']:,.2f}")
            print(f"   Total: ${data['monto_total']:,.2f}")
            
            if data['monto_total'] == 0:
                print("   Se registro una caja con total $0")
        else:
            print(f"Error: {resultado['message']}")
            
    except ValueError:
        print("Entrada invalida. Operacion cancelada.")

def registrar_caja_fecha_especifica():
    print("\n=== REGISTRAR CAJA FECHA ESPECIFICA ===")
    
    try:
        fecha = input("Fecha (YYYY-MM-DD): ").strip()
        
        validacion = controller.validar_puede_registrar_caja_controller(fecha)
        
        if not validacion["puede_registrar"]:
            print(f"{validacion['message']}")
            return
        
        print("Ingresa los montos (deja vacio para $0):")
        
        efectivo_input = input("Monto en efectivo: $").strip()
        efectivo = float(efectivo_input) if efectivo_input else None
        
        transferencia_input = input("Monto por transferencia: $").strip()
        transferencia = float(transferencia_input) if transferencia_input else None
        
        usuario_id = int(input("ID de usuario: ").strip())
        observaciones = input("Observaciones (opcional): ").strip()
        
        resultado = controller.registrar_caja_diaria_controller(
            fecha=fecha,
            monto_efectivo=efectivo,
            monto_transferencia=transferencia,
            usuario_id=usuario_id,
            observaciones=observaciones
        )
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\nCaja registrada para {fecha}!")
            print(f"   Total: ${data['monto_total']:,.2f}")
            
            if data['monto_total'] == 0:
                print("   Se registro una caja con total $0")
        else:
            print(f"Error: {resultado['message']}")
            
    except ValueError:
        print("Entrada invalida. Operacion cancelada.")

def consultar_caja_fecha():
    print("\n=== CONSULTAR CAJA POR FECHA ===")
    
    fecha = input("Fecha a consultar (YYYY-MM-DD): ").strip()
    resultado = controller.consultar_caja_por_fecha_controller(fecha)
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\nCierre encontrado para {fecha}:")
        print("-" * 50)
        print(f"Efectivo: ${data['monto_efectivo']:,.2f}")
        print(f"Transferencia: ${data['monto_transferencia']:,.2f}")
        print(f"TOTAL: ${data['monto_total']:,.2f}")
        print(f"Hora cierre: {data['hora_cierre']}")
        print(f"Usuario: {data['usuario_nombre'] or 'Sin asignar'}")
        if data['observaciones']:
            print(f"Observaciones: {data['observaciones']}")
        print("-" * 50)
    else:
        print(f"{resultado['message']}")

def consultar_rango_fechas():
    print("\n=== CONSULTAR RANGO DE FECHAS ===")
    
    try:
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()
        
        resultado = controller.listar_cierres_rango_controller(fecha_inicio, fecha_fin)
        
        if resultado["success"]:
            cierres = resultado["data"]["cierres"]
            resumen = resultado["data"]["resumen"]
            
            print(f"\n{resultado['message']}")
            print("-" * 70)
            print(f"{'Fecha':<12} {'Total':<12} {'Usuario':<20} {'Observaciones':<20}")
            print("-" * 70)
            
            for cierre in cierres:
                obs = (cierre['observaciones'] or '')[:18] + '...' if len(cierre['observaciones'] or '') > 18 else (cierre['observaciones'] or '')
                usuario = (cierre['usuario_nombre'] or 'Sin usuario')[:18]
                print(f"{cierre['fecha']:<12} ${cierre['monto_total']:<11,.0f} {usuario:<20} {obs:<20}")
            
            print("-" * 70)
            print(f"TOTAL PERIODO: ${resumen['total_general']:,.2f}")
            print(f"PROMEDIO DIARIO: ${resumen['promedio_diario']:,.2f}")
            print("-" * 70)
        else:
            print(f"{resultado['message']}")
            
    except Exception as e:
        print(f"Error: {e}")

def actualizar_caja():
    print("\n=== ACTUALIZAR CAJA ===")
    
    try:
        mostrar_caja_hoy()
        
        opcion = input("\nActualizar caja de hoy? (s) o ingresar fecha especifica (f): ").lower()
        
        if opcion == 's':
            consulta = controller.consultar_caja_hoy_controller()
            if not consulta["success"]:
                print("No hay caja registrada para hoy")
                return
            cierre_id = consulta["data"]["id"]
        elif opcion == 'f':
            fecha = input("Fecha (YYYY-MM-DD): ").strip()
            consulta = controller.consultar_caja_por_fecha_controller(fecha)
            if not consulta["success"]:
                print(f"No se encontro caja para {fecha}")
                return
            cierre_id = consulta["data"]["id"]
        else:
            print("Operacion cancelada.")
            return
        
        print(f"\nActualizando caja ID: {cierre_id}")
        print("Deja en blanco los campos que no quieras cambiar:")
        print("Para poner $0, escribi '0' (cero)")
        
        efectivo_input = input("Nuevo monto efectivo: $").strip()
        transferencia_input = input("Nuevo monto transferencia: $").strip()
        observaciones = input("Nuevas observaciones: ").strip()
        
        kwargs = {"cierre_id": cierre_id}
        
        if efectivo_input:
            kwargs["monto_efectivo"] = float(efectivo_input)
        
        if transferencia_input:
            kwargs["monto_transferencia"] = float(transferencia_input)
        
        if observaciones:
            kwargs["observaciones"] = observaciones
        
        if len(kwargs) == 1:
            print("No se especificaron cambios.")
            return
        
        resultado = controller.actualizar_caja_controller(**kwargs)
        
        if resultado["success"]:
            data = resultado["data"]
            print(f"\nCaja actualizada exitosamente!")
            print(f"   Nuevo total: ${data['monto_total']:,.2f}")
        else:
            print(f"Error: {resultado['message']}")
            
    except ValueError:
        print("Entrada invalida. Operacion cancelada.")

def eliminar_caja():
    print("\n=== ELIMINAR REGISTRO DE CAJA ===")
    
    try:
        fecha = input("Fecha del registro a eliminar (YYYY-MM-DD): ").strip()
        
        consulta = controller.consultar_caja_por_fecha_controller(fecha)
        
        if not consulta["success"]:
            print(f"{consulta['message']}")
            return
        
        data = consulta["data"]
        print(f"\nRegistro encontrado:")
        print(f"   Total: ${data['monto_total']:,.2f}")
        print(f"   Usuario: {data['usuario_nombre'] or 'Sin asignar'}")
        
        confirmar = input(f"\nELIMINAR este registro? (escribi 'ELIMINAR' para confirmar): ")
        
        if confirmar != 'ELIMINAR':
            print("Operacion cancelada.")
            return
        
        motivo = input("Motivo de eliminacion: ").strip()
        
        resultado = controller.eliminar_registro_caja_controller(
            cierre_id=data["id"],
            motivo=motivo
        )
        
        if resultado["success"]:
            print(f"\nRegistro eliminado exitosamente!")
            print(f"   Fecha: {resultado['data']['fecha']}")
            print(f"   Monto: ${resultado['data']['monto_total']:,.2f}")
        else:
            print(f"Error: {resultado['message']}")
            
    except Exception as e:
        print(f"Error: {e}")

def mostrar_registros_eliminados():
    print("\n=== REGISTROS MARCADOS COMO ELIMINADOS ===")
    
    resultado = controller.contar_registros_eliminados_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        cantidad = data["cantidad"]
        
        print(f"{resultado['message']}")
        
        if cantidad == 0:
            print("No hay registros eliminados para limpiar")
            return
        
        print(f"\nAlgunos ejemplos:")
        print("-" * 60)
        print(f"{'Fecha':<12} {'Total':<12} {'Observaciones':<30}")
        print("-" * 60)
        
        for ejemplo in data["ejemplos"]:
            obs = ejemplo['observaciones'][:28] + "..." if len(ejemplo['observaciones']) > 28 else ejemplo['observaciones']
            print(f"{ejemplo['fecha']:<12} ${ejemplo['monto_total']:<11,.0f} {obs:<30}")
        
        print("-" * 60)
        
        if cantidad > len(data["ejemplos"]):
            print(f"... y {cantidad - len(data['ejemplos'])} registros mas")
        
        print(f"\nEstos {cantidad} registros pueden ser eliminados permanentemente")
    else:
        print(f"{resultado['message']}")

def limpiar_registros_eliminados():
    print("\n=== LIMPIEZA PERMANENTE DE REGISTROS ===")
    
    print("Verificando registros a eliminar...")
    contador = controller.contar_registros_eliminados_controller()
    
    if not contador["success"]:
        print(f"Error al verificar registros: {contador['message']}")
        return
    
    cantidad = contador["data"]["cantidad"]
    
    if cantidad == 0:
        print("No hay registros eliminados para limpiar")
        return
    
    print(f"Se encontraron {cantidad} registros marcados como eliminados")
    
    ejemplos = contador["data"]["ejemplos"]
    if ejemplos:
        print(f"\nAlgunos registros que seran eliminados:")
        for ejemplo in ejemplos[:3]:
            print(f"   {ejemplo['fecha']}: ${ejemplo['monto_total']:,.2f}")
        if cantidad > 3:
            print(f"   ... y {cantidad - 3} mas")
    
    print(f"\nADVERTENCIA:")
    print(f"   Esta operacion eliminara PERMANENTEMENTE {cantidad} registros")
    print(f"   Los datos NO se podran recuperar")
    print(f"   Solo se eliminaran registros con estado=False")
    
    confirmar1 = input(f"\nContinuar con la eliminacion? (escribi 'CONFIRMAR'): ")
    
    if confirmar1 != 'CONFIRMAR':
        print("Operacion cancelada.")
        return
    
    confirmar2 = input(f"Estas SEGURO de eliminar {cantidad} registros? (escribi 'ELIMINAR PERMANENTE'): ")
    
    if confirmar2 != 'ELIMINAR PERMANENTE':
        print("Operacion cancelada.")
        return
    
    print(f"\nEliminando registros...")
    
    resultado = controller.limpiar_registros_eliminados_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\n{resultado['message']}")
        print(f"Detalles de la operacion:")
        print(f"   Registros eliminados: {data['registros_eliminados']}")
        
        if data['detalles']:
            print(f"   Fechas eliminadas:")
            for detalle in data['detalles'][:5]:
                print(f"     - {detalle['fecha']}: ${detalle['monto_total']:,.2f}")
            
            if len(data['detalles']) > 5:
                print(f"     ... y {len(data['detalles']) - 5} mas")
        
        print(f"\nLimpieza completada exitosamente!")
    else:
        print(f"Error en la limpieza: {resultado['message']}")

def consultas_avanzadas():
    while True:
        print("\n=== CONSULTAS AVANZADAS ===")
        print("1. Ver cierres del mes especifico")
        print("2. Ver estadisticas de periodo")
        print("3. Buscar por rango de montos")
        print("4. Ver registros eliminados")
        print("5. Limpiar registros eliminados (PERMANENTE)")
        print("6. Volver al menu principal")
        
        opcion = input("Elegi una opcion: ")
        
        if opcion == "1":
            try:
                year = int(input("Año (ej: 2024): "))
                month = int(input("Mes (1-12): "))
                
                resultado = controller.listar_cierres_mes_controller(year, month)
                
                if resultado["success"]:
                    cierres = resultado["data"]["cierres"]
                    resumen = resultado["data"]["resumen"]
                    
                    print(f"\nCIERRES DE {month:02d}/{year}")
                    print(f"Dias trabajados: {resumen['cantidad_cierres']}")
                    print(f"Total del mes: ${resumen['total_general']:,.2f}")
                    
                    for cierre in cierres[:15]:
                        print(f"  {cierre['fecha']}: ${cierre['monto_total']:,.2f}")
                    
                    if len(cierres) > 15:
                        print(f"  ... y {len(cierres) - 15} mas")
                else:
                    print(f"{resultado['message']}")
                    
            except ValueError:
                print("Entrada invalida.")
        
        elif opcion == "2":
            consultar_rango_fechas()
        
        elif opcion == "3":
            print("Funcion de busqueda por montos - Por implementar")
        
        elif opcion == "4":
            mostrar_registros_eliminados()
        
        elif opcion == "5":
            limpiar_registros_eliminados()
        
        elif opcion == "6":
            break
        else:
            print("Opcion invalida.")

def menu_caja():
    while True:
        print("\n" + "="*50)
        print("SISTEMA DE GESTION DE CAJA")
        print("="*50)
        print("1. Ver caja de hoy")
        print("2. Registrar caja de hoy")
        print("3. Registrar caja fecha especifica")
        print("4. Consultar caja por fecha")
        print("5. Ver cierres de la semana")
        print("6. Ver cierres del mes")
        print("7. Consultar rango de fechas")
        print("8. Actualizar caja existente")
        print("9. Eliminar registro de caja")
        print("10. Consultas avanzadas")
        print("11. Salir")
        print("="*50)

        opcion = input("Elegi una opcion: ")

        if opcion == "1":
            mostrar_caja_hoy()

        elif opcion == "2":
            registrar_caja_hoy()

        elif opcion == "3":
            registrar_caja_fecha_especifica()

        elif opcion == "4":
            consultar_caja_fecha()

        elif opcion == "5":
            mostrar_cierres_semana()

        elif opcion == "6":
            mostrar_cierres_mes()

        elif opcion == "7":
            consultar_rango_fechas()

        elif opcion == "8":
            actualizar_caja()

        elif opcion == "9":
            eliminar_caja()

        elif opcion == "10":
            consultas_avanzadas()

        elif opcion == "11":
            print("Saliendo del sistema de caja.")
            break

        else:
            print("Opcion invalida.")

if __name__ == "__main__":
    menu_caja()