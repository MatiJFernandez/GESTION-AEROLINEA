"""
Decoradores personalizados para el sistema de autenticación.

Este módulo contiene decoradores para manejar permisos específicos
por rol de usuario y validaciones de acceso.
"""

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps


def staff_required(view_func):
    """
    Decorador que requiere que el usuario sea staff.
    
    Redirige a usuarios no autorizados con un mensaje informativo.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
        
        if not request.user.is_staff:
            messages.error(request, 'No tienes permisos para acceder a esta página.')
            return redirect('vuelos:home')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(allowed_roles):
    """
    Decorador que requiere un rol específico.
    
    Args:
        allowed_roles: Lista de roles permitidos (ej: ['admin', 'empleado'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('usuarios:login')
            
            if request.user.rol not in allowed_roles:
                messages.error(request, f'Tu rol ({request.user.get_rol_display()}) no tiene permisos para esta acción.')
                return redirect('vuelos:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def owner_required(model_class, pk_name='pk'):
    """
    Decorador que requiere que el usuario sea el propietario del objeto.
    
    Args:
        model_class: Clase del modelo a verificar
        pk_name: Nombre del parámetro que contiene la clave primaria
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('usuarios:login')
            
            # Obtener el objeto
            obj_pk = kwargs.get(pk_name)
            try:
                obj = model_class.objects.get(pk=obj_pk)
            except model_class.DoesNotExist:
                messages.error(request, 'El recurso solicitado no existe.')
                return redirect('vuelos:home')
            
            # Verificar si el usuario es el propietario o es staff
            if not request.user.is_staff and not hasattr(obj, 'usuario'):
                messages.error(request, 'No tienes permisos para acceder a este recurso.')
                return redirect('vuelos:home')
            
            if not request.user.is_staff and obj.usuario != request.user:
                messages.error(request, 'No tienes permisos para acceder a este recurso.')
                return redirect('vuelos:home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def reservation_owner_required(view_func):
    """
    Decorador específico para verificar que el usuario es propietario de una reserva.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
        
        from reservas.models import Reserva
        
        reserva_id = kwargs.get('reserva_id')
        try:
            reserva = Reserva.objects.get(pk=reserva_id)
        except Reserva.DoesNotExist:
            messages.error(request, 'La reserva solicitada no existe.')
            return redirect('reservas:lista_reservas')
        
        # Verificar si el usuario es el propietario de la reserva o es staff
        if not request.user.is_staff and reserva.pasajero.email != request.user.email:
            messages.error(request, 'No tienes permisos para acceder a esta reserva.')
            return redirect('reservas:lista_reservas')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def active_flight_required(view_func):
    """
    Decorador para verificar que un vuelo está activo (programado).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        from vuelos.models import Vuelo
        
        vuelo_id = kwargs.get('vuelo_id')
        try:
            vuelo = Vuelo.objects.get(pk=vuelo_id)
        except Vuelo.DoesNotExist:
            messages.error(request, 'El vuelo solicitado no existe.')
            return redirect('vuelos:lista_vuelos')
        
        if vuelo.estado != 'programado':
            messages.error(request, f'El vuelo {vuelo.origen} → {vuelo.destino} no está disponible para reservas.')
            return redirect('vuelos:detalle_vuelo', vuelo_id=vuelo.id)
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view 