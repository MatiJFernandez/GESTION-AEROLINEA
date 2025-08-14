"""
URLs para la aplicación vuelos.

Este archivo define todas las rutas relacionadas con:
- Página principal del sitio
- Gestión de vuelos
- Gestión de aviones
- Gestión de asientos
"""

from django.urls import path
from . import views, admin_views

# Namespace para la aplicación vuelos
app_name = 'vuelos'

urlpatterns = [
    # Página principal del sitio
    path('', views.home, name='home'),
    
    # Gestión de vuelos
    path('vuelos/', views.lista_vuelos, name='lista_vuelos'),
    path('vuelos/<int:vuelo_id>/', views.detalle_vuelo, name='detalle_vuelo'),
    path('vuelos/buscar/', views.buscar_vuelos, name='buscar_vuelos'),
    
    # Gestión de aviones (solo para administradores)
    path('aviones/', views.lista_aviones, name='lista_aviones'),
    path('aviones/<int:avion_id>/', views.detalle_avion, name='detalle_avion'),
    
    # Gestión de asientos
    path('asientos/<int:avion_id>/', views.asientos_avion, name='asientos_avion'),
    path('asientos/<int:asiento_id>/disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    
    # URLs administrativas
    path('dashboard/', admin_views.dashboard_admin, name='dashboard_admin'),
    path('reportes/pasajeros/', admin_views.reporte_pasajeros, name='reporte_pasajeros'),
    path('reportes/pasajeros/<int:vuelo_id>/', admin_views.detalle_pasajeros_vuelo, name='detalle_pasajeros_vuelo'),
    path('estadisticas/ocupacion/', admin_views.estadisticas_ocupacion, name='estadisticas_ocupacion'),
    path('api/estadisticas/', admin_views.api_estadisticas_vuelos, name='api_estadisticas'),
    path('api/actualizar-estado/', admin_views.api_actualizar_estado_vuelo, name='api_actualizar_estado'),
    
    # Test de traducciones
    path('test-translation/', views.test_translation, name='test_translation'),
] 