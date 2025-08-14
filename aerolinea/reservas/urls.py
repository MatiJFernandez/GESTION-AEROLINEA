"""
URLs para la aplicación reservas.

Este archivo define todas las rutas relacionadas con:
- Gestión de reservas
- Creación de reservas
- Gestión de boletos
- Consulta de reservas
"""

from django.urls import path
from . import views

# Namespace para la aplicación reservas
app_name = 'reservas'

urlpatterns = [
    # Gestión de reservas
    path('', views.lista_reservas, name='lista_reservas'),
    path('crear/', views.crear_reserva, name='crear_reserva'),
    path('<int:reserva_id>/', views.detalle_reserva, name='detalle_reserva'),
    path('<int:reserva_id>/editar/', views.editar_reserva, name='editar_reserva'),
    path('<int:reserva_id>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    path('<int:reserva_id>/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    
    # Gestión de boletos
    path('boletos/', views.lista_boletos, name='lista_boletos'),
    path('boletos/<int:boleto_id>/', views.detalle_boleto, name='detalle_boleto'),
    path('boletos/<int:boleto_id>/emitir/', views.emitir_boleto, name='emitir_boleto'),
    path('boletos/<int:boleto_id>/imprimir/', views.imprimir_boleto, name='imprimir_boleto'),
    
    # Búsqueda y consultas
    path('buscar/', views.buscar_reservas, name='buscar_reservas'),
    path('por-codigo/<str:codigo>/', views.reserva_por_codigo, name='reserva_por_codigo'),
    
    # API para verificar disponibilidad
    path('verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    
    # Historial de reservas por usuario
    path('mi-historial/', views.mi_historial, name='mi_historial'),
] 