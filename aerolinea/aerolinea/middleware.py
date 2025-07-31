"""
Middleware personalizado para el sistema de aerolínea.

Este módulo contiene middleware para:
- Logging de requests
- Manejo de errores
- Validaciones de seguridad
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para loggear información de requests.
    
    Registra información sobre requests, incluyendo:
    - Método HTTP
    - URL
    - Usuario
    - Tiempo de respuesta
    - Código de estado
    """
    
    def process_request(self, request):
        """Registra información del request al inicio."""
        request.start_time = time.time()
        
        # Loggear información básica del request
        logger = logging.getLogger('django.request')
        
        user_info = 'Anónimo'
        if request.user.is_authenticated:
            user_info = f"{request.user.username} ({request.user.email})"
        
        logger.info(
            f"Request iniciado - Método: {request.method} - URL: {request.path} - "
            f"Usuario: {user_info} - IP: {self.get_client_ip(request)}"
        )
    
    def process_response(self, request, response):
        """Registra información del response al final."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            logger = logging.getLogger('django.request')
            
            user_info = 'Anónimo'
            if request.user.is_authenticated:
                user_info = f"{request.user.username} ({request.user.email})"
            
            logger.info(
                f"Request completado - Método: {request.method} - URL: {request.path} - "
                f"Usuario: {user_info} - Status: {response.status_code} - "
                f"Duración: {duration:.3f}s"
            )
        
        return response
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware para manejo centralizado de errores.
    
    Captura excepciones y las maneja de forma consistente,
    loggeando información útil para debugging.
    """
    
    def process_exception(self, request, exception):
        """Maneja excepciones no capturadas."""
        logger = logging.getLogger('django.request')
        
        user_info = 'Anónimo'
        if request.user.is_authenticated:
            user_info = f"{request.user.username} ({request.user.email})"
        
        # Loggear el error
        logger.error(
            f"Excepción no manejada - Método: {request.method} - URL: {request.path} - "
            f"Usuario: {user_info} - Error: {str(exception)} - "
            f"Tipo: {type(exception).__name__}"
        )
        
        # Manejar diferentes tipos de excepciones
        if isinstance(exception, ValidationError):
            return JsonResponse({
                'error': 'Error de validación',
                'details': exception.messages
            }, status=400)
        
        elif isinstance(exception, IntegrityError):
            return JsonResponse({
                'error': 'Error de integridad de datos',
                'details': 'Los datos proporcionados violan las restricciones de la base de datos.'
            }, status=400)
        
        elif isinstance(exception, PermissionError):
            return JsonResponse({
                'error': 'Error de permisos',
                'details': 'No tienes permisos para realizar esta acción.'
            }, status=403)
        
        # Para otros tipos de errores, retornar error genérico
        return JsonResponse({
            'error': 'Error interno del servidor',
            'details': 'Ha ocurrido un error inesperado. Por favor, inténtalo de nuevo.'
        }, status=500)


class SecurityMiddleware(MiddlewareMixin):
    """
    Middleware para validaciones de seguridad básicas.
    
    Implementa validaciones de seguridad como:
    - Headers de seguridad
    - Validación de contenido
    - Protección contra ataques básicos
    """
    
    def process_request(self, request):
        """Aplica validaciones de seguridad al request."""
        # Loggear requests sospechosos
        logger = logging.getLogger('django.security')
        
        # Verificar headers de seguridad
        if self.is_suspicious_request(request):
            user_info = 'Anónimo'
            if request.user.is_authenticated:
                user_info = f"{request.user.username} ({request.user.email})"
            
            logger.warning(
                f"Request sospechoso detectado - Método: {request.method} - "
                f"URL: {request.path} - Usuario: {user_info} - "
                f"IP: {self.get_client_ip(request)}"
            )
        
        return None
    
    def process_response(self, request, response):
        """Añade headers de seguridad al response."""
        # Headers de seguridad básicos
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    def is_suspicious_request(self, request):
        """Detecta requests potencialmente sospechosos."""
        suspicious_patterns = [
            'script',
            'javascript:',
            'data:text/html',
            'vbscript:',
            'onload=',
            'onerror=',
        ]
        
        # Verificar en URL
        url_lower = request.path.lower()
        for pattern in suspicious_patterns:
            if pattern in url_lower:
                return True
        
        # Verificar en parámetros GET
        for key, value in request.GET.items():
            if any(pattern in str(value).lower() for pattern in suspicious_patterns):
                return True
        
        # Verificar en parámetros POST
        for key, value in request.POST.items():
            if any(pattern in str(value).lower() for pattern in suspicious_patterns):
                return True
        
        return False
    
    def get_client_ip(self, request):
        """Obtiene la IP real del cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 