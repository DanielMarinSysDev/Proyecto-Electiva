from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, F
from django.db import models
from django.http import HttpResponse
from .models import Producto, HistorialMovimiento, validar_positivo
from .forms import ProductoForm, MovimientoForm
from django.utils import timezone
import csv

# --- DASHBOARD & HOME ---
# --- DASHBOARD & HOME ---
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')

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
    
    # Calculate Total Inventory Value
    valor_inventario = productos.aggregate(
        valor=Sum(F('precio') * F('cantidad'), output_field=models.DecimalField())
    )['valor'] or 0

    return render(request, 'core/lista_productos.html', {
        'productos': productos, 
        'valor_inventario': valor_inventario
    })

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
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
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
            messages.success(request, f'Producto "{producto.nombre}" actualizado correctamente.')
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
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre}" eliminado correctamente.')
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
                messages.success(request, f'Entrada de {cantidad} unidades registrada.')
            elif tipo == 'SALIDA':
                if producto.cantidad >= cantidad:
                    producto.cantidad -= cantidad
                    messages.success(request, f'Salida de {cantidad} unidades registrada.')
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

# --- USERS MANAGEMENT (Admin Only) ---
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

@login_required
@permission_required('auth.view_user', raise_exception=True)
def lista_usuarios(request):
    usuarios = User.objects.all().order_by('date_joined')
    return render(request, 'core/lista_usuarios.html', {'usuarios': usuarios})

@login_required
@permission_required('auth.add_user', raise_exception=True)
def crear_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
            return redirect('lista_usuarios')
    else:
        form = UserCreationForm()
    return render(request, 'core/form_usuario.html', {'form': form, 'titulo': 'Nuevo Usuario'})

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario.is_superuser:
        messages.error(request, 'No puedes eliminar a un superusuario.')
        return redirect('lista_usuarios')
    
    if request.method == 'POST':
        nombre = usuario.username
        usuario.delete()
        messages.success(request, f'Usuario "{nombre}" eliminado.')
        return redirect('lista_usuarios')
    
    return render(request, 'core/confirmar_eliminar.html', {'producto': usuario, 'titulo': f'Eliminar Usuario {usuario.username}'})

# --- PDF GENERATION ---
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

@login_required
def exportar_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    filename = f"inventario_{timezone.now().date()}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1 # Center
    )
    elements.append(Paragraph("Reporte de Inventario", title_style))
    elements.append(Paragraph(f"Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Data
    data = [['SKU', 'Nombre', 'Categoría', 'Precio', 'Stock']]
    productos = Producto.objects.all()
    
    for p in productos:
        data.append([
            p.sku,
            p.nombre[:30], # Truncate long names
            p.categoria,
            f"${p.precio}",
            str(p.cantidad)
        ])

    # Table configuration
    table = Table(data, colWidths=[80, 200, 100, 80, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (-1, 0), (-1, -1), 'CENTER'), # Center Stock column
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response
