import json
import os

class GestorDatos:
    def __init__(self, ruta_archivo):
        # TRUCO: Obtenemos la ruta absoluta de este archivo (gestor_datos.py)
        # .../sistema_inventario/SRC/gestor_datos.py
        ruta_actual = os.path.abspath(__file__)
        
        # Subimos un nivel para salir de SRC y llegar a 'sistema_inventario'
        carpeta_src = os.path.dirname(ruta_actual)
        carpeta_proyecto = os.path.dirname(carpeta_src)
        
        # Definimos que la carpeta data SIEMPRE estará dentro de sistema_inventario
        self.ruta_carpeta_data = os.path.join(carpeta_proyecto, "data")
        self.ruta = os.path.join(self.ruta_carpeta_data, ruta_archivo)
        
        self.asegurar_directorio()

    def asegurar_directorio(self):
        """Si la carpeta 'data' no existe en la ruta calculada, la crea."""
        if not os.path.exists(self.ruta_carpeta_data):
            try:
                os.makedirs(self.ruta_carpeta_data)
            except OSError as e:
                print(f"Error creando carpeta data: {e}")

    def leer_datos(self):
        """Lee el JSON y devuelve una lista. Si no existe, devuelve lista vacía."""
        if not os.path.exists(self.ruta):
            return []
        
        try:
            with open(self.ruta, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return []
        except Exception as e:
            print(f"Error al leer datos: {e}")
            return []

    def guardar_datos(self, datos):
        """Recibe una lista de diccionarios y la guarda en el JSON."""
        try:
            with open(self.ruta, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False