from gestor_datos import GestorDatos
import os

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_inventario():
    db = GestorDatos("productos.json")
    
    while True:
        limpiar_pantalla()
        print("\n=== GESTIÓN DE INVENTARIO ===")
        print("1. Ver Todos los Productos")
        print("2. Buscar Producto (Filtro)")
        print("3. Agregar Producto")
        print("4. Editar Producto")
        print("5. Eliminar Producto")
        print("6. Registrar Movimiento (Entrada/Salida)")  # <--- NUEVO
        print("7. Volver al Menú Principal")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            listar_productos(db)
        elif opcion == "2":
            buscar_producto(db)
        elif opcion == "3":
            agregar_producto(db)
        elif opcion == "4":
            editar_producto(db)
        elif opcion == "5":
            eliminar_producto(db)
        elif opcion == "6":
            registrar_movimiento(db)  # <--- CONECTADO
        elif opcion == "7":
            break
        else:
            input("Opción no válida. Enter para continuar...")

def listar_productos(db):
    productos = db.leer_datos()
    mostrar_tabla(productos)
    input("\nPresione Enter para volver...")

def mostrar_tabla(lista_productos):
    """Función auxiliar para no repetir código de impresión"""
    limpiar_pantalla()
    print("\n--- LISTADO DE PRODUCTOS ---")
    
    if not lista_productos:
        print("No hay productos para mostrar.")
    else:
        print(f"{'SKU':<10} {'NOMBRE':<20} {'CATEGORIA':<15} {'PRECIO':<10} {'STOCK'}")
        print("-" * 70)
        for p in lista_productos:
            print(f"{p['sku']:<10} {p['nombre']:<20} {p['categoria']:<15} ${p['precio']:<9} {p['cantidad']}")

def buscar_producto(db):
    productos = db.leer_datos()
    limpiar_pantalla()
    print("\n--- BUSCAR PRODUCTO ---")
    termino = input("Ingrese nombre o categoría a buscar: ").strip().lower()
    
    resultados = [p for p in productos if termino in p['nombre'].lower() or termino in p['categoria'].lower()]
    
    if resultados:
        mostrar_tabla(resultados)
    else:
        print(f"\nNo se encontraron productos que coincidan con '{termino}'.")
        
    input("\nPresione Enter para continuar...")

def agregar_producto(db):
    productos = db.leer_datos()
    print("\n--- NUEVO PRODUCTO ---")
    
    sku = input("Código (SKU): ").strip().upper()
    for p in productos:
        if p['sku'] == sku:
            print("¡Error! Ya existe un producto con ese SKU.")
            input("Enter para continuar...")
            return

    nombre = input("Nombre del producto: ").strip()
    categoria = input("Categoría: ").strip()
    
    try:
        precio = float(input("Precio: "))
        if precio < 0: raise ValueError("El precio no puede ser negativo")
        
        cantidad = int(input("Cantidad inicial: "))
        if cantidad < 0: raise ValueError("La cantidad no puede ser negativa")
        
    except ValueError as e:
        print(f"¡Error! {e}")
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

def editar_producto(db):
    productos = db.leer_datos()
    print("\n--- EDITAR PRODUCTO ---")
    sku_buscar = input("Ingrese el SKU del producto a editar: ").strip().upper()
    
    indice = -1
    for i, p in enumerate(productos):
        if p['sku'] == sku_buscar:
            indice = i
            break
            
    if indice == -1:
        print("Producto no encontrado.")
        input("Enter para continuar...")
        return

    prod = productos[indice]
    print(f"\nEditando: {prod['nombre']} (Precio actual: ${prod['precio']})")
    print("Deje el campo vacío si no desea cambiar el valor.")
    
    nuevo_nombre = input("Nuevo nombre: ").strip()
    nuevo_precio_str = input("Nuevo precio: ").strip()
    
    if nuevo_nombre:
        prod['nombre'] = nuevo_nombre
    
    if nuevo_precio_str:
        try:
            nuevo_precio = float(nuevo_precio_str)
            if nuevo_precio < 0: raise ValueError
            prod['precio'] = nuevo_precio
        except ValueError:
            print("Precio inválido. No se actualizó el precio.")

    productos[indice] = prod
    db.guardar_datos(productos)
    print("\nProducto actualizado correctamente.")
    input("Enter para continuar...")

def eliminar_producto(db):
    productos = db.leer_datos()
    print("\n--- ELIMINAR PRODUCTO ---")
    sku_buscar = input("Ingrese el SKU del producto a eliminar: ").strip().upper()
    
    nueva_lista = [p for p in productos if p['sku'] != sku_buscar]
    
    if len(nueva_lista) == len(productos):
        print("Producto no encontrado.")
    else:
        confirmacion = input("¿Está seguro? Esto no se puede deshacer (s/n): ")
        if confirmacion.lower() == 's':
            db.guardar_datos(nueva_lista)
            print("Producto eliminado.")
        else:
            print("Operación cancelada.")
            
    input("Enter para continuar...")

def registrar_movimiento(db):
    """NUEVA FUNCIÓN: Permite sumar o restar stock fácilmente"""
    productos = db.leer_datos()
    print("\n--- REGISTRAR MOVIMIENTO DE STOCK ---")
    sku_buscar = input("SKU del producto: ").strip().upper()
    
    producto = None
    indice = -1
    for i, p in enumerate(productos):
        if p['sku'] == sku_buscar:
            producto = p
            indice = i
            break
    
    if not producto:
        print("Producto no encontrado.")
        input("Enter para continuar...")
        return

    print(f"Producto: {producto['nombre']} | Stock actual: {producto['cantidad']}")
    print("1. Entrada (Compra/Devolución)")
    print("2. Salida (Venta/Merma)")
    tipo = input("Seleccione tipo de movimiento: ").strip()
    
    try:
        cantidad = int(input("Cantidad a mover: "))
        if cantidad <= 0: raise ValueError("La cantidad debe ser mayor a 0")
        
        if tipo == "1": # Entrada
            producto['cantidad'] += cantidad
            print(f"✅ Stock actualizado. Nuevo total: {producto['cantidad']}")
            
        elif tipo == "2": # Salida
            if cantidad > producto['cantidad']:
                print("❌ ¡Error! No hay suficiente stock para realizar esta salida.")
                input("Enter para continuar...")
                return
            producto['cantidad'] -= cantidad
            print(f"✅ Stock actualizado. Nuevo total: {producto['cantidad']}")
            
        else:
            print("Opción inválida.")
            return

        productos[indice] = producto
        db.guardar_datos(productos)
        
    except ValueError:
        print("Error: Ingrese un número válido.")
        
    input("Enter para continuar...")