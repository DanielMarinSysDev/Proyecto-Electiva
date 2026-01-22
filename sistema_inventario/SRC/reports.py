from gestor_datos import GestorDatos
import os
import datetime

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_reportes():
    db = GestorDatos("productos.json")
    
    while True:
        limpiar_pantalla()
        print("\n=== MÓDULO DE REPORTES ===")
        print("1. Ver Alertas de Stock Bajo")
        print("2. Calcular Valor Total del Inventario")
        print("3. Exportar Inventario a Archivo (.txt)")
        print("4. Volver al Menú Principal")
        
        opcion = input("\nOpción: ")
        
        if opcion == "1":
            reporte_stock_bajo(db)
        elif opcion == "2":
            calcular_valor_total(db)
        elif opcion == "3":
            exportar_inventario_txt(db)
        elif opcion == "4":
            break
        else:
            input("Opción no válida. Enter para continuar...")

def reporte_stock_bajo(db):
    """Filtra y muestra productos con menos de 5 unidades."""
    productos = db.leer_datos()
    stock_minimo = 5
    
    print(f"\n--- ALERTA: PRODUCTOS CON BAJO STOCK (< {stock_minimo}) ---")
    
    encontrados = False
    print(f"{'SKU':<10} {'NOMBRE':<20} {'CANTIDAD'}")
    print("-" * 40)
    
    for p in productos:
        if p['cantidad'] < stock_minimo:
            print(f"{p['sku']:<10} {p['nombre']:<20} {p['cantidad']} UNIDADES")
            encontrados = True
            
    if not encontrados:
        print("¡Todo en orden! No hay productos con stock crítico.")
        
    input("\nPresione Enter para volver...")

def calcular_valor_total(db):
    """Suma el precio * cantidad de todos los productos."""
    productos = db.leer_datos()
    total_general = 0
    cantidad_productos = 0
    
    for p in productos:
        subtotal = p['precio'] * p['cantidad']
        total_general += subtotal
        cantidad_productos += p['cantidad']
        
    print("\n--- RESUMEN FINANCIERO ---")
    print(f"Total de artículos en bodega: {cantidad_productos}")
    print(f"Valor total del inventario:   ${total_general:,.2f}")
    
    input("\nPresione Enter para volver...")

def exportar_inventario_txt(db):
    """Genera un archivo de texto con la fecha y el listado de productos."""
    productos = db.leer_datos()
    
    # Creamos un nombre de archivo con la fecha de hoy, ej: reporte_2023-10-25.txt
    fecha_hoy = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    nombre_archivo = f"reporte_inventario_{fecha_hoy}.txt"
    
    try:
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("========================================\n")
            f.write(f" REPORTE DE INVENTARIO - {fecha_hoy}\n")
            f.write("========================================\n\n")
            
            f.write(f"{'SKU':<10} {'NOMBRE':<20} {'CANTIDAD':<10} {'PRECIO'}\n")
            f.write("-" * 55 + "\n")
            
            for p in productos:
                linea = f"{p['sku']:<10} {p['nombre']:<20} {p['cantidad']:<10} ${p['precio']}\n"
                f.write(linea)
            
            f.write("\n========================================\n")
            f.write("FIN DEL REPORTE")
            
        print(f"\n[ÉXITO] Reporte generado: {nombre_archivo}")
        print("Busque el archivo en la carpeta de su proyecto.")
        
    except Exception as e:
        print(f"\n[ERROR] No se pudo exportar el archivo: {e}")
        
    input("\nPresione Enter para continuar...")