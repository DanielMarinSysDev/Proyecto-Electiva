from django.contrib import admin
from .models import Producto, HistorialMovimiento

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'categoria', 'precio', 'cantidad')
    search_fields = ('nombre', 'sku', 'categoria') # ¡Tu requisito de búsqueda ya está hecho aquí!
    list_filter = ('categoria',) # ¡Tu requisito de filtros también!

@admin.register(HistorialMovimiento)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'tipo', 'producto', 'cantidad')
    list_filter = ('tipo', 'fecha')
# Register your models here.
