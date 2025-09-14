from aplicacion.backend.usuarios.usuarios import controller

def menu_usuarios():
    while True:
        print("\n=== TEST DE USUARIOS ===")
        print("1. Registrar usuario")
        print("2. Login")
        print("3. Editar usuario")
        print("4. Recuperar contraseña por email")
        print("5. Listar todos los usuarios")
        print("6. Ver usuario por ID")
        print("7. Salir")

        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            nombre_usuario = input("Nombre de usuario: ").strip()
            password = input("Contraseña: ").strip()
            email = input("Email: ").strip()
            registrado = controller.registrar_usuario_controller(nombre_usuario, password, email)
            if registrado:
                print("✅ Usuario registrado correctamente.")
            else:
                print("❌ No se pudo registrar el usuario.")

        elif opcion == "2":
            nombre_usuario = input("Nombre de usuario: ").strip()
            password = input("Contraseña: ").strip()
            usuario = controller.login_usuario_controller(nombre_usuario, password)
            if usuario:
                print(f"Login exitoso. Bienvenido, {usuario.nombre_usuario}.")
            else:
                print("Credenciales inválidas.")

        elif opcion == "3":
            user_id = int(input("ID del usuario a editar: ").strip())
            nuevo_nombre = input("Nuevo nombre (dejar vacío para no cambiar): ").strip()
            nuevo_password = input("Nueva contraseña (dejar vacío para no cambiar): ").strip()
            nuevo_email = input("Nuevo email (dejar vacío para no cambiar): ").strip()
            data = {}
            if nuevo_nombre:
                data["nombre_usuario"] = nuevo_nombre
            if nuevo_password:
                data["password"] = nuevo_password
            if nuevo_email:
                data["email"] = nuevo_email
            usuario = controller.editar_usuario_controller(user_id, data)
            if usuario:
                print(f"Usuario actualizado: {usuario.nombre_usuario}")
            else:
                print("No se encontró el usuario.")

        elif opcion == "4":
            nombre_usuario = input("Nombre de usuario para recuperar contraseña: ").strip()
            exito = controller.recuperar_password_controller(nombre_usuario)
            if exito:
                print(f"Se ha enviado una contraseña temporal al email registrado del usuario '{nombre_usuario}'.")
            else:
                print("No se encontró un usuario con ese nombre.")

        elif opcion == "5":
            usuarios = controller.listar_usuarios_controller()
            print("\nUsuarios registrados:")
            for u in usuarios:
                print(f"ID: {u.id}, Usuario: {u.nombre_usuario}")

        elif opcion == "6":
            user_id = int(input("ID del usuario a ver: ").strip())
            usuario = controller.obtener_usuario_controller(user_id)
            if usuario:
                print(f"Usuario: {usuario.nombre_usuario} (ID: {usuario.id})")
            else:
                print("Usuario no encontrado.")

        elif opcion == "7":
            break

        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu_usuarios()
    
#python -m aplicacion.backend.usuarios.usuarios.test_usuarios