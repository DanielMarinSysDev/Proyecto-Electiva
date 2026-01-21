import json
import os

class GestorDatos:
    def __init__(self, ruta_archivo):
        # Construimos la ruta absoluta para evitar errores de "archivo no encontrado"
        self.ruta = os.path.join("data", ruta_archivo)
        self.asegurar_directorio()

    def asegurar_directorio(self):
        """Si la carpeta 'data' no existe, la crea."""
        if not os.path.exists("data"):
            os.makedirs("data")

    def leer_datos(self):
        """Lee el JSON y devuelve una lista. Si no existe, devuelve lista vacía."""
        if not os.path.exists(self.ruta):
            return []
        
        try:
            with open(self.ruta, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            # Si el archivo está corrupto o vacío, devolvemos lista vacía
            return []
        except Exception as e:
            print(f"Error al leer datos: {e}")
            return []

    def guardar_datos(self, datos):
        """Recibe una lista de diccionarios y la guarda en el JSON."""
        try:
            with open(self.ruta, 'w', encoding='utf-8') as archivo:
                # indent=4 hace que el JSON se vea bonito y legible para humanos
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar datos: {e}")
            return False