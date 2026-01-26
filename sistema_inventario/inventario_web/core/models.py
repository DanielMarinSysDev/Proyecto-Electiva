from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

def validar_positivo(value):
    if value < 0:
        raise ValidationError('El valor no puede ser negativo.')

class Producto(models.Model):
    sku = models.CharField(max_length=10, unique=True, verbose_name="SKU / Código")
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_positivo])
    cantidad = models.IntegerField(default=0, verbose_name="Stock Actual", validators=[validar_positivo])
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
        ('ELIMINACION', 'Eliminación'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True) # Null=True para conservar historial si se borra producto (opcional, o SET_NULL)
    # Nota: Si se borra el producto, idealmente deberíamos guardar al menos el nombre o SKU en otro campo para referencia.
    # Por simplicidad ahora, si se borra el producto, dejaremos este campo null o se borrará en cascada según lógica de negocio.
    # Cambiemos a SET_NULL para mantener el registro.
    producto_nombre = models.CharField(max_length=100, blank=True, null=True, help_text="Copia del nombre por si se borra el producto")
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if self.producto and not self.producto_nombre:
            self.producto_nombre = self.producto.nombre
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo} - {self.producto_nombre or 'Desconocido'} ({self.fecha})"

