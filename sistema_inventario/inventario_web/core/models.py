from django.db import models
from django.contrib.auth.models import User # Usaremos el sistema de usuarios de Django

class Producto(models.Model):
    sku = models.CharField(max_length=10, unique=True, verbose_name="SKU / Código")
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.IntegerField(default=0, verbose_name="Stock Actual")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

class HistorialMovimiento(models.Model):
    """
    Equivalente a tu historial.txt pero guardado en Base de Datos.
    """
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('CREACION', 'Creación'),
        ('EDICION', 'Edición'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.fecha})"
# Create your models here.
