from gestor_datos import GestorDatos

def inicializar_sistema():
    # 1. Conectamos con el archivo de usuarios
    db_usuarios = GestorDatos("usuarios.json")
    
    # 2. Leemos qué usuarios existen
    usuarios = db_usuarios.leer_datos()
    
    # 3. Lógica: Si no hay usuarios, creamos el Admin por defecto
    if not usuarios:
        print("--- Configuración Inicial ---")
        print("No se encontraron usuarios. Creando Administrador...")
        
        admin_user = {
            "id": 1,
            "username": "admin",
            "password": "123",  # En un sistema real esto iría encriptado
            "rol": "admin"
        }
        
        usuarios.append(admin_user)
        db_usuarios.guardar_datos(usuarios)
        print("¡Usuario Admin creado con éxito!")
    else:
        print(f"Sistema cargado. Se encontraron {len(usuarios)} usuarios.")

if __name__ == "__main__":
    inicializar_sistema()