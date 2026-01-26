from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, F
from django.http import HttpResponse
from .models import Producto, HistorialMovimiento, validar_positivo
from .forms import ProductoForm, MovimientoForm
from django.utils import timezone
import csv

# --- DASHBOARD & HOME ---
@login_required
def dashboard(request):
    total_productos = Producto.objects.aggregate(total=Sum('cantidad'))['total'] or 0
    valor_inventario = Producto.objects.aggregate(
        valor=Sum(F('precio') * F('cantidad'), output_field=models.DecimalField())
    )['valor'] or 0
    productos_bajo_stock = Producto.objects.filter(cantidad__lt=5).count()
    ultimos_movimientos = HistorialMovimiento.objects.select_related('producto').order_by('-fecha')[:5]

    context = {
        'total_productos': total_productos,
        'valor_inventario': valor_inventario,
        'productos_bajo_stock': productos_bajo_stock,
        'ultimos_movimientos': ultimos_movimientos
    }
    return render(request, 'core/dashboard.html', context)

# --- PRODUCTS CRUD ---
@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    query = request.GET.get('q')
    if query:
        productos = productos.filter(models.Q(nombre__icontains=query) | models.Q(sku__icontains=query))
    
    return render(request, 'core/lista_productos.html', {'productos': productos})

@login_required
@permission_required('core.add_producto')
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save()
            HistorialMovimiento.objects.create(
                producto=producto,
                usuario=request.user,
                tipo='CREACION',
                cantidad=producto.cantidad
            )
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    return render(request, 'core/form_producto.html', {'form': form, 'titulo': 'Nuevo Producto'})

@login_required
@permission_required('core.change_producto')
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            HistorialMovimiento.objects.create(
                producto=producto,
                usuario=request.user,
                tipo='EDICION',
                cantidad=0 # No changed stock, just details
            )
            return redirect('lista_productos')
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'core/form_producto.html', {'form': form, 'titulo': f'Editar {producto.nombre}'})

@login_required
@permission_required('core.delete_producto')
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        HistorialMovimiento.objects.create(
            producto_nombre=producto.nombre,
            usuario=request.user,
            tipo='ELIMINACION',
            cantidad=producto.cantidad
        )
        producto.delete()
        return redirect('lista_productos')
    return render(request, 'core/confirmar_eliminar.html', {'producto': producto})

# --- MOVEMENTS ---
@login_required
def registrar_movimiento(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.producto = producto
            movimiento.usuario = request.user
            
            tipo = movimiento.tipo
            cantidad = movimiento.cantidad
            
            if tipo == 'ENTRADA':
                producto.cantidad += cantidad
            elif tipo == 'SALIDA':
                if producto.cantidad >= cantidad:
                    producto.cantidad -= cantidad
                else:
                    form.add_error('cantidad', 'No hay suficiente stock.')
                    return render(request, 'core/form_movimiento.html', {'form': form, 'producto': producto})
            
            producto.save()
            movimiento.save()
            return redirect('lista_productos')
    else:
        form = MovimientoForm()
    return render(request, 'core/form_movimiento.html', {'form': form, 'producto': producto})

# --- REPORTS ---
@login_required
def reportes(request):
    bajos_stock = Producto.objects.filter(cantidad__lt=5)
    return render(request, 'core/reportes.html', {'bajos_stock': bajos_stock})

@login_required
def exportar_reporte(request):
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="reporte_inventario_{timezone.now().date()}.txt"'
    
    writer = csv.writer(response)
    writer.writerow(['SKU', 'NOMBRE', 'CATEGORIA', 'PRECIO', 'STOCK'])
    
    for p in Producto.objects.all():
        writer.writerow([p.sku, p.nombre, p.categoria, p.precio, p.cantidad])
        
    return response
