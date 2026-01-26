from gestor_datos import GestorDatos
import os

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_usuarios(usuario_actual):
    db = GestorDatos("usuarios.json")
    
    while True:
        limpiar_pantalla()
        print("\n=== PANEL DE ADMINISTRACIÓN DE USUARIOS ===")
        print("1. Listar Usuarios")
        print("2. Crear Nuevo Usuario")
        print("3. Cambiar Contraseña de un Usuario")
        print("4. Eliminar Usuario")
        print("5. Volver al Menú Principal")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            listar_usuarios(db)
        elif opcion == "2":
            crear_usuario(db)
        elif opcion == "3":
            editar_usuario(db)
        elif opcion == "4":
            eliminar_usuario(db, usuario_actual)
        elif opcion == "5":
            break
        else:
            input("Opción no válida. Enter para continuar...")

def listar_usuarios(db):
    usuarios = db.leer_datos()
    print("\n--- PERSONAL REGISTRADO ---")
    print(f"{'ID':<5} {'USUARIO':<15} {'ROL'}")
    print("-" * 30)
    for u in usuarios:
        print(f"{u['id']:<5} {u['username']:<15} {u['rol']}")
    input("\nPresione Enter para volver...")

def crear_usuario(db):
    usuarios = db.leer_datos()
    print("\n--- NUEVO USUARIO ---")
    nuevo_user = input("Username: ").strip()
    
    # Validación: No duplicados
    for u in usuarios:
        if u['username'] == nuevo_user:
            print("¡Error! Ese usuario ya existe.")
            input("Enter para continuar...")
            return

    nuevo_pass = input("Password: ").strip()
    rol = input("Rol (admin/user): ").strip().lower()
    
    if rol not in ['admin', 'user']:
        print("Rol inválido. Se asignará 'user' por defecto.")
        rol = 'user'

    nuevo_id = 1
    if usuarios:
        nuevo_id = usuarios[-1]['id'] + 1

    usuarios.append({
        "id": nuevo_id,
        "username": nuevo_user,
        "password": nuevo_pass,
        "rol": rol
    })
    
    if db.guardar_datos(usuarios):
        print("Usuario creado exitosamente.")
    input("Enter para continuar...")

def editar_usuario(db):
    usuarios = db.leer_datos()
    print("\n--- CAMBIAR CONTRASEÑA ---")
    target_user = input("Ingrese el Username a editar: ")
    
    usuario_encontrado = None
    for u in usuarios:
        if u['username'] == target_user:
            usuario_encontrado = u
            break
            
    if not usuario_encontrado:
        print("Usuario no encontrado.")
    else:
        nueva_pass = input(f"Nueva contraseña para {target_user}: ")
        usuario_encontrado['password'] = nueva_pass
        db.guardar_datos(usuarios)
        print("Contraseña actualizada.")
        
    input("Enter para continuar...")

def eliminar_usuario(db, usuario_actual):
    usuarios = db.leer_datos()
    print("\n--- ELIMINAR USUARIO ---")
    target_user = input("Ingrese el Username a eliminar: ")
    
    # Validación: No auto-eliminarse
    if target_user == usuario_actual['username']:
        print("¡Error! No puedes eliminar tu propia cuenta mientras la usas.")
        input("Enter para continuar...")
        return

    # Filtramos la lista para quitar al usuario (List Comprehension)
    # Esto crea una lista nueva SIN el usuario que queremos borrar
    lista_nueva = [u for u in usuarios if u['username'] != target_user]
    
    if len(lista_nueva) == len(usuarios):
        print("Usuario no encontrado.")
    else:
        confirmacion = input(f"¿Seguro que desea eliminar a '{target_user}'? (s/n): ")
        if confirmacion.lower() == 's':
            db.guardar_datos(lista_nueva)
            print("Usuario eliminado.")
        else:
            print("Operación cancelada.")
            
    input("Enter para continuar...")