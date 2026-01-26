import os
import datetime

def registrar_accion(mensaje, usuario="Sistema"):
    """
    Guarda un mensaje en el archivo historial.txt con fecha y hora.
    """
    # Calculamos la ruta absoluta para que siempre encuentre la carpeta data
    ruta_actual = os.path.abspath(__file__)
    carpeta_src = os.path.dirname(ruta_actual)
    carpeta_proyecto = os.path.dirname(carpeta_src)
    ruta_log = os.path.join(carpeta_proyecto, "data", "historial.txt")
    
    fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha_hora}] - {usuario.upper()}: {mensaje}\n"
    
    try:
        with open(ruta_log, 'a', encoding='utf-8') as f:
            f.write(linea)
    except Exception as e:
        print(f"Error al escribir en el log: {e}")