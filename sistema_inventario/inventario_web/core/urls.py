from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.public_catalog, name='public_catalog'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('productos/movimiento/<int:pk>/', views.registrar_movimiento, name='registrar_movimiento'),
    path('productos/qr/<int:pk>/', views.generar_qr, name='generar_qr'),
    path('api/movimiento/<int:pk>/', views.api_registrar_movimiento, name='api_registrar_movimiento'),
    path('movimientos/limpiar/', views.limpiar_movimientos, name='limpiar_movimientos'),
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/exportar/', views.exportar_reporte, name='exportar_reporte'),
    path('reportes/pdf/', views.exportar_pdf, name='exportar_pdf'),
    
    # User Management
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/nuevo/', views.crear_usuario, name='crear_usuario'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/password/<int:pk>/', views.cambiar_password, name='cambiar_password'),
    path('usuarios/eliminar/<int:pk>/', views.eliminar_usuario, name='eliminar_usuario'), # Admin delete user
    path('perfil/', views.perfil_usuario, name='perfil_usuario'), # Self-service profile
    path('seguridad/auditoria/', views.audit_logs, name='audit_logs'), # Audit Log - Changed to avoid admin/ conflict
    path('seguridad/respaldo/', views.admin_backup, name='admin_backup'), # JSON Backup
    
    # Auth Views
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]