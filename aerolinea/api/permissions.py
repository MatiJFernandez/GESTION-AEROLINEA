"""
Permisos personalizados para la API REST.

Este archivo define los permisos basados en roles de usuario.
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos pero escritura solo a administradores.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.rol == 'admin'


class IsAdminOrEmployee(permissions.BasePermission):
    """
    Permiso que permite acceso solo a administradores y empleados.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.rol in ['admin', 'empleado']


class IsAdmin(permissions.BasePermission):
    """
    Permiso que permite acceso solo a administradores.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.rol == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite acceso al dueño del objeto o a administradores.
    """
    def has_object_permission(self, request, view, obj):
        # Los administradores tienen acceso completo
        if request.user.rol == 'admin':
            return True
        
        # Los demás usuarios solo pueden ver/editar sus propios objetos
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        # Si no tiene atributo usuario, solo admins
        return False

