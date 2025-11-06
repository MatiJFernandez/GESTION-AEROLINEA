"""
Manejo personalizado de excepciones para la API REST.

Este archivo define cómo manejar diferentes tipos de errores HTTP.
"""

from rest_framework.views import exception_handler
from rest_framework import status
from django.http import Http404
from rest_framework.exceptions import PermissionDenied, NotAuthenticated


def custom_exception_handler(exc, context):
    """
    Handler personalizado para excepciones de la API.
    
    Proporciona respuestas de error más consistentes y detalladas.
    """
    # Llamar al handler por defecto de DRF
    response = exception_handler(exc, context)
    
    # No modificar respuestas de autenticación JWT
    if context and 'view' in context:
        view = context['view']
        if hasattr(view, '__class__'):
            view_class_name = view.__class__.__name__
            # Permitir que las vistas de token manejen sus propios errores
            if 'Token' in view_class_name:
                return response
    
    # Personalizar la respuesta
    if response is not None:
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': None,
            'details': None,
        }
        
        custom_response_data['message'] = response.data.get('detail', 'Error desconocido')
        
        # Si hay múltiples errores (ej: validación de serializer)
        if isinstance(response.data, dict) and 'detail' not in response.data:
            custom_response_data['message'] = 'Error de validación'
            custom_response_data['details'] = response.data
        
        # Mensajes personalizados según el tipo de error
        if response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'Recurso no encontrado'
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Solicitud inválida'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'No autenticado. Token inválido o faltante'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'Sin permisos para realizar esta acción'
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            custom_response_data['message'] = 'Error interno del servidor'
        
        response.data = custom_response_data
    
    return response

