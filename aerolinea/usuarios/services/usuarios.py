"""
Servicio para la gestión de usuarios.

Este archivo implementa la capa de servicios del patrón Vista-Servicio-Repositorio.
Los servicios contienen la lógica de negocio y orquestan las operaciones.
"""

from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from typing import List
from usuarios.models import Perfil
from usuarios.repositories.usuarios import UsuarioRepository, PerfilRepository


class UsuarioService:
    """Servicio para la gestión de usuarios."""
    
    @staticmethod
    def registrar_usuario(username: str, password: str, email: str, first_name: str = None, 
                         last_name: str = None) -> User:
        """
        Registra un nuevo usuario con validaciones de negocio.
        
        Args:
            username (str): Username del usuario
            password (str): Contraseña del usuario
            email (str): Email del usuario
            first_name (str): Nombre del usuario (opcional)
            last_name (str): Apellido del usuario (opcional)
            
        Returns:
            User: El usuario creado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones de negocio
        UsuarioService._validar_datos_usuario(username, password, email)
        UsuarioService._validar_username_unico(username)
        UsuarioService._validar_email_unico(email)
        
        # Crear usuario
        usuario = UsuarioRepository.crear_usuario(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        
        # Lógica adicional post-creación
        UsuarioService._procesar_usuario_creado(usuario)
        
        return usuario
    
    @staticmethod
    def autenticar_usuario(username: str, password: str) -> User | None:
        """
        Autentica un usuario.
        
        Args:
            username (str): Username del usuario
            password (str): Contraseña del usuario
            
        Returns:
            User: Usuario autenticado o None
        """
        return UsuarioRepository.verificar_credenciales(username, password)
    
    @staticmethod
    def obtener_usuario(usuario_id: int) -> User | None:
        """
        Obtiene un usuario por su ID.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            User: Usuario encontrado o None
        """
        return UsuarioRepository.obtener_por_id(usuario_id)
    
    @staticmethod
    def buscar_usuarios(criterios: dict = None) -> List[User]:
        """
        Busca usuarios por criterios.
        
        Args:
            criterios (dict): Criterios de búsqueda
            
        Returns:
            List[User]: Usuarios que cumplen los criterios
        """
        if criterios:
            return UsuarioRepository.buscar_por_criterios(criterios)
        else:
            return UsuarioRepository.obtener_todos()
    
    @staticmethod
    def actualizar_usuario(usuario_id: int, **datos_actualizacion) -> User | None:
        """
        Actualiza un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            User: Usuario actualizado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validar que el usuario existe
        usuario = UsuarioRepository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValidationError("Usuario no encontrado")
        
        # Validar datos de actualización
        UsuarioService._validar_datos_actualizacion(datos_actualizacion)
        
        # Actualizar usuario
        return UsuarioRepository.actualizar(usuario, **datos_actualizacion)
    
    @staticmethod
    def cambiar_password(usuario_id: int, password_actual: str, nueva_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            password_actual (str): Contraseña actual
            nueva_password (str): Nueva contraseña
            
        Returns:
            bool: True si se cambió correctamente
            
        Raises:
            ValidationError: Si la contraseña actual es incorrecta
        """
        # Validar que el usuario existe
        usuario = UsuarioRepository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValidationError("Usuario no encontrado")
        
        # Validar contraseña actual
        if not usuario.check_password(password_actual):
            raise ValidationError("La contraseña actual es incorrecta")
        
        # Validar nueva contraseña
        UsuarioService._validar_password(nueva_password)
        
        # Cambiar contraseña
        return UsuarioRepository.cambiar_password(usuario_id, nueva_password)
    
    @staticmethod
    def eliminar_usuario(usuario_id: int) -> bool:
        """
        Elimina un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ValidationError: Si el usuario no existe
        """
        # Validar que el usuario existe
        usuario = UsuarioRepository.obtener_por_id(usuario_id)
        if not usuario:
            raise ValidationError("Usuario no encontrado")
        
        # Eliminar usuario
        return UsuarioRepository.eliminar(usuario_id)
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """
        Obtiene estadísticas de usuarios.
        
        Returns:
            dict: Estadísticas de usuarios
        """
        return UsuarioRepository.obtener_estadisticas()
    
    @staticmethod
    def _validar_datos_usuario(username: str, password: str, email: str):
        """Valida los datos del usuario."""
        # Validar campos obligatorios
        if not username:
            raise ValidationError("El username es obligatorio")
        if not password:
            raise ValidationError("La contraseña es obligatoria")
        if not email:
            raise ValidationError("El email es obligatorio")
        
        # Validar longitud del username
        if len(username) < 3:
            raise ValidationError("El username debe tener al menos 3 caracteres")
        
        # Validar longitud de la contraseña
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        # Validar email
        from django.core.validators import validate_email
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("El formato del email no es válido")
    
    @staticmethod
    def _validar_username_unico(username: str):
        """Valida que el username sea único."""
        if UsuarioRepository.obtener_por_username(username):
            raise ValidationError("Ya existe un usuario con este username")
    
    @staticmethod
    def _validar_email_unico(email: str):
        """Valida que el email sea único."""
        if email and UsuarioRepository.obtener_por_email(email):
            raise ValidationError("Ya existe un usuario con este email")
    
    @staticmethod
    def _validar_datos_actualizacion(datos: dict):
        """Valida los datos de actualización."""
        if 'email' in datos and datos['email']:
            from django.core.validators import validate_email
            try:
                validate_email(datos['email'])
            except ValidationError:
                raise ValidationError("El formato del email no es válido")
    
    @staticmethod
    def _validar_password(password: str):
        """Valida la contraseña."""
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        # Validar que contenga al menos una letra y un número
        if not any(c.isalpha() for c in password):
            raise ValidationError("La contraseña debe contener al menos una letra")
        
        if not any(c.isdigit() for c in password):
            raise ValidationError("La contraseña debe contener al menos un número")
    
    @staticmethod
    def _procesar_usuario_creado(usuario: User):
        """Procesa acciones adicionales después de crear un usuario."""
        # Aquí se pueden agregar acciones como:
        # - Enviar email de bienvenida
        # - Crear perfil por defecto
        # - Asignar permisos por defecto
        pass


class PerfilService:
    """Servicio para la gestión de perfiles."""
    
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
        return PerfilRepository.crear_perfil(
            usuario=usuario,
            telefono=telefono,
            direccion=direccion,
            fecha_nacimiento=fecha_nacimiento
        )
    
    @staticmethod
    def obtener_perfil_usuario(usuario: User) -> Perfil | None:
        """
        Obtiene el perfil de un usuario.
        
        Args:
            usuario (User): Usuario del perfil
            
        Returns:
            Perfil: Perfil encontrado o None
        """
        return PerfilRepository.obtener_por_usuario(usuario)
    
    @staticmethod
    def actualizar_perfil(perfil_id: int, **datos_actualizacion) -> Perfil | None:
        """
        Actualiza un perfil.
        
        Args:
            perfil_id (int): ID del perfil
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Perfil: Perfil actualizado
        """
        perfil = PerfilRepository.obtener_por_id(perfil_id)
        if not perfil:
            return None
        
        return PerfilRepository.actualizar(perfil, **datos_actualizacion) 