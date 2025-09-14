from aplicacion.backend.usuarios.perfiles import controller

def menu_perfiles():
    while True:
        print("\n=== TEST DE PERFILES ===")
        print("1. Ver perfil de usuario")
        print("2. Actualizar nombre de perfil")
        print("3. Actualizar email de perfil")
        print("4. Actualizar teléfono de perfil")
        print("5. Salir")

        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            user_id = int(input("Ingresá el ID del usuario: "))
            perfil = controller.obtener_perfil_controller(user_id)
            if perfil:
                print(f"Perfil de Usuario {perfil.usuario_id}:")
                print(f"Nombre: {perfil.nombre}")
                print(f"Email: {perfil.email}")
                print(f"Teléfono: {perfil.telefono if perfil.telefono else 'No registrado'}")
            else:
                print("No se encontró perfil para este usuario.")

        elif opcion == "2":
            user_id = int(input("Ingresá el ID del usuario: "))
            nuevo_nombre = input("Nuevo nombre de perfil: ")
            actualizado = controller.actualizar_nombre_perfil_controller(user_id, nuevo_nombre)
            if actualizado:
                print(f"Nombre de perfil actualizado a: {nuevo_nombre}")
            else:
                print("No se pudo actualizar el nombre.")

        elif opcion == "3":
            user_id = int(input("Ingresá el ID del usuario: "))
            nuevo_email = input("Nuevo email de perfil: ")
            actualizado = controller.actualizar_email_perfil_controller(user_id, nuevo_email)
            if actualizado:
                print(f"Email de perfil actualizado a: {nuevo_email}")
            else:
                print("No se pudo actualizar el email.")

        elif opcion == "4":
            user_id = int(input("Ingresá el ID del usuario: "))
            nuevo_telefono = input("Nuevo número de teléfono: ")
            actualizado = controller.actualizar_telefono_perfil_controller(user_id, nuevo_telefono)
            if actualizado:
                print(f"Teléfono de perfil actualizado a: {nuevo_telefono}")
            else:
                print("No se pudo actualizar el teléfono.")

        elif opcion == "5":
            print("Saliendo del test de perfiles.")
            break
        else:
            print("Opción inválida. Probá de nuevo.")

if __name__ == "__main__":
    menu_perfiles()

#python -m aplicacion.backend.usuarios.perfiles.test_perfiles