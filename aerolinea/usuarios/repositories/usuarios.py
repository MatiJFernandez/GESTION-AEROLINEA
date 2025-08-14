"""
Repositorio para la gestión de usuarios.

Este archivo implementa la capa de repositorios del patrón Vista-Servicio-Repositorio.
Los repositorios manejan el acceso a datos y las consultas a la base de datos.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db.models import Q
from usuarios.models import Perfil


class UsuarioRepository:
    """Repositorio para la gestión de usuarios."""
    
    @staticmethod
    def crear_usuario(username: str, password: str, email: str, first_name: str = None, 
                     last_name: str = None, is_active: bool = True) -> User:
        """
        Crea un nuevo usuario.
        
        Args:
            username (str): Username del usuario
            password (str): Contraseña del usuario
            email (str): Email del usuario
            first_name (str): Nombre del usuario (opcional)
            last_name (str): Apellido del usuario (opcional)
            is_active (bool): Si el usuario está activo
            
        Returns:
            User: Usuario creado
        """
        return User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name or '',
            last_name=last_name or '',
            is_active=is_active
        )
    
    @staticmethod
    def obtener_por_id(usuario_id: int) -> User | None:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            User: Usuario encontrado o None
        """
        try:
            return User.objects.get(id=usuario_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_por_username(username: str) -> User | None:
        """
        Obtiene un usuario por su username.
        
        Args:
            username (str): Username del usuario
            
        Returns:
            User: Usuario encontrado o None
        """
        try:
            return User.objects.get(username=username)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_por_email(email: str) -> User | None:
        """
        Obtiene un usuario por su email.
        
        Args:
            email (str): Email del usuario
            
        Returns:
            User: Usuario encontrado o None
        """
        try:
            return User.objects.get(email=email)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def buscar_por_criterios(criterios: dict) -> list[User]:
        """
        Busca usuarios por múltiples criterios.
        
        Args:
            criterios (dict): Criterios de búsqueda
            
        Returns:
            list[User]: Usuarios que cumplen los criterios
        """
        queryset = User.objects.all()
        
        if criterios.get('query'):
            query = criterios['query']
            queryset = queryset.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        
        if criterios.get('is_active') is not None:
            queryset = queryset.filter(is_active=criterios['is_active'])
        
        if criterios.get('is_staff') is not None:
            queryset = queryset.filter(is_staff=criterios['is_staff'])
        
        return list(queryset.order_by('username'))
    
    @staticmethod
    def obtener_todos() -> list[User]:
        """
        Obtiene todos los usuarios ordenados.
        
        Returns:
            list[User]: Todos los usuarios
        """
        return list(User.objects.all().order_by('username'))
    
    @staticmethod
    def actualizar(usuario: User, **datos_actualizacion) -> User:
        """
        Actualiza un usuario.
        
        Args:
            usuario (User): Usuario a actualizar
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            User: Usuario actualizado
        """
        for campo, valor in datos_actualizacion.items():
            setattr(usuario, campo, valor)
        usuario.save()
        return usuario
    
    @staticmethod
    def eliminar(usuario_id: int) -> bool:
        """
        Elimina un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        try:
            usuario = User.objects.get(id=usuario_id)
            usuario.delete()
            return True
        except ObjectDoesNotExist:
            return False
    
    @staticmethod
    def cambiar_password(usuario_id: int, nueva_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            nueva_password (str): Nueva contraseña
            
        Returns:
            bool: True si se cambió correctamente
        """
        try:
            usuario = User.objects.get(id=usuario_id)
            usuario.set_password(nueva_password)
            usuario.save()
            return True
        except ObjectDoesNotExist:
            return False
    
    @staticmethod
    def verificar_credenciales(username: str, password: str) -> User | None:
        """
        Verifica las credenciales de un usuario.
        
        Args:
            username (str): Username del usuario
            password (str): Contraseña del usuario
            
        Returns:
            User: Usuario si las credenciales son correctas, None en caso contrario
        """
        try:
            usuario = User.objects.get(username=username)
            if usuario.check_password(password):
                return usuario
            return None
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """
        Obtiene estadísticas de usuarios.
        
        Returns:
            dict: Estadísticas de usuarios
        """
        return {
            'total_usuarios': User.objects.count(),
            'usuarios_activos': User.objects.filter(is_active=True).count(),
            'usuarios_staff': User.objects.filter(is_staff=True).count(),
            'usuarios_superuser': User.objects.filter(is_superuser=True).count(),
            'perfiles_completos': Perfil.objects.count(),
        }


class PerfilRepository:
    """Repositorio para la gestión de perfiles."""
    
    @staticmethod
    def crear_perfil(usuario: User, telefono: str = None, direccion: str = None, 
                     fecha_nacimiento = None) -> Perfil:
        """
        Crea un nuevo perfil.
        
        Args:
            usuario (User): Usuario del perfil
            telefono (str): Teléfono del usuario (opcional)
            direccion (str): Dirección del usuario (opcional)
            fecha_nacimiento: Fecha de nacimiento (opcional)
            
        Returns:
            Perfil: Perfil creado
        """
        return Perfil.objects.create(
            usuario=usuario,
            telefono=telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento
        )
    
    @staticmethod
    def obtener_por_usuario(usuario: User) -> Perfil | None:
        """
        Obtiene el perfil de un usuario.
        
        Args:
            usuario (User): Usuario del perfil
            
        Returns:
            Perfil: Perfil encontrado o None
        """
        try:
            return Perfil.objects.get(usuario=usuario)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_por_id(perfil_id: int) -> Perfil | None:
        """
        Obtiene un perfil por su ID.
        
        Args:
            perfil_id (int): ID del perfil
            
        Returns:
            Perfil: Perfil encontrado o None
        """
        try:
            return Perfil.objects.get(id=perfil_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def actualizar(perfil: Perfil, **datos_actualizacion) -> Perfil:
        """
        Actualiza un perfil.
        
        Args:
            perfil (Perfil): Perfil a actualizar
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Perfil: Perfil actualizado
        """
        for campo, valor in datos_actualizacion.items():
            setattr(perfil, campo, valor)
        perfil.save()
        return perfil 