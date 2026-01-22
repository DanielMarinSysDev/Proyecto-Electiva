from gestor_datos import GestorDatos
from auth import autenticar_usuario, registrar_usuario_nuevo
import os
from inventory import menu_inventario
from reports import menu_reportes
from admin_users import menu_usuarios

def limpiar_pantalla():
    # Detecta si es Windows ('nt') o Linux/Mac ('posix')
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_principal(usuario_actual):
    """
    El bucle principal del programa una vez logueado.
    """
    while True:
        print("\n" + "="*30)
        print(f" SISTEMA DE INVENTARIO - Usuario: {usuario_actual['username']} ({usuario_actual['rol']})")
        print("="*30)
        print("1. Gestión de Inventario (Próximamente)")
        print("2. Reportes (Próximamente)")
        
        # Solo mostramos opción de crear usuarios si es admin
        if usuario_actual['rol'] == 'admin':
            print("3. Administración de Usuarios")
            
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            menu_inventario()
        elif opcion == "2":
            menu_reportes()  # <-- Conectamos el módulo nuevo
        elif opcion == "3" and usuario_actual['rol'] == 'admin':
            menu_usuarios(usuario_actual)
        elif opcion == "0":
            print("Saliendo...")
            break
        else:
            print("Opción no válida.")

def inicializar_sistema():
    # 1. Aseguramos que existan datos básicos
    db = GestorDatos("usuarios.json")
    if not db.leer_datos():
        print("Creando usuario admin por defecto...")
        db.guardar_datos([{"id": 1, "username": "admin", "password": "123", "rol": "admin"}])

    # 2. Bucle de Login
    intentos = 0
    usuario_logueado = None
    
    while intentos < 3 and usuario_logueado is None:
        usuario_logueado = autenticar_usuario()
        if usuario_logueado:
            limpiar_pantalla()
            menu_principal(usuario_logueado)
        else:
            intentos += 1
            print(f"Intentos restantes: {3 - intentos}")
    
    if not usuario_logueado:
        print("Demasiados intentos fallidos. Sistema bloqueado.")

if __name__ == "__main__":
    inicializar_sistema()