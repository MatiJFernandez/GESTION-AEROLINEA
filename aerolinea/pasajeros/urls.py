"""
URLs para la aplicación pasajeros.

Este archivo define todas las rutas relacionadas con:
- Gestión de pasajeros
- Registro de pasajeros
- Consulta de información de pasajeros
"""

from django.urls import path
from . import views

# Namespace para la aplicación pasajeros
app_name = 'pasajeros'

urlpatterns = [
    # Gestión de pasajeros
    path(
        route='', 
        view=views.PasajeroList.as_view(), 
        name='lista_pasajeros'
    ),
    path(
        route='registro/', 
        view=views.PasajeroCreate.as_view(), 
        name='registro_pasajero'
    ),
    path(
        route='<int:pasajero_id>/', 
        view=views.PasajeroDetail.as_view(), 
        name='detalle_pasajero'
    ),
    path(
        route='<int:pasajero_id>/editar/', 
        view=views.PasajeroUpdate.as_view(), 
        name='editar_pasajero'
    ),
    path(
        route='<int:pasajero_id>/eliminar/', 
        view=views.PasajeroDelete.as_view(), 
        name='eliminar_pasajero'
    ),
    
    # Búsqueda de pasajeros
    path(
        route='buscar/', 
        view=views.PasajeroSearch.as_view(), 
        name='buscar_pasajeros'
    ),
    
    # API para verificar documento
    path(
        route='verificar-documento/', 
        view=views.VerificarDocumento.as_view(), 
        name='verificar_documento'
    ),
] 