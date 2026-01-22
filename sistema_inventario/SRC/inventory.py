from gestor_datos import GestorDatos
import os

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_inventario():
    db = GestorDatos("productos.json")
    
    while True:
        limpiar_pantalla()
        print("\n=== GESTIÓN DE INVENTARIO ===")
        print("1. Ver Productos")
        print("2. Agregar Producto")
        print("3. Volver al Menú Principal")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            listar_productos(db)
        elif opcion == "2":
            agregar_producto(db)
        elif opcion == "3":
            break
        else:
            input("Opción no válida. Enter para continuar...")

def listar_productos(db):
    productos = db.leer_datos()
    limpiar_pantalla()
    print("\n--- LISTA DE PRODUCTOS ---")
    
    if not productos:
        print("No hay productos registrados.")
    else:
        # Encabezado bonito
        print(f"{'SKU':<10} {'NOMBRE':<20} {'CATEGORIA':<15} {'PRECIO':<10} {'CANTIDAD'}")
        print("-" * 70)
        for p in productos:
            print(f"{p['sku']:<10} {p['nombre']:<20} {p['categoria']:<15} ${p['precio']:<9} {p['cantidad']}")
    
    input("\nPresione Enter para volver...")

def agregar_producto(db):
    productos = db.leer_datos()
    print("\n--- NUEVO PRODUCTO ---")
    
    # 1. Validación de duplicados (Requisito clave)
    sku = input("Código (SKU): ").strip().upper()
    for p in productos:
        if p['sku'] == sku:
            print("¡Error! Ya existe un producto con ese SKU.")
            input("Enter para continuar...")
            return

    nombre = input("Nombre del producto: ").strip()
    categoria = input("Categoría: ").strip()
    
    # 2. Validación de tipos de datos (Try-Except)
    try:
        precio = float(input("Precio: "))
        cantidad = int(input("Cantidad inicial: "))
    except ValueError:
        print("¡Error! Precio o Cantidad deben ser números.")
        input("Enter para continuar...")
        return

    nuevo_producto = {
        "sku": sku,
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "cantidad": cantidad
    }
    
    productos.append(nuevo_producto)
    if db.guardar_datos(productos):
        print("¡Producto guardado éxito!")
    input("Enter para continuar...")