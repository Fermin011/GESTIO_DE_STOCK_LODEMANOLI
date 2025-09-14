from aplicacion.backend.ventas import controller
from aplicacion.backend.ventas import crud
from aplicacion.backend.stock import controller as stock_controller

def mostrar_productos_disponibles():
    """Muestra todos los productos disponibles para venta"""
    productos = controller.obtener_todos_los_productos_controller()
    if not productos:
        print("No hay productos disponibles.")
        return
    
    print("\nProductos disponibles:")
    print("-" * 80)
    print(f"{'ID':<5} {'Nombre':<30} {'Stock':<10} {'Precio':<10} {'Unidad':<10}")
    print("-" * 80)
    for prod in productos:
        print(f"{prod['id']:<5} {prod['nombre']:<30} {prod['cantidad']:<10} ${prod['precio']:<9} {prod['unidad_medida']:<10}")
    print("-" * 80)

def mostrar_carrito():
    """Muestra el contenido actual del carrito"""
    carrito = controller.obtener_carrito_controller()
    if not carrito:
        print("Carrito vacío.")
        return
    
    print("\nCarrito actual:")
    print("-" * 85)
    print(f"{'#':<3} {'Producto':<25} {'Precio':<10} {'Cant.':<8} {'Tipo':<12} {'Subtotal':<10}")
    print("-" * 85)
    
    for i, item in enumerate(carrito):
        subtotal = item['precio_unitario'] * item['cantidad']
        tipo_venta = item.get('tipo_venta', 'codigo_barras')
        
        if tipo_venta == 'codigo_barras':
            tipo_display = "Cód.Barras"
            cantidad_display = f"{item['cantidad']} ud"
        else:
            tipo_display = "Por ID"
            unidad = "kg" if item.get('unidad_medida') == 'kg' else "ud"
            cantidad_display = f"{item['cantidad']} {unidad}"
        
        print(f"{i:<3} {item['nombre']:<25} ${item['precio_unitario']:<9} {cantidad_display:<7} {tipo_display:<12} ${subtotal:<9}")
    
    total = controller.calcular_total_carrito_controller()
    print("-" * 85)
    print(f"{'TOTAL':<67} ${total}")
    print("-" * 85)

def agregar_por_codigo_barras():
    """Maneja la adición de productos por código de barras"""
    codigo = input("Ingresá el código de barras del producto: ").strip()
    resultado = controller.agregar_producto_por_codigo_controller(codigo)
    
    if resultado.get("exito"):
        item = resultado["item"]
        print(f"✅ Agregado: {item['nombre']} - ${item['precio_unitario']}")
    else:
        print(f"❌ Error: {resultado.get('mensaje', 'No se pudo agregar el producto')}")

def agregar_por_id_producto():
    """Maneja la adición de productos por ID"""
    mostrar_productos_disponibles()
    
    try:
        prod_id = int(input("\nIngresá el ID del producto: ").strip())
        cantidad_input = input("Ingresá la cantidad (enter para 1 unidad): ").strip()
        
        if cantidad_input:
            cantidad = float(cantidad_input)
        else:
            cantidad = 1
            
        resultado = controller.agregar_producto_por_id_controller(prod_id, cantidad)
        
        if resultado.get("exito"):
            item = resultado["item"]
            tipo_venta = item.get('tipo_venta', 'producto_id')
            print(f"✅ Agregado por ID: {item['nombre']} - {cantidad} unidades - ${item['precio_unitario'] * cantidad}")
        else:
            print(f"❌ Error: {resultado.get('mensaje', 'No se pudo agregar el producto')}")
            
    except ValueError:
        print("❌ Entrada inválida. Operación cancelada.")

def gestionar_carrito():
    """Submenu para gestionar el carrito"""
    while True:
        print("\n=== GESTIÓN DE CARRITO ===")
        print("1. Ver carrito")
        print("2. Eliminar item del carrito")
        print("3. Limpiar carrito completo")
        print("4. Volver al menú principal")
        
        opcion = input("Elegí una opción: ")
        
        if opcion == "1":
            mostrar_carrito()
        elif opcion == "2":
            mostrar_carrito()
            try:
                indice = int(input("Ingresá el número del item a eliminar: "))
                resultado = controller.eliminar_item_carrito_controller(indice)
                if resultado.get("exito"):
                    print(f"✅ Item eliminado: {resultado['item']['nombre']}")
                else:
                    print(f"❌ Error: {resultado.get('mensaje')}")
            except ValueError:
                print("❌ Número inválido.")
        elif opcion == "3":
            confirmar = input("¿Estás seguro de limpiar todo el carrito? (s/N): ").lower()
            if confirmar == 's':
                controller.limpiar_carrito_controller()
                print("✅ Carrito limpiado.")
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")

def menu_ventas():
    while True:
        print("\n=== SISTEMA DE VENTAS ===")
        print("1. Agregar producto por código de barras")
        print("2. Agregar producto por ID")
        print("3. Ver productos disponibles")
        print("4. Gestionar carrito")
        print("5. Confirmar venta")
        print("6. Cancelar última venta")
        print("7. Limpiar unidades fantasma")
        print("8. Salir")

        opcion = input("Elegí una opción: ")

        if opcion == "1":
            agregar_por_codigo_barras()

        elif opcion == "2":
            agregar_por_id_producto()

        elif opcion == "3":
            mostrar_productos_disponibles()

        elif opcion == "4":
            gestionar_carrito()

        elif opcion == "5":
            carrito = controller.obtener_carrito_controller()
            if not carrito:
                print("❌ El carrito está vacío.")
                continue
                
            mostrar_carrito()
            confirmar = input("\n¿Confirmar esta venta? (s/N): ").lower()
            if confirmar != 's':
                print("Venta cancelada.")
                continue
                
            metodo = input("Método de pago: ").strip()
            if not metodo:
                print("❌ Método de pago requerido.")
                continue
                
            try:
                usuario_id = int(input("ID de usuario: ").strip())
            except ValueError:
                print("❌ ID de usuario inválido.")
                continue
                
            resultado = controller.confirmar_venta_controller({
                "metodo_pago": metodo,
                "usuario_id": usuario_id
            })

            if resultado.get("exito"):
                print(f"\n✅ Venta confirmada con éxito. ID: {resultado['venta_id']}")
                print(f"💰 Total: ${resultado['total']}")
                
                # Ejecutar limpieza automática de unidades fantasma
                for item in resultado["productos"]:
                    if hasattr(stock_controller, 'limpiar_unidades_fantasma_controller'):
                        stock_controller.limpiar_unidades_fantasma_controller(item["producto_id"])
            else:
                print(f"❌ Error al confirmar la venta: {resultado.get('mensaje')}")

        elif opcion == "6":
            resultado = controller.cancelar_ultima_venta_controller()
            if resultado.get("exito"):
                print(f"\n✅ Última venta cancelada correctamente. ID: {resultado['venta_id']}")
                if resultado.get('restaurados'):
                    print("Productos restaurados:")
                    for rest in resultado['restaurados']:
                        print(f"  - {rest['producto']}: +{rest['cantidad_restaurada']}")
            else:
                print(f"❌ Error al cancelar la venta: {resultado.get('mensaje')}")

        elif opcion == "7":
            try:
                prod_id = int(input("ID del producto a limpiar (cantidad 0): "))
                if hasattr(stock_controller, 'limpiar_unidades_fantasma_controller'):
                    stock_controller.limpiar_unidades_fantasma_controller(prod_id)
                    print(f"✅ Unidades fantasma limpiadas para el producto con ID {prod_id}.")
                else:
                    print("❌ Función de limpieza no disponible.")
            except ValueError:
                print("❌ ID inválido.")

        elif opcion == "8":
            print("Saliendo del sistema de ventas.")
            break

        else:
            print("Opción inválida.")

if __name__ == "__main__":
    menu_ventas()
    
# python -m aplicacion.backend.ventas.test_ventas

    
