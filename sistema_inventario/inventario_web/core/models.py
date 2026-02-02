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

    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
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

class UserAudit(models.Model):
    """
    Log de auditoría para cambios en usuarios (Caja Negra).
    """
    ACTION_CHOICES = [
        ('CREATE', 'Creación'),
        ('UPDATE', 'Edición'),
        ('DELETE', 'Eliminación'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    admin = models.CharField(max_length=150, help_text="Usuario que realizó la acción") # CharField in case admin is deleted
    target_user = models.CharField(max_length=150, help_text="Usuario afectado")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.admin} -> {self.action} -> {self.target_user}"

# --- SIGNALS FOR AUDIT ---
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
# Thread local to store current request user (Admin)
import threading

_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def set_current_user(user):
    _thread_locals.user = user

@receiver(post_save, sender=User)
def log_user_save(sender, instance, created, **kwargs):
    # Avoid recursion/loops
    if hasattr(instance, '_audit_disable'):
        return

    admin_user = get_current_user()
    admin_name = admin_user.username if admin_user else "Sistema/Desconocido"
    
    action = 'CREATE' if created else 'UPDATE'
    
    # Don't log login updates (last_login) as essential edits unless crucial
    # Check fields if needed, but for now simple logging
    
    UserAudit.objects.create(
        action=action,
        admin=admin_name,
        target_user=instance.username,
        details=f"Email: {instance.email}, Staff: {instance.is_staff}, Superuser: {instance.is_superuser}"
    )

@receiver(post_delete, sender=User)
def log_user_delete(sender, instance, **kwargs):
    admin_user = get_current_user()
    admin_name = admin_user.username if admin_user else "Sistema/Desconocido"

    UserAudit.objects.create(
        action='DELETE',
        admin=admin_name,
        target_user=instance.username,
        details="Usuario eliminado permanentemente."
    )

