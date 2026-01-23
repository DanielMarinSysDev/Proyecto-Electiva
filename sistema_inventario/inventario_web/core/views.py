from django.shortcuts import render
from .models import Producto

def lista_productos(request):
    # Esto equivale a tu antiguo db.leer_datos()
    productos = Producto.objects.all()
    
    context = {
        'productos': productos
    }
    # Renderizamos (dibujamos) el HTML enviándole los datos
    return render(request, 'core/lista_productos.html', context)

# Create your views here.
