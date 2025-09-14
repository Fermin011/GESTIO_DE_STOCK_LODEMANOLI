from aplicacion.backend.metricas.ganancias import controller
from datetime import date, datetime, timedelta

def mostrar_calculo_ganancia_simple_hoy():
    """Muestra el cálculo simple de ganancia neta para hoy"""
    print("\n=== CÁLCULO SIMPLE DE GANANCIA NETA HOY ===")
    print("(Solo considera: Total Vendido - Costo de Productos)")
    
    resultado = controller.calcular_ganancia_neta_simple_hoy_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        
        print(f"📅 Fecha: {data['fecha']}")
        print("-" * 80)
        
        if data['cantidad_ventas'] == 0:
            print("ℹ️  No hay ventas registradas para hoy")
            return
        
        print(f"🏪 RESUMEN SIMPLE:")
        print(f"   • Cantidad de ventas: {data['cantidad_ventas']}")
        print(f"   • Total vendido: ${data['total_vendido']:,.2f}")
        print(f"   • Costo de productos: ${data['total_costos_productos']:,.2f}")
        print(f"   • Ganancia neta simple: ${data['ganancia_neta_simple']:,.2f}")
        
        if data['total_vendido'] > 0:
            margen = (data['ganancia_neta_simple'] / data['total_vendido']) * 100
            print(f"   • Margen de ganancia: {margen:.1f}%")
        
        if data['detalles_productos']:
            print(f"\n📦 PRODUCTOS VENDIDOS (DETALLE SIMPLE):")
            print("-" * 90)
            print(f"{'Producto':<25} {'Cant.':<6} {'P.Venta':<10} {'Costo':<10} {'G.Unit':<10} {'G.Total':<10}")
            print("-" * 90)
            
            for detalle in data['detalles_productos'][:10]:
                print(f"{detalle['producto'][:24]:<25} {detalle['cantidad']:<6.1f} ${detalle['precio_venta_unitario']:<9.2f} ${detalle['costo_unitario']:<9.2f} ${detalle['ganancia_unitaria']:<9.2f} ${detalle['ganancia_total_producto']:<9.2f}")
            
            if len(data['detalles_productos']) > 10:
                print(f"   ... y {len(data['detalles_productos']) - 10} productos más")
            print("-" * 90)
        
        print("-" * 80)
    else:
        print(f"❌ {resultado['message']}")

def mostrar_calculo_ganancia_simple_fecha():
    """Muestra el cálculo simple para una fecha específica"""
    print("\n=== CÁLCULO SIMPLE DE GANANCIA NETA POR FECHA ===")
    print("(Solo considera: Total Vendido - Costo de Productos)")
    
    fecha = input("Fecha a calcular (YYYY-MM-DD): ").strip()
    
    resultado = controller.calcular_ganancia_neta_simple_fecha_controller(fecha)
    
    if resultado["success"]:
        data = resultado["data"]
        
        print(f"\n📅 Cálculo simple para: {data['fecha']}")
        print("-" * 60)
        
        if data['cantidad_ventas'] == 0:
            print(f"ℹ️  No hay ventas registradas para {fecha}")
            return
        
        print(f"🏪 Resumen simple: {data['cantidad_ventas']} ventas")
        print(f"💰 Total vendido: ${data['total_vendido']:,.2f}")
        print(f"💸 Costo productos: ${data['total_costos_productos']:,.2f}")
        print(f"💚 Ganancia neta simple: ${data['ganancia_neta_simple']:,.2f}")
        
        if data['total_vendido'] > 0:
            margen = (data['ganancia_neta_simple'] / data['total_vendido']) * 100
            print(f"📈 Margen: {margen:.1f}%")
        
        print("-" * 60)
    else:
        print(f"❌ {resultado['message']}")

def comparar_ganancia_hoy_vs_ayer():
    """Compara la ganancia de hoy con la de ayer"""
    print("\n=== COMPARACIÓN HOY vs AYER ===")
    
    resultado = controller.comparar_ganancia_hoy_vs_ayer_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        
        # Caso 1: No hay ganancia hoy (data = None)
        if data is None:
            print("ℹ️  No hay ganancias registradas para hoy.")
            print("   No hay nada que comparar.")
            return
        
        # Caso 2: Hay ganancia hoy pero no ayer (data = False)
        if data is False:
            print("⚠️  Hay ganancias hoy pero no hay ganancias de ayer.")
            print("   No se puede hacer la comparación.")
            return
        
        # Caso 3: Hay ganancias ambos días (data = dict)
        print(f"📊 COMPARACIÓN DE GANANCIAS NETAS SIMPLES:")
        print("=" * 70)
        print(f"📅 Ayer ({data['fecha_ayer']}):")
        print(f"   • Ganancia neta: ${data['ganancia_ayer']:,.2f}")
        print(f"   • Ventas realizadas: {data['ventas_ayer']}")
        print(f"   • Total vendido: ${data['total_vendido_ayer']:,.2f}")
        
        print(f"\n📅 Hoy ({data['fecha_hoy']}):")
        print(f"   • Ganancia neta: ${data['ganancia_hoy']:,.2f}")
        print(f"   • Ventas realizadas: {data['ventas_hoy']}")
        print(f"   • Total vendido: ${data['total_vendido_hoy']:,.2f}")
        
        print(f"\n📈 ANÁLISIS COMPARATIVO:")
        print("-" * 50)
        
        # Mostrar diferencia
        if data['diferencia'] > 0:
            print(f"📈 Tendencia: {data['tendencia'].upper()}")
            print(f"💰 Diferencia: +${data['diferencia']:,.2f}")
            print(f"📊 Porcentaje de mejora: +{data['porcentaje_cambio']:.1f}%")
        elif data['diferencia'] < 0:
            print(f"📉 Tendencia: {data['tendencia'].upper()}")
            print(f"💸 Diferencia: -${abs(data['diferencia']):,.2f}")
            print(f"📊 Porcentaje de disminución: {abs(data['porcentaje_cambio']):.1f}%")
        else:
            print(f"➡️  Tendencia: IGUAL")
            print(f"💰 Diferencia: $0.00")
            print(f"📊 Sin cambios")
        
        print("-" * 50)
        
        # Análisis adicional
        if data['diferencia'] > 0:
            print("🎉 ¡Felicidades! Hoy tuviste mejor ganancia que ayer.")
        elif data['diferencia'] < 0:
            print("⚠️  La ganancia de hoy fue menor que la de ayer.")
            print("💡 Revisa qué factores pudieron influir en la disminución.")
        else:
            print("➡️  La ganancia se mantiene igual que ayer.")
        
        print("=" * 70)
    else:
        print(f"❌ {resultado['message']}")

def comparar_metodos_calculo():
    """Compara el cálculo completo vs el cálculo simple para hoy"""
    print("\n=== COMPARACIÓN DE MÉTODOS DE CÁLCULO ===")
    
    # Obtener cálculo completo
    completo = controller.calcular_ganancias_hoy_controller()
    # Obtener cálculo simple
    simple = controller.calcular_ganancia_neta_simple_hoy_controller()
    
    if completo["success"] and simple["success"]:
        data_completo = completo["data"]
        data_simple = simple["data"]
        
        print(f"📅 Fecha: {data_completo['fecha']}")
        print("=" * 80)
        print(f"{'CONCEPTO':<35} {'MÉTODO COMPLETO':<20} {'MÉTODO SIMPLE':<20}")
        print("=" * 80)
        print(f"{'Total vendido':<35} ${data_completo['total_ventas']:<19,.2f} ${data_simple['total_vendido']:<19,.2f}")
        print(f"{'Costo de productos':<35} ${data_completo['total_costos_productos']:<19,.2f} ${data_simple['total_costos_productos']:<19,.2f}")
        print(f"{'Costos operativos diarios':<35} ${data_completo['total_costos_operativos_diarios']:<19,.2f} ${'0.00':<19}")
        print(f"{'Impuestos fijos diarios':<35} ${data_completo['total_impuestos_fijos_diarios']:<19,.2f} ${'0.00':<19}")
        print(f"{'Impuestos porcentuales diarios':<35} ${data_completo['total_impuestos_porcentuales_diarios']:<19,.2f} ${'0.00':<19}")
        print("-" * 80)
        print(f"{'GANANCIA NETA':<35} ${data_completo['ganancia_neta']:<19,.2f} ${data_simple['ganancia_neta_simple']:<19,.2f}")
        
        if data_completo['total_ventas'] > 0:
            margen_completo = (data_completo['ganancia_neta'] / data_completo['total_ventas']) * 100
            margen_simple = (data_simple['ganancia_neta_simple'] / data_simple['total_vendido']) * 100
            print(f"{'Margen de ganancia':<35} {margen_completo:<19.1f}% {margen_simple:<19.1f}%")
        
        diferencia = data_simple['ganancia_neta_simple'] - data_completo['ganancia_neta']
        print("-" * 80)
        print(f"💡 Diferencia entre métodos: ${diferencia:,.2f}")
        print(f"   (El método simple es ${abs(diferencia):,.2f} {'mayor' if diferencia > 0 else 'menor'} que el completo)")
        print("=" * 80)
    else:
        print("❌ Error al obtener los cálculos para comparar")

def mostrar_calculo_ganancias_hoy():
    """Muestra el cálculo detallado de ganancias para hoy sin registrar"""
    print("\n=== CÁLCULO DE GANANCIAS HOY ===")
    
    resultado = controller.calcular_ganancias_hoy_controller()
    
    if resultado["success"]:
        data = resultado["data"]
        
        print(f"📅 Fecha: {data['fecha']}")
        print("-" * 80)
        
        if data['cantidad_ventas'] == 0:
            print("ℹ️  No hay ventas registradas para hoy")
            return
        
        print(f"🏪 RESUMEN DE VENTAS:")
        print(f"   • Cantidad de ventas: {data['cantidad_ventas']}")
        print(f"   • Total en ventas: ${data['total_ventas']:,.2f}")
        print(f"   • Costo de productos vendidos: ${data['total_costos_productos']:,.2f}")
        
        print(f"\n💰 CÁLCULO DE GANANCIA BRUTA:")
        print(f"   • Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
        
        if data['detalles_productos']:
            print(f"\n📦 PRODUCTOS VENDIDOS:")
            print("-" * 80)
            print(f"{'Producto':<25} {'Cant.':<6} {'Precio':<10} {'Costo':<10} {'Costo Total':<12}")
            print("-" * 80)
            
            for detalle in data['detalles_productos'][:10]:  # Mostrar máximo 10
                print(f"{detalle['producto'][:24]:<25} {detalle['cantidad']:<6.1f} ${detalle['precio_venta']:<9.2f} ${detalle['costo_unitario']:<9.2f} ${detalle['costo_total']:<11.2f}")
            
            if len(data['detalles_productos']) > 10:
                print(f"   ... y {len(data['detalles_productos']) - 10} productos más")
            print("-" * 80)
        
        print(f"\n🏭 COSTOS OPERATIVOS APLICADOS:")
        if data['costos_aplicados']:
            for costo in data['costos_aplicados']:
                tipo_display = f"({costo['tipo']})"
                print(f"   • {costo['nombre']} {tipo_display}: ${costo['monto_mensual']:,.2f}/mes → ${costo['monto_diario']:,.2f}/día")
            print(f"   📊 Total costos operativos diarios: ${data['total_costos_operativos_diarios']:,.2f}")
        else:
            print("   ℹ️  No hay costos operativos aplicados")
        
        print(f"\n💸 IMPUESTOS APLICADOS:")
        if data['impuestos_aplicados']:
            for impuesto in data['impuestos_aplicados']:
                if impuesto['tipo'] == 'fijo':
                    print(f"   • {impuesto['nombre']} (fijo): ${impuesto['valor_mensual']:,.2f}/mes → ${impuesto['valor_diario']:,.2f}/día")
                elif impuesto['tipo'] == 'porcentaje':
                    print(f"   • {impuesto['nombre']} (porcentual): {impuesto['porcentaje_mensual']:.2f}%/mes → {impuesto['porcentaje_diario']:.4f}%/día = ${impuesto['monto_aplicado']:,.2f}")
            
            total_impuestos_diarios = data['total_impuestos_fijos_diarios'] + data['total_impuestos_porcentuales_diarios']
            print(f"   📊 Total impuestos diarios: ${total_impuestos_diarios:,.2f}")
            print(f"       - Fijos: ${data['total_impuestos_fijos_diarios']:,.2f}")
            print(f"       - Porcentuales: ${data['total_impuestos_porcentuales_diarios']:,.2f}")
        else:
            print("   ℹ️  No hay impuestos aplicados")
        
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"   💚 Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
        print(f"   💛 Ganancia neta: ${data['ganancia_neta']:,.2f}")
        
        # Mostrar eficiencia
        if data['ganancia_bruta'] > 0:
            eficiencia = (data['ganancia_neta'] / data['ganancia_bruta']) * 100
            print(f"   📈 Eficiencia: {eficiencia:.1f}%")
        
        if data['ya_calculado']:
            print(f"\n⚠️  Ya existe un registro de ganancias para esta fecha")
        
        print("-" * 80)
    else:
        print(f"❌ {resultado['message']}")

def mostrar_calculo_ganancias_fecha():
    """Muestra el cálculo detallado para una fecha específica"""
    print("\n=== CÁLCULO DE GANANCIAS POR FECHA ===")
    
    fecha = input("Fecha a calcular (YYYY-MM-DD): ").strip()
    
    resultado = controller.calcular_ganancias_fecha_controller(fecha)
    
    if resultado["success"]:
        data = resultado["data"]
        
        print(f"\n📅 Cálculo para: {data['fecha']}")
        print("-" * 60)
        
        if data['cantidad_ventas'] == 0:
            print(f"ℹ️  No hay ventas registradas para {fecha}")
            return
        
        print(f"🏪 Resumen: {data['cantidad_ventas']} ventas - ${data['total_ventas']:,.2f}")
        print(f"💰 Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
        print(f"💛 Ganancia neta: ${data['ganancia_neta']:,.2f}")
        
        if data['ganancia_bruta'] > 0:
            eficiencia = (data['ganancia_neta'] / data['ganancia_bruta']) * 100
            print(f"📈 Eficiencia: {eficiencia:.1f}%")
        
        if data['ya_calculado']:
            print(f"✅ Ya registrado en base de datos")
        else:
            print(f"⏸️  Aún no registrado en base de datos")
        
        print("-" * 60)
    else:
        print(f"❌ {resultado['message']}")

def registrar_ganancias_hoy():
    """Registra las ganancias del día actual en la base de datos"""
    print("\n=== REGISTRAR GANANCIAS DE HOY ===")
    
    # Primero mostrar el cálculo
    calculo = controller.calcular_ganancias_hoy_controller()
    
    if not calculo["success"]:
        print(f"❌ Error al calcular: {calculo['message']}")
        return
    
    data = calculo["data"]
    
    if data['cantidad_ventas'] == 0:
        print("ℹ️  No hay ventas para hoy. No se puede registrar ganancias.")
        return
    
    print(f"📊 Resumen del cálculo:")
    print(f"   • Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
    print(f"   • Ganancia neta: ${data['ganancia_neta']:,.2f}")
    print(f"   • Basado en {data['cantidad_ventas']} ventas")
    
    if data['ganancia_bruta'] > 0:
        eficiencia = (data['ganancia_neta'] / data['ganancia_bruta']) * 100
        print(f"   • Eficiencia: {eficiencia:.1f}%")
    
    usar_sobrescribir = False
    if data['ya_calculado']:
        print(f"\n⚠️  Ya existe un registro para hoy")
        sobrescribir = input("¿Sobrescribir el registro existente? (s/N): ").lower()
        if sobrescribir != 's':
            print("Operación cancelada.")
            return
        usar_sobrescribir = True
    
    confirmar = input(f"\n¿Registrar estas ganancias en la base de datos? (s/N): ").lower()
    if confirmar != 's':
        print("Operación cancelada.")
        return
    
    # Registrar en base de datos
    resultado = controller.registrar_ganancias_hoy_controller(sobrescribir=usar_sobrescribir)
    
    if resultado["success"]:
        data_resultado = resultado["data"]
        print(f"\n✅ Ganancias {data_resultado['accion']} exitosamente!")
        print(f"   📅 Fecha: {data_resultado['fecha']}")
        print(f"   💚 Ganancia bruta: ${data_resultado['ganancia_bruta']:,.2f}")
        print(f"   💛 Ganancia neta: ${data_resultado['ganancia_neta']:,.2f}")
        print(f"   🆔 ID registro: {data_resultado['id']}")
    else:
        print(f"❌ Error: {resultado['message']}")

def registrar_ganancias_fecha():
    """Registra ganancias para una fecha específica"""
    print("\n=== REGISTRAR GANANCIAS FECHA ESPECÍFICA ===")
    
    fecha = input("Fecha (YYYY-MM-DD): ").strip()
    
    # Calcular primero
    calculo = controller.calcular_ganancias_fecha_controller(fecha)
    
    if not calculo["success"]:
        print(f"❌ Error al calcular: {calculo['message']}")
        return
    
    data = calculo["data"]
    
    if data['cantidad_ventas'] == 0:
        print(f"ℹ️  No hay ventas para {fecha}. No se puede registrar ganancias.")
        return
    
    print(f"\n📊 Cálculo para {fecha}:")
    print(f"   • Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
    print(f"   • Ganancia neta: ${data['ganancia_neta']:,.2f}")
    
    if data['ganancia_bruta'] > 0:
        eficiencia = (data['ganancia_neta'] / data['ganancia_bruta']) * 100
        print(f"   • Eficiencia: {eficiencia:.1f}%")
    
    sobrescribir = False
    if data['ya_calculado']:
        print(f"\n⚠️  Ya existe un registro para esta fecha")
        sobrescribir_input = input("¿Sobrescribir? (s/N): ").lower()
        sobrescribir = sobrescribir_input == 's'
        
        if not sobrescribir:
            print("Operación cancelada.")
            return
    
    confirmar = input(f"\n¿Registrar estas ganancias? (s/N): ").lower()
    if confirmar != 's':
        print("Operación cancelada.")
        return
    
    resultado = controller.registrar_ganancias_fecha_controller(fecha, sobrescribir)
    
    if resultado["success"]:
        data_resultado = resultado["data"]
        print(f"\n✅ Ganancias {data_resultado['accion']}!")
        print(f"   💰 Total neto: ${data_resultado['ganancia_neta']:,.2f}")
    else:
        print(f"❌ Error: {resultado['message']}")

def consultar_ganancias_registradas():
    """Consulta ganancias ya registradas en base de datos"""
    print("\n=== CONSULTAR GANANCIAS REGISTRADAS ===")
    
    fecha = input("Fecha a consultar (YYYY-MM-DD): ").strip()
    
    resultado = controller.consultar_ganancia_fecha_controller(fecha)
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\n📋 Ganancia registrada para {fecha}:")
        print("-" * 50)
        print(f"🆔 ID: {data['id']}")
        print(f"💚 Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
        print(f"💛 Ganancia neta: ${data['ganancia_neta']:,.2f}")
        
        if data['ganancia_bruta'] > 0:
            eficiencia = (data['ganancia_neta'] / data['ganancia_bruta']) * 100
            print(f"📈 Eficiencia: {eficiencia:.1f}%")
        
        print("-" * 50)
    else:
        print(f"❌ {resultado['message']}")

def mostrar_ganancias_semana():
    """Muestra ganancias de la última semana"""
    resultado = controller.listar_ganancias_semana_controller()
    
    if resultado["success"]:
        ganancias = resultado["data"]["ganancias"]
        resumen = resultado["data"]["resumen"]
        
        print("\n=== GANANCIAS DE LA SEMANA ===")
        print("-" * 70)
        print(f"{'Fecha':<12} {'G.Bruta':<12} {'G.Neta':<12} {'Eficiencia':<12}")
        print("-" * 70)
        
        for ganancia in ganancias:
            eficiencia = (ganancia['ganancia_neta'] / ganancia['ganancia_bruta'] * 100) if ganancia['ganancia_bruta'] > 0 else 0
            print(f"{ganancia['fecha']:<12} ${ganancia['ganancia_bruta']:<11,.0f} ${ganancia['ganancia_neta']:<11,.0f} {eficiencia:<11.1f}%")
        
        print("-" * 70)
        print(f"📊 RESUMEN DE LA SEMANA:")
        print(f"   • Días con registros: {resumen['cantidad_dias']}")
        print(f"   • Total bruto: ${resumen['total_bruta']:,.2f}")
        print(f"   • Total neto: ${resumen['total_neta']:,.2f}")
        print(f"   • Promedio diario neto: ${resumen['promedio_neta']:,.2f}")
        
        if resumen['total_bruta'] > 0:
            eficiencia_total = (resumen['total_neta'] / resumen['total_bruta']) * 100
            print(f"   • Eficiencia promedio: {eficiencia_total:.1f}%")
        
        print("-" * 70)
    else:
        print(f"❌ {resultado['message']}")

def mostrar_ganancias_mes_actual():
    """Muestra ganancias del mes actual"""
    resultado = controller.obtener_resumen_mes_actual_controller()
    
    if resultado["success"]:
        ganancias = resultado["data"]["ganancias"]
        resumen = resultado["data"]["resumen"]
        
        print("\n=== GANANCIAS DEL MES ACTUAL ===")
        print(f"📈 Días registrados: {resumen['cantidad_dias']}")
        print(f"💚 Total bruto del mes: ${resumen['total_bruta']:,.2f}")
        print(f"💛 Total neto del mes: ${resumen['total_neta']:,.2f}")
        print(f"📊 Promedio diario neto: ${resumen['promedio_neta']:,.2f}")
        
        if resumen['total_bruta'] > 0:
            eficiencia_total = (resumen['total_neta'] / resumen['total_bruta']) * 100
            print(f"📈 Eficiencia promedio: {eficiencia_total:.1f}%")
        
        if len(ganancias) <= 10:
            print(f"\n📋 Todos los registros:")
            print("-" * 50)
            for ganancia in ganancias:
                eficiencia = (ganancia['ganancia_neta'] / ganancia['ganancia_bruta'] * 100) if ganancia['ganancia_bruta'] > 0 else 0
                print(f"  {ganancia['fecha']}: ${ganancia['ganancia_neta']:,.2f} ({eficiencia:.1f}%)")
        else:
            print(f"\n📋 Últimos 10 registros:")
            print("-" * 50)
            for ganancia in ganancias[:10]:
                eficiencia = (ganancia['ganancia_neta'] / ganancia['ganancia_bruta'] * 100) if ganancia['ganancia_bruta'] > 0 else 0
                print(f"  {ganancia['fecha']}: ${ganancia['ganancia_neta']:,.2f} ({eficiencia:.1f}%)")
            print(f"  ... y {len(ganancias) - 10} más")
        print("-" * 50)
    else:
        print(f"❌ {resultado['message']}")

def consultar_rango_ganancias():
    """Consulta ganancias en un rango de fechas"""
    print("\n=== CONSULTAR RANGO DE GANANCIAS ===")
    
    try:
        fecha_inicio = input("Fecha inicio (YYYY-MM-DD): ").strip()
        fecha_fin = input("Fecha fin (YYYY-MM-DD): ").strip()
        
        resultado = controller.listar_ganancias_rango_controller(fecha_inicio, fecha_fin)
        
        if resultado["success"]:
            ganancias = resultado["data"]["ganancias"]
            resumen = resultado["data"]["resumen"]
            
            print(f"\n📊 {resultado['message']}")
            print("-" * 75)
            print(f"{'Fecha':<12} {'G.Bruta':<12} {'G.Neta':<12} {'Eficiencia':<12}")
            print("-" * 75)
            
            for ganancia in ganancias:
                if ganancia['ganancia_bruta'] > 0:
                    eficiencia = (ganancia['ganancia_neta'] / ganancia['ganancia_bruta']) * 100
                    eficiencia_str = f"{eficiencia:.1f}%"
                else:
                    eficiencia_str = "N/A"
                
                print(f"{ganancia['fecha']:<12} ${ganancia['ganancia_bruta']:<11,.0f} ${ganancia['ganancia_neta']:<11,.0f} {eficiencia_str:<12}")
            
            print("-" * 75)
            print(f"💰 RESUMEN DEL PERÍODO:")
            print(f"   • Días registrados: {resumen['cantidad_dias']}")
            print(f"   • Total bruto: ${resumen['total_bruta']:,.2f}")
            print(f"   • Total neto: ${resumen['total_neta']:,.2f}")
            print(f"   • Promedio diario neto: ${resumen['promedio_neta']:,.2f}")
            
            if resumen['total_bruta'] > 0:
                eficiencia_total = (resumen['total_neta'] / resumen['total_bruta']) * 100
                print(f"   • Eficiencia total: {eficiencia_total:.1f}%")
            
            print("-" * 75)
        else:
            print(f"❌ {resultado['message']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def eliminar_ganancia():
    """Elimina un registro de ganancias"""
    print("\n=== ELIMINAR REGISTRO DE GANANCIAS ===")
    
    fecha = input("Fecha del registro a eliminar (YYYY-MM-DD): ").strip()
    
    # Consultar primero para mostrar información
    consulta = controller.consultar_ganancia_fecha_controller(fecha)
    
    if not consulta["success"]:
        print(f"❌ {consulta['message']}")
        return
    
    data = consulta["data"]
    print(f"\n📋 Registro encontrado:")
    print(f"   💚 Ganancia bruta: ${data['ganancia_bruta']:,.2f}")
    print(f"   💛 Ganancia neta: ${data['ganancia_neta']:,.2f}")
    
    confirmar = input(f"\n⚠️  ¿ELIMINAR este registro? (escribí 'ELIMINAR' para confirmar): ")
    
    if confirmar != 'ELIMINAR':
        print("Operación cancelada.")
        return
    
    resultado = controller.eliminar_ganancia_fecha_controller(fecha)
    
    if resultado["success"]:
        data = resultado["data"]
        print(f"\n✅ Registro eliminado exitosamente!")
        print(f"   📅 Fecha: {data['fecha']}")
        print(f"   💰 Ganancia eliminada: ${data['ganancia_neta']:,.2f}")
    else:
        print(f"❌ Error: {resultado['message']}")

def consultas_avanzadas():
    """Submenú para consultas avanzadas"""
    while True:
        print("\n=== CONSULTAS AVANZADAS ===")
        print("1. Ver ganancias del mes específico")
        print("2. Consultar rango personalizado")
        print("3. Eliminar registro de ganancias")
        print("4. Calcular ganancias sin registrar")
        print("5. Volver al menú principal")
        
        opcion = input("Elegí una opción: ")
        
        if opcion == "1":
            try:
                year = int(input("Año (ej: 2024): "))
                month = int(input("Mes (1-12): "))
                
                resultado = controller.listar_ganancias_mes_controller(year, month)
                
                if resultado["success"]:
                    ganancias = resultado["data"]["ganancias"]
                    resumen = resultado["data"]["resumen"]
                    
                    print(f"\n📅 GANANCIAS DE {month:02d}/{year}")
                    print(f"💰 Total neto del mes: ${resumen['total_neta']:,.2f}")
                    print(f"📊 Promedio diario: ${resumen['promedio_neta']:,.2f}")
                    
                    if resumen['total_bruta'] > 0:
                        eficiencia_total = (resumen['total_neta'] / resumen['total_bruta']) * 100
                        print(f"📈 Eficiencia promedio: {eficiencia_total:.1f}%")
                    
                    print(f"\n📋 Registros del mes:")
                    for ganancia in ganancias[:15]:  # Mostrar máximo 15
                        eficiencia = (ganancia['ganancia_neta'] / ganancia['ganancia_bruta'] * 100) if ganancia['ganancia_bruta'] > 0 else 0
                        print(f"  {ganancia['fecha']}: ${ganancia['ganancia_neta']:,.2f} ({eficiencia:.1f}%)")
                    
                    if len(ganancias) > 15:
                        print(f"  ... y {len(ganancias) - 15} más")
                else:
                    print(f"❌ {resultado['message']}")
                    
            except ValueError:
                print("❌ Entrada inválida.")
        
        elif opcion == "2":
            consultar_rango_ganancias()
        
        elif opcion == "3":
            eliminar_ganancia()
        
        elif opcion == "4":
            mostrar_calculo_ganancias_fecha()
        
        elif opcion == "5":
            break
        else:
            print("❌ Opción inválida.")

def menu_ganancias():
    """Menú principal del sistema de ganancias"""
    while True:
        print("\n" + "="*70)
        print("📈 SISTEMA DE MÉTRICAS - GANANCIAS")
        print("="*70)
        print("MÉTODO COMPLETO (con costos operativos e impuestos):")
        print("1. Ver cálculo detallado completo de hoy")
        print("2. Registrar ganancias de hoy")
        print("3. Registrar ganancias fecha específica")
        print("4. Consultar ganancias registradas")
        print("5. Ver ganancias de la semana")
        print("6. Ver ganancias del mes actual")
        print("\nMÉTODO SIMPLE (solo productos):")
        print("7. Ver cálculo simple de ganancia neta hoy")
        print("8. Ver cálculo simple de fecha específica")
        print("9. Comparar métodos de cálculo")
        print("10. Comparar ganancia hoy vs ayer")
        print("\nOTRAS OPCIONES:")
        print("11. Consultas avanzadas")
        print("12. Salir")
        print("="*70)

        opcion = input("Elegí una opción: ")

        if opcion == "1":
            mostrar_calculo_ganancias_hoy()

        elif opcion == "2":
            registrar_ganancias_hoy()

        elif opcion == "3":
            registrar_ganancias_fecha()

        elif opcion == "4":
            consultar_ganancias_registradas()

        elif opcion == "5":
            mostrar_ganancias_semana()

        elif opcion == "6":
            mostrar_ganancias_mes_actual()

        elif opcion == "7":
            mostrar_calculo_ganancia_simple_hoy()

        elif opcion == "8":
            mostrar_calculo_ganancia_simple_fecha()

        elif opcion == "9":
            comparar_metodos_calculo()

        elif opcion == "10":
            comparar_ganancia_hoy_vs_ayer()

        elif opcion == "11":
            consultas_avanzadas()

        elif opcion == "12":
            print("👋 Saliendo del sistema de ganancias.")
            break

        else:
            print("❌ Opción inválida.")

if __name__ == "__main__":
    menu_ganancias()

# Ejecutar con: python -m aplicacion.backend.metricas.ganancias.test_ganancias