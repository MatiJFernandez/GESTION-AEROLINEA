"""
Servicio para la gestión de pasajeros.

Este archivo implementa la capa de servicios del patrón Vista-Servicio-Repositorio.
Los servicios contienen la lógica de negocio y orquestan las operaciones.
"""

from django.core.exceptions import ValidationError
from datetime import date
from typing import List
from pasajeros.models import Pasajero
from pasajeros.repositories.pasajeros import PasajeroRepository


class PasajeroService:
    """Servicio para la gestión de pasajeros."""
    
    @staticmethod
    def crear_pasajero(nombre: str, apellido: str, tipo_documento: str, numero_documento: str,
                       fecha_nacimiento, email: str = None, telefono: str = None) -> Pasajero:
        """
        Crea un nuevo pasajero con validaciones de negocio.
        
        Args:
            nombre (str): Nombre del pasajero
            apellido (str): Apellido del pasajero
            tipo_documento (str): Tipo de documento
            numero_documento (str): Número de documento
            fecha_nacimiento: Fecha de nacimiento
            email (str): Email del pasajero (opcional)
            telefono (str): Teléfono del pasajero (opcional)
            
        Returns:
            Pasajero: El pasajero creado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones de negocio
        PasajeroService._validar_datos_pasajero(nombre, apellido, tipo_documento, numero_documento, fecha_nacimiento, email)
        PasajeroService._validar_documento_unico(tipo_documento, numero_documento)
        
        # Crear pasajero
        pasajero = PasajeroRepository.crear(
            nombre=nombre,
            apellido=apellido,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            telefono=telefono
        )
        
        # Lógica adicional post-creación
        PasajeroService._procesar_pasajero_creado(pasajero)
        
        return pasajero
    
    @staticmethod
    def obtener_pasajero(pasajero_id: int) -> Pasajero | None:
        """
        Obtiene un pasajero por su ID.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            Pasajero: Pasajero encontrado o None
        """
        return PasajeroRepository.obtener_por_id(pasajero_id)
    
    @staticmethod
    def obtener_pasajero_con_reservas(pasajero_id: int) -> Pasajero | None:
        """
        Obtiene un pasajero con sus reservas.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            Pasajero: Pasajero con reservas
        """
        return PasajeroRepository.obtener_con_reservas(pasajero_id)
    
    @staticmethod
    def buscar_pasajeros(criterios: dict = None) -> List[Pasajero]:
        """
        Busca pasajeros por criterios.
        
        Args:
            criterios (dict): Criterios de búsqueda
            
        Returns:
            List[Pasajero]: Pasajeros que cumplen los criterios
        """
        if criterios:
            return PasajeroRepository.buscar_por_criterios(criterios)
        else:
            return PasajeroRepository.obtener_todos()
    
    @staticmethod
    def buscar_por_documento(tipo_documento: str, numero_documento: str) -> Pasajero | None:
        """
        Busca un pasajero por documento.
        
        Args:
            tipo_documento (str): Tipo de documento
            numero_documento (str): Número de documento
            
        Returns:
            Pasajero: Pasajero encontrado o None
        """
        return PasajeroRepository.buscar_por_documento(tipo_documento, numero_documento)
    
    @staticmethod
    def actualizar_pasajero(pasajero_id: int, **datos_actualizacion) -> Pasajero | None:
        """
        Actualiza un pasajero.
        
        Args:
            pasajero_id (int): ID del pasajero
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Pasajero: Pasajero actualizado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validar que el pasajero existe
        pasajero = PasajeroRepository.obtener_por_id(pasajero_id)
        if not pasajero:
            raise ValidationError("Pasajero no encontrado")
        
        # Validar datos de actualización
        PasajeroService._validar_datos_actualizacion(datos_actualizacion)
        
        # Actualizar pasajero
        return PasajeroRepository.actualizar(pasajero, **datos_actualizacion)
    
    @staticmethod
    def eliminar_pasajero(pasajero_id: int) -> bool:
        """
        Elimina un pasajero.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ValidationError: Si el pasajero tiene reservas activas
        """
        # Validar que el pasajero existe
        pasajero = PasajeroRepository.obtener_por_id(pasajero_id)
        if not pasajero:
            raise ValidationError("Pasajero no encontrado")
        
        # Validar que no tenga reservas activas
        PasajeroService._validar_sin_reservas_activas(pasajero)
        
        # Eliminar pasajero
        return PasajeroRepository.eliminar(pasajero_id)
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """
        Obtiene estadísticas de pasajeros.
        
        Returns:
            dict: Estadísticas de pasajeros
        """
        return PasajeroRepository.obtener_estadisticas()
    
    @staticmethod
    def verificar_documento(tipo_documento: str, numero_documento: str) -> bool:
        """
        Verifica si un documento ya existe.
        
        Args:
            tipo_documento (str): Tipo de documento
            numero_documento (str): Número de documento
            
        Returns:
            bool: True si el documento existe
        """
        return PasajeroRepository.buscar_por_documento(tipo_documento, numero_documento) is not None
    
    @staticmethod
    def _validar_datos_pasajero(nombre: str, apellido: str, tipo_documento: str, 
                                numero_documento: str, fecha_nacimiento, email: str = None):
        """Valida los datos del pasajero."""
        # Validar campos obligatorios
        if not nombre:
            raise ValidationError("El nombre es obligatorio")
        if not apellido:
            raise ValidationError("El apellido es obligatorio")
        if not tipo_documento:
            raise ValidationError("El tipo de documento es obligatorio")
        if not numero_documento:
            raise ValidationError("El número de documento es obligatorio")
        if not fecha_nacimiento:
            raise ValidationError("La fecha de nacimiento es obligatoria")
        
        # Validar fecha de nacimiento
        if fecha_nacimiento > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser futura")
        
        # Validar edad mínima (ejemplo: 0 años)
        edad = (date.today() - fecha_nacimiento).days / 365.25
        if edad < 0:
            raise ValidationError("La edad debe ser válida")
        
        # Validar email si se proporciona
        if email:
            from django.core.validators import validate_email
            try:
                validate_email(email)
            except ValidationError:
                raise ValidationError("El formato del email no es válido")
    
    @staticmethod
    def _validar_documento_unico(tipo_documento: str, numero_documento: str):
        """Valida que el documento sea único."""
        if PasajeroRepository.buscar_por_documento(tipo_documento, numero_documento):
            raise ValidationError("Ya existe un pasajero con este documento")
    
    @staticmethod
    def _validar_datos_actualizacion(datos: dict):
        """Valida los datos de actualización."""
        if 'fecha_nacimiento' in datos:
            if datos['fecha_nacimiento'] > date.today():
                raise ValidationError("La fecha de nacimiento no puede ser futura")
        
        if 'email' in datos and datos['email']:
            from django.core.validators import validate_email
            try:
                validate_email(datos['email'])
            except ValidationError:
                raise ValidationError("El formato del email no es válido")
    
    @staticmethod
    def _validar_sin_reservas_activas(pasajero: Pasajero):
        """Valida que el pasajero no tenga reservas activas."""
        reservas_activas = pasajero.reserva_set.filter(estado='confirmada')
        if reservas_activas.exists():
            raise ValidationError("No se puede eliminar un pasajero con reservas activas")
    
    @staticmethod
    def _procesar_pasajero_creado(pasajero: Pasajero):
        """Procesa acciones adicionales después de crear un pasajero."""
        # Aquí se pueden agregar acciones como:
        # - Enviar email de bienvenida
        # - Crear perfil adicional
        # - Registrar en sistema externo
        pass 