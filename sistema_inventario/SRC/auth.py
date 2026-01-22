from gestor_datos import GestorDatos

def autenticar_usuario():
    """
    Solicita credenciales al usuario y verifica contra la base de datos.
    Retorna el diccionario del usuario si es correcto, o None si falla.
    """
    db_usuarios = GestorDatos("usuarios.json")
    usuarios = db_usuarios.leer_datos()
    
    print("\n=== INICIAR SESIÓN ===")
    usuario_input = input("Usuario: ")
    password_input = input("Contraseña: ")
    
    # Buscamos si existe alguna coincidencia en la lista de usuarios
    for usuario in usuarios:
        if usuario["username"] == usuario_input and usuario["password"] == password_input:
            print(f"\n¡Bienvenido, {usuario['username']}!")
            return usuario
            
    print("\nError: Usuario o contraseña incorrectos.")
    return None

def registrar_usuario_nuevo():
    """
    Permite crear un usuario nuevo. (Solo accesible por admins en el futuro)
    """
    db_usuarios = GestorDatos("usuarios.json")
    usuarios = db_usuarios.leer_datos()
    
    print("\n--- Registrar Nuevo Usuario ---")
    nuevo_user = input("Nombre de usuario nuevo: ")
    
    # Validación 1: Verificar que no exista ya
    for u in usuarios:
        if u["username"] == nuevo_user:
            print("Error: El usuario ya existe.")
            return

    nuevo_pass = input("Contraseña: ")
    rol = input("Rol (admin/user): ").lower()
    
    # Creamos el nuevo ID (simplemente el último + 1)
    nuevo_id = 1
    if usuarios:
        nuevo_id = usuarios[-1]["id"] + 1
        
    usuario_nuevo = {
        "id": nuevo_id,
        "username": nuevo_user,
        "password": nuevo_pass,
        "rol": rol
    }
    
    usuarios.append(usuario_nuevo)
    if db_usuarios.guardar_datos(usuarios):
        print("Usuario registrado exitosamente.")