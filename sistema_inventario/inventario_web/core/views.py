from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import Sum, F
from django.db import models
from django.http import HttpResponse
from .models import Producto, HistorialMovimiento, UserAudit, validar_positivo
from .forms import ProductoForm, MovimientoForm
from django.utils import timezone
import csv
from io import StringIO
from django.core.management import call_command

# --- DASHBOARD & HOME ---
# --- DASHBOARD & HOME ---
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')

def public_catalog(request):
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    query = request.GET.get('q')
    if query:
        productos = productos.filter(
            models.Q(nombre__icontains=query) | 
            models.Q(categoria__icontains=query) |
            models.Q(sku__icontains=query)
        )
    return render(request, 'core/public_catalog.html', {'productos': productos})

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
@permission_required('core.add_producto', raise_exception=True)
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
@login_required
@permission_required('core.change_producto', raise_exception=True)
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
@permission_required('core.delete_producto', raise_exception=True)
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

import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def api_registrar_movimiento(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    try:
        data = json.loads(request.body)
        tipo = data.get('tipo')
        cantidad = int(data.get('cantidad', 0))
        
        if cantidad <= 0:
            return JsonResponse({'success': False, 'error': 'La cantidad debe ser mayor a 0.'})

        if tipo == 'ENTRADA':
            producto.cantidad += cantidad
            action_msg = f'Entrada de {cantidad}'
        elif tipo == 'SALIDA':
            if producto.cantidad >= cantidad:
                producto.cantidad -= cantidad
                action_msg = f'Salida de {cantidad}'
            else:
                return JsonResponse({'success': False, 'error': 'Stock insuficiente.'})
        else:
            return JsonResponse({'success': False, 'error': 'Tipo de movimiento inválido.'})

        producto.save()
        
        # Guardar historial
        HistorialMovimiento.objects.create(
            producto=producto,
            usuario=request.user,
            tipo=tipo,
            cantidad=cantidad
        )
        
        # Recalcular valor total del inventario para devolverlo
        total_valor = Producto.objects.aggregate(
            valor=Sum(F('precio') * F('cantidad'), output_field=models.DecimalField())
        )['valor'] or 0

        return JsonResponse({
            'success': True, 
            'message': f'{action_msg} registrada correctamente.',
            'new_stock': producto.cantidad,
            'total_valor': float(total_valor) # Convert to float for JSON
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@permission_required('core.delete_historialmovimiento', raise_exception=True)
def limpiar_movimientos(request):
    if not request.user.is_superuser:
        messages.error(request, 'Solo administradores pueden realizar esta acción.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        HistorialMovimiento.objects.all().delete()
        messages.success(request, 'Historial de movimientos eliminado correctamente.')
        
    return redirect('dashboard')

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

@login_required
@permission_required('auth.change_user', raise_exception=True)
def editar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    
    # Prevent editing superusers by non-superusers (redundant if only superuser has perms, but safe)
    if usuario.is_superuser and not request.user.is_superuser:
        messages.error(request, 'No tienes permiso para editar administradores.')
        return redirect('lista_usuarios')

    from .forms import UsuarioEditForm # Import here to avoid circulars if any
    
    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado al 100%.')
            return redirect('lista_usuarios')
    else:
        form = UsuarioEditForm(instance=usuario)
    
    return render(request, 'core/form_usuario.html', {
        'form': form, 
        'titulo': f'Editar Usuario: {usuario.username}',
        'usuario_editar': usuario # Pass user to template to show "Change Password" link
    })

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Tu contraseña ha sido actualizada correctamente.')
            return redirect('perfil_usuario')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'core/perfil.html', {'form': form})

@login_required
def audit_logs(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado. Solo administradores pueden ver los registros de auditoría.')
        return redirect('dashboard')
    
    logs = UserAudit.objects.all().order_by('-timestamp')[:100] # Limit to 100 for perf
    return render(request, 'core/admin_audit.html', {'logs': logs})

@login_required
def admin_backup(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acceso denegado.')
        return redirect('dashboard')
    
    sysout = StringIO()
    # Dump only 'core' app data to avoid huge auth/session dumps, or use no args for everything
    call_command('dumpdata', 'core', stdout=sysout) 
    response = HttpResponse(sysout.getvalue(), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="backup_inventario_{timezone.now().date()}.json"'
    return response


from django.contrib.auth.forms import SetPasswordForm

@login_required
@permission_required('auth.change_user', raise_exception=True)
def cambiar_password(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = SetPasswordForm(usuario, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contraseña de "{usuario.username}" actualizada.')
            return redirect('lista_usuarios')
    else:
        form = SetPasswordForm(usuario)
        
    return render(request, 'core/form_password.html', {
        'form': form,
        'titulo': f'Cambiar Contraseña: {usuario.username}'
    })


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

# --- QR CODE GENERATION ---
import qrcode
from io import BytesIO

@login_required
def generar_qr(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    # URL pointing to public catalog filtering by SKU
    base_url = request.build_absolute_uri('/catalogo/')
    qr_data = f"{base_url}?q={producto.sku}"
    
    img = qrcode.make(qr_data)
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    
    return HttpResponse(buffer, content_type='image/png')
