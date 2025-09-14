from aplicacion.backend.stock.importer import cargar_productos_desde_csv, ruta_csv
import os
from aplicacion.backend.stock import controller
from aplicacion.backend.stock.crud import (
    crear_categoria_sin_categoria,
    asignar_producto_a_categoria,
    quitar_categoria_a_producto,
    exportar_productos_json,
    obtener_categorias_json,
    exportar_categorias_json,
    exportar_proveedores_json,
)
from aplicacion.backend.stock.utils import (
    generar_codigo_barras,
    buscar_productos_por_nombre,
    buscar_productos_por_codigo,
    verificar_stock_bajo,
    fecha_actual_iso,
    obtener_codigos_por_producto,
    obtener_codigos_activos_por_producto,
    mostrar_codigos_producto,
)

def menu():
    while True:
        print("\n=== TEST DE STOCK ===")
        print("1. Agregar producto")
        print("2. Editar producto")
        print("3. Listar productos")
        print("4. Buscar producto por nombre")
        print("5. Agregar proveedor")
        print("6. Salir")
        print("7. Buscar producto por codigo de barras")
        print("8. Gestion de categorias")
        print("9. Cargar productos desde CSV")
        print("10. Listar unidades vencidas")
        print("11. Listar unidades proximas a vencer")
        print("12. Cargar mas stock a un producto existente")
        print("13. Exportar JSON de stock")
        print("14. Ver codigos de barras de un producto")
        print("15. Exportar JSON de categorias")
        print("16. Exportar JSON de proveedores")  # NUEVA OPCION
        opcion = input("Elegi una opcion: ")

        if opcion == "1":
            nombre = input("Nombre del producto: ")
            unidad = input("Unidad de medida (unidad/kg/l/etc): ")
            usa_redondeo = True  # Se aplica siempre

            costo = float(input("Costo unitario: "))
            usar_precio_directo = input("¿Queres ingresar directamente el precio de venta? (s/n): ").lower()
            if usar_precio_directo == "s":
                precio_venta = float(input("Precio de venta: "))
                from aplicacion.backend.stock.utils import calcular_margen_con_precio
                margen = calcular_margen_con_precio(costo, precio_venta)
                print(f"El margen de ganancia calculado es: {margen:.2f}")
                # margen ya fue calculado arriba
            else:
                margen = float(input("Margen de ganancia (0.2 para 20%): "))
                precio_venta = None

            proveedor_id = None
            hay_proveedor = input("¿El producto tiene proveedor? (s/n): ").lower()
            if hay_proveedor == "s":
                proveedores = controller.listar_proveedores_controller()
                if proveedores:
                    print("Proveedores existentes:")
                    for pr in proveedores:
                        print(f"[{pr.id}] {pr.nombre}")
                    ya_registrado = input("¿Esta registrado? (s/n): ").lower()
                    if ya_registrado == "s":
                        proveedor_id = int(input("Ingresa el ID del proveedor: "))
                    else:
                        nuevo_nombre = input("Nombre del nuevo proveedor: ")
                        contacto = input("Contacto: ")
                        direccion = input("Direccion: ")
                        telefono = input("Telefono: ")
                        email = input("Email: ")
                        nuevo_proveedor = controller.agregar_proveedor_controller({
                            "nombre": nuevo_nombre,
                            "contacto": contacto,
                            "direccion": direccion,
                            "telefono": telefono,
                            "email": email
                        })
                        proveedor_id = nuevo_proveedor.id
                else:
                    print("No hay proveedores registrados. Se creara uno nuevo.")
                    nuevo_nombre = input("Nombre del nuevo proveedor: ")
                    contacto = input("Contacto: ")
                    direccion = input("Direccion: ")
                    telefono = input("Telefono: ")
                    email = input("Email: ")
                    nuevo_proveedor = controller.agregar_proveedor_controller({
                        "nombre": nuevo_nombre,
                        "contacto": contacto,
                        "direccion": direccion,
                        "telefono": telefono,
                        "email": email
                    })
                    proveedor_id = nuevo_proveedor.id

            categoria_id = None
            categorias = controller.listar_clasificaciones_controller()
            tiene_categoria = input("¿Queres asignar una categoria al producto? (s/n): ").lower()
            if tiene_categoria == "s":
                if categorias:
                    print("Categorias existentes:")
                    for c in categorias:
                        print(f"[{c.id}] {c.nombre}")
                    id_cat = input("Ingresa el ID de la categoria: ")
                    if id_cat.isdigit():
                        categoria_id = int(id_cat)
                else:
                    print("No hay categorias creadas. Se asignara como 'Sin categoria'.")
            else:
                print("El producto quedara sin categoria.")

            cantidad = float(input("Cantidad inicial: "))

            data = {
                "nombre": nombre,
                "unidad_medida": unidad,
                "cantidad": cantidad,
                "costo_unitario": costo,
                "margen_ganancia": margen,
                "usa_redondeo": usa_redondeo,
                "proveedor_id": proveedor_id,
                "categoria_id": categoria_id,
            }
            if precio_venta is not None:
                data["precio_venta"] = precio_venta
                data["precio_redondeado"] = precio_venta

            p = controller.agregar_producto_controller(data)
            print("Producto agregado:", p.nombre)

            if unidad == "kg":
                from aplicacion.backend.stock.utils import generar_codigo_barras_con_letras
                # Genera un codigo alfanumerico unico para productos a granel
                codigo = generar_codigo_barras_con_letras()
                ahora = fecha_actual_iso()
                controller.agregar_unidad_controller({
                    "producto_id": p.id,
                    "codigo_barras": codigo,
                    "estado": "activo",
                    "fecha_ingreso": ahora,
                    "fecha_modificacion": ahora,
                    "observaciones": "Producto a granel (kg)",
                    "fecha_vencimiento": None
                })
                print(f"Producto por kg registrado con codigo interno: {codigo}")

            elif not p.es_divisible:
                cantidad_unidades = int(p.cantidad)
                print(f"Registrando {cantidad_unidades} unidades fisicas para '{p.nombre}'.")

                for i in range(cantidad_unidades):
                    print(f"\nUnidad {i+1} de {cantidad_unidades}")
                    usar_existente = input("¿Ingresar codigo de barras manualmente? (s/n): ").lower()
                    if usar_existente == "s":
                        codigo = input("Codigo de barras: ")
                    else:
                        codigo = generar_codigo_barras()
                        print("Codigo generado:", codigo)

                    observaciones = input("Observaciones (Enter si ninguna): ") or ""
                    vencimiento = input("Fecha de vencimiento (YYYY-MM-DD) o Enter si no tiene: ").strip()
                    vencimiento = vencimiento if vencimiento != "" else None

                    ahora = fecha_actual_iso()
                    controller.agregar_unidad_controller({
                        "producto_id": p.id,
                        "codigo_barras": codigo,
                        "estado": "activo",
                        "fecha_ingreso": ahora,
                        "fecha_modificacion": ahora,
                        "observaciones": observaciones,
                        "fecha_vencimiento": vencimiento
                    })

                print("Unidades registradas correctamente.")

        elif opcion == "2":
            idp = int(input("ID del producto a editar: "))
            campo = input("Campo a modificar (unidad_medida, costo_unitario, margen_ganancia, precio_venta): ")
            valor = input("Nuevo valor: ")

            if campo in ["costo_unitario", "margen_ganancia"]:
                valor = float(valor)
            elif campo == "precio_venta":
                valor = float(valor)

            data = {campo: valor}
            actualizado = controller.editar_producto_controller(idp, data)
            print("Producto actualizado:", actualizado.nombre if actualizado else "No encontrado")

        elif opcion == "3":
            productos = controller.listar_productos_controller()
            categorias = {c.id: c.nombre for c in controller.listar_clasificaciones_controller()}
            from aplicacion.backend.stock.utils import verificar_sin_stock
            for p in productos:
                alertas = []
                if verificar_sin_stock(p):
                    alertas.append("SIN STOCK")
                elif verificar_stock_bajo(p):
                    alertas.append("Bajo stock")
                alerta_str = " | ".join(alertas)
                nombre_categoria = categorias.get(p.categoria_id, "Sin categoria")
                print(f"[{p.id}] {p.nombre} - {p.cantidad} {p.unidad_medida} | ${p.precio_redondeado} | Categoria: {nombre_categoria} (Divisible: {p.es_divisible}) {alerta_str}")

        elif opcion == "4":
            nombre = input("Buscar por nombre: ")
            productos = controller.listar_productos_controller()
            encontrados = buscar_productos_por_nombre(productos, nombre)
            for p in encontrados:
                print(f"[{p.id}] {p.nombre}")

        elif opcion == "5":
            nombre = input("Nombre del proveedor: ")
            contacto = input("Contacto: ")
            direccion = input("Direccion: ")
            telefono = input("Telefono: ")
            email = input("Email: ")
            nuevo = controller.agregar_proveedor_controller({
                "nombre": nombre,
                "contacto": contacto,
                "direccion": direccion,
                "telefono": telefono,
                "email": email
            })
            print("Proveedor creado con ID:", nuevo.id)

        elif opcion == "6":
            print("Saliendo.")
            break

        elif opcion == "7":
            codigo = input("Ingresa el codigo de barras exacto: ")
            productos = controller.listar_productos_controller()
            unidades = []
            for p in productos:
                unidades += controller.obtener_unidades_de_producto_controller(p.id)
            encontrados = buscar_productos_por_codigo(unidades, codigo)
            if encontrados:
                unidad = encontrados[0]
                print(f"Codigo encontrado. Producto ID: {unidad.producto_id}, Codigo: {unidad.codigo_barras}")
            else:
                print("No se encontro el codigo.")

        elif opcion == "8":
            while True:
                print("\n--- GESTION DE CATEGORIAS ---")
                print("1. Crear nueva categoria")
                print("2. Listar categorias")
                print("3. Asignar producto a categoria")
                print("4. Quitar categoria de un producto")
                print("5. Crear categoria 'Sin categoria'")
                print("6. Volver")

                subop = input("Elegi una opcion: ")

                if subop == "1":
                    nombre = input("Nombre de la nueva categoria: ")
                    descripcion = input("Descripcion: ")
                    activa = True
                    nueva = controller.agregar_clasificacion_controller({
                        "nombre": nombre,
                        "descripcion": descripcion,
                        "activa": activa
                    })
                    print(f"Categoria creada con ID {nueva.id}")

                elif subop == "2":
                    categorias = controller.listar_clasificaciones_controller()
                    for c in categorias:
                        estado = "Activa" if c.activa else "Inactiva"
                        print(f"[{c.id}] {c.nombre} - {estado}")

                elif subop == "3":
                    id_prod = int(input("ID del producto: "))
                    id_cat = int(input("ID de la categoria: "))
                    asignar_producto_a_categoria(id_prod, id_cat)
                    print("Producto asignado.")

                elif subop == "4":
                    id_prod = int(input("ID del producto: "))
                    quitar_categoria_a_producto(id_prod)
                    print("Categoria quitada del producto.")

                elif subop == "5":
                    resultado = crear_categoria_sin_categoria()
                    print(f"Categoria disponible con ID {resultado.id}")

                elif subop == "6":
                    break

                else:
                    print("Opcion invalida.")

        elif opcion == "9":
            confirmar = input(f"¿Hay un archivo CSV en esta ruta?\n{ruta_csv}\n¿Deseas procesarlo? (s/n): ").lower()
            if confirmar == "s":
                if os.path.exists(ruta_csv):
                    cargar_productos_desde_csv()
                else:
                    print(f"No se encontro ningun archivo en:\n{ruta_csv}")
            else:
                print(f"Por favor, coloca el archivo CSV en esta ruta antes de ejecutar la carga:\n{ruta_csv}")

        elif opcion == "10":
            print("\n=== UNIDADES VENCIDAS ===")
            from aplicacion.backend.stock.crud import obtener_unidades_vencidas
            vencidas = obtener_unidades_vencidas()
            if vencidas:
                for unidad in vencidas:
                    print(f"[ID {unidad.id}] Producto ID: {unidad.producto_id} | Codigo: {unidad.codigo_barras} | Vence: {unidad.fecha_vencimiento}")
            else:
                print("No hay unidades vencidas.")

        elif opcion == "11":
            print("\n=== UNIDADES PROXIMAS A VENCER ===")
            from aplicacion.backend.stock.crud import obtener_unidades_por_vencer
            resultados = obtener_unidades_por_vencer()
            if resultados:
                for unidad, dias in resultados:
                    print(f"[ID {unidad.id}] Producto ID: {unidad.producto_id} | Codigo: {unidad.codigo_barras} | Vence: {unidad.fecha_vencimiento} | Faltan {dias} dias")
            else:
                print("No hay unidades proximas a vencer.")

        elif opcion == "12":
            try:
                id_producto = int(input("ID del producto al que queres agregar stock: "))
                cantidad = float(input("Cantidad a agregar: "))
                actualizado = controller.agregar_stock_controller(id_producto, cantidad)
                if actualizado:
                    print(f"Stock actualizado. Ahora hay {actualizado.cantidad} {actualizado.unidad_medida} de {actualizado.nombre}.")
                else:
                    print("No se encontro el producto.")
            except ValueError:
                print("Entrada invalida. Intenta nuevamente.")

        elif opcion == "13":
            print("\n=== EXPORTAR JSON DE STOCK ===")
            ok = exportar_productos_json()
            if ok:
                # misma logica de ruta que usa exportar_productos_json()
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                json_dir = os.path.join(base_dir, "frontend", "json")
                archivo_path = os.path.join(json_dir, "stock.json")

                if os.path.exists(archivo_path):
                    print(f"JSON creado en: {archivo_path}")
                    try:
                        import json
                        with open(archivo_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        print(f"{len(data)} productos exportados.")
                        preview = [p.get("nombre", "sin_nombre") for p in data[:5]]
                        if preview:
                            print("Ejemplos:", ", ".join(preview))
                    except Exception as e:
                        print(f"Se creo el archivo pero no pude leerlo: {e}")
                else:
                    print("La exportacion dijo OK pero no encontre el archivo.")
            else:
                print("Fallo la exportacion del JSON.")

        elif opcion == "14":
            print("\n=== VER CODIGOS DE BARRAS DE UN PRODUCTO ===")
            try:
                id_producto = int(input("Ingresa el ID del producto: "))
                
                # Verificar que el producto existe
                productos = controller.listar_productos_controller()
                producto_encontrado = None
                for p in productos:
                    if p.id == id_producto:
                        producto_encontrado = p
                        break
                
                if not producto_encontrado:
                    print(f"No se encontro el producto con ID: {id_producto}")
                    continue
                
                print(f"\nProducto: {producto_encontrado.nombre}")
                print(f"Stock actual: {producto_encontrado.cantidad} {producto_encontrado.unidad_medida}")
                print("=" * 50)
                
                # Mostrar menu de opciones para codigos
                print("1. Ver todos los codigos (activos e inactivos)")
                print("2. Ver solo codigos activos")
                print("3. Ver codigos con formato detallado")
                
                sub_opcion = input("Elegi una opcion: ")
                
                if sub_opcion == "1":
                    codigos = obtener_codigos_por_producto(id_producto)
                    if codigos:
                        print(f"\nTODOS LOS CODIGOS DEL PRODUCTO {id_producto}:")
                        for codigo, info in codigos.items():
                            estado_emoji = "OK" if info["estado"] == "activo" else "X"
                            venc = info["vencimiento"] or "Sin vencimiento"
                            print(f"{estado_emoji} {codigo} - Vence: {venc} - Estado: {info['estado']}")
                    else:
                        print("No se encontraron codigos para este producto.")
                
                elif sub_opcion == "2":
                    codigos_activos = obtener_codigos_activos_por_producto(id_producto)
                    if codigos_activos:
                        print(f"\nCODIGOS ACTIVOS DEL PRODUCTO {id_producto}:")
                        for codigo, vencimiento in codigos_activos.items():
                            venc = vencimiento or "Sin vencimiento"
                            print(f"{codigo} - Vence: {venc}")
                    else:
                        print("No se encontraron codigos activos para este producto.")
                
                elif sub_opcion == "3":
                    mostrar_codigos_producto(id_producto)
                
                else:
                    print("Opcion invalida.")
                    
            except ValueError:
                print("ID invalido. Debe ser un numero entero.")
            except Exception as e:
                print(f"Error al buscar codigos: {e}")

        elif opcion == "15":
            print("\n=== EXPORTAR JSON DE CATEGORIAS ===")
            ok = exportar_categorias_json()
            if ok:
                # misma logica de ruta que usa exportar_categorias_json()
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                json_dir = os.path.join(base_dir, "frontend", "json")
                archivo_path = os.path.join(json_dir, "categorias.json")

                if os.path.exists(archivo_path):
                    print(f"JSON de categorias creado en: {archivo_path}")
                    try:
                        import json
                        with open(archivo_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        print(f"{len(data)} categorias exportadas.")
                        # Mostrar preview de las categorias exportadas
                        if data:
                            print("Categorias exportadas:")
                            for categoria in data:
                                estado = "Activa" if categoria.get("activa") else "Inactiva"
                                print(f"  - {categoria.get('nombre', 'Sin nombre')} ({estado})")
                    except Exception as e:
                        print(f"Se creo el archivo pero no pude leerlo: {e}")
                else:
                    print("La exportacion dijo OK pero no encontre el archivo.")
            else:
                print("Fallo la exportacion del JSON de categorias.")

        elif opcion == "16":  # NUEVA OPCION PARA PROVEEDORES
            print("\n=== EXPORTAR JSON DE PROVEEDORES ===")
            ok = exportar_proveedores_json()
            if ok:
                # misma logica de ruta que usa exportar_proveedores_json()
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                json_dir = os.path.join(base_dir, "frontend", "json")
                archivo_path = os.path.join(json_dir, "proveedores.json")

                if os.path.exists(archivo_path):
                    print(f"JSON de proveedores creado en: {archivo_path}")
                    try:
                        import json
                        with open(archivo_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        print(f"{len(data)} proveedores exportados.")
                        # Mostrar preview de los proveedores exportados
                        if data:
                            print("Proveedores exportados:")
                            for proveedor in data:
                                nombre = proveedor.get('nombre', 'Sin nombre')
                                telefono = proveedor.get('telefono', 'Sin telefono')
                                email = proveedor.get('email', 'Sin email')
                                print(f"  - {nombre} | Tel: {telefono} | Email: {email}")
                    except Exception as e:
                        print(f"Se creo el archivo pero no pude leerlo: {e}")
                else:
                    print("La exportacion dijo OK pero no encontre el archivo.")
            else:
                print("Fallo la exportacion del JSON de proveedores.")

        else:
            print("Opcion invalida.")

if __name__ == "__main__":
    menu()

#python -m aplicacion.backend.stock.test_stock