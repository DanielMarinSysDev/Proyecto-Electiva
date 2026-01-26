from django import forms
from .models import Producto, HistorialMovimiento

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['sku', 'nombre', 'categoria', 'precio', 'cantidad']
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. P001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = HistorialMovimiento
        fields = ['tipo', 'cantidad']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
