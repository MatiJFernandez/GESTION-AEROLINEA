"""
Servicio para la gestión de reservas.

Este archivo implementa la capa de servicios del patrón Vista-Servicio-Repositorio.
Los servicios contienen la lógica de negocio y orquestan las operaciones.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import List
from reservas.models import Reserva
from reservas.repositories.reservas import ReservaRepository
from vuelos.repositories.vuelos import VueloRepository, AsientoRepository


class ReservaService:
    """Servicio para la gestión de reservas."""
    
    @staticmethod
    def crear_reserva(usuario_id: int, pasajero_id: int, vuelo_id: int, 
                      asiento_id: int = None, precio_final: float = None) -> Reserva:
        """
        Crea una nueva reserva con validaciones de negocio.
        
        Args:
            usuario_id (int): ID del usuario que hace la reserva
            pasajero_id (int): ID del pasajero
            vuelo_id (int): ID del vuelo
            asiento_id (int): ID del asiento (opcional)
            precio_final (float): Precio final de la reserva
            
        Returns:
            Reserva: La reserva creada
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones de negocio
        ReservaService._validar_vuelo_disponible(vuelo_id)
        ReservaService._validar_asiento_disponible(asiento_id, vuelo_id)
        ReservaService._validar_pasajero_valido(pasajero_id)
        
        # Calcular precio final si no se proporciona
        if precio_final is None:
            precio_final = ReservaService._calcular_precio_final(vuelo_id, asiento_id)
        
        # Crear reserva
        reserva = ReservaRepository.crear(
            usuario_id=usuario_id,
            pasajero_id=pasajero_id,
            vuelo_id=vuelo_id,
            asiento_id=asiento_id,
            estado='pendiente',
            precio_final=precio_final
        )
        
        # Lógica adicional post-creación
        ReservaService._procesar_reserva_creada(reserva)
        
        return reserva
    
    @staticmethod
    def obtener_reserva(reserva_id: int) -> Reserva | None:
        """
        Obtiene una reserva por su ID.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva: Reserva encontrada o None
        """
        return ReservaRepository.obtener_por_id(reserva_id)
    
    @staticmethod
    def obtener_reserva_con_detalles(reserva_id: int) -> Reserva | None:
        """
        Obtiene una reserva con todos sus detalles.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva: Reserva con detalles
        """
        return ReservaRepository.obtener_con_detalles(reserva_id)
    
    @staticmethod
    def obtener_reservas_usuario(usuario_id: int) -> List[Reserva]:
        """
        Obtiene las reservas de un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            List[Reserva]: Reservas del usuario
        """
        return ReservaRepository.obtener_por_usuario(usuario_id)
    
    @staticmethod
    def buscar_reservas(criterios: dict = None) -> List[Reserva]:
        """
        Busca reservas por criterios.
        
        Args:
            criterios (dict): Criterios de búsqueda
            
        Returns:
            List[Reserva]: Reservas que cumplen los criterios
        """
        if criterios:
            return ReservaRepository.buscar_por_criterios(criterios)
        else:
            return ReservaRepository.obtener_reservas_activas()
    
    @staticmethod
    def confirmar_reserva(reserva_id: int) -> Reserva | None:
        """
        Confirma una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva: Reserva confirmada
            
        Raises:
            ValidationError: Si la reserva no puede ser confirmada
        """
        # Validar que la reserva existe
        reserva = ReservaRepository.obtener_por_id(reserva_id)
        if not reserva:
            raise ValidationError("Reserva no encontrada")
        
        # Validar que puede ser confirmada
        ReservaService._validar_puede_confirmar(reserva)
        
        # Confirmar reserva
        return ReservaRepository.actualizar(reserva, estado='confirmada')
    
    @staticmethod
    def cancelar_reserva(reserva_id: int) -> Reserva | None:
        """
        Cancela una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva: Reserva cancelada
            
        Raises:
            ValidationError: Si la reserva no puede ser cancelada
        """
        # Validar que la reserva existe
        reserva = ReservaRepository.obtener_por_id(reserva_id)
        if not reserva:
            raise ValidationError("Reserva no encontrada")
        
        # Validar que puede ser cancelada
        ReservaService._validar_puede_cancelar(reserva)
        
        # Cancelar reserva
        return ReservaRepository.actualizar(reserva, estado='cancelada')
    
    @staticmethod
    def actualizar_reserva(reserva_id: int, **datos_actualizacion) -> Reserva | None:
        """
        Actualiza una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Reserva: Reserva actualizada
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validar que la reserva existe
        reserva = ReservaRepository.obtener_por_id(reserva_id)
        if not reserva:
            raise ValidationError("Reserva no encontrada")
        
        # Validar datos de actualización
        ReservaService._validar_datos_actualizacion(datos_actualizacion)
        
        # Actualizar reserva
        return ReservaRepository.actualizar(reserva, **datos_actualizacion)
    
    @staticmethod
    def eliminar_reserva(reserva_id: int) -> bool:
        """
        Elimina una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ValidationError: Si la reserva no puede ser eliminada
        """
        # Validar que la reserva existe
        reserva = ReservaRepository.obtener_por_id(reserva_id)
        if not reserva:
            raise ValidationError("Reserva no encontrada")
        
        # Validar que puede ser eliminada
        ReservaService._validar_puede_eliminar(reserva)
        
        # Eliminar reserva
        return ReservaRepository.eliminar(reserva_id)
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """
        Obtiene estadísticas de reservas.
        
        Returns:
            dict: Estadísticas de reservas
        """
        return ReservaRepository.obtener_estadisticas()
    
    @staticmethod
    def limpiar_reservas_expiradas() -> int:
        """
        Limpia las reservas expiradas.
        
        Returns:
            int: Número de reservas limpiadas
        """
        reservas_expiradas = ReservaRepository.obtener_reservas_expiradas()
        count = len(reservas_expiradas)
        
        for reserva in reservas_expiradas:
            ReservaRepository.actualizar(reserva, estado='expirada')
        
        return count
    
    @staticmethod
    def _validar_vuelo_disponible(vuelo_id: int):
        """Valida que el vuelo esté disponible."""
        vuelo = VueloRepository.obtener_por_id(vuelo_id)
        if not vuelo:
            raise ValidationError("Vuelo no encontrado")
        
        if vuelo.estado != 'programado':
            raise ValidationError("El vuelo no está disponible para reservas")
        
        if vuelo.fecha_salida <= timezone.now():
            raise ValidationError("El vuelo ya ha partido")
    
    @staticmethod
    def _validar_asiento_disponible(asiento_id: int, vuelo_id: int):
        """Valida que el asiento esté disponible."""
        if asiento_id:
            if AsientoRepository.esta_reservado_para_vuelo(asiento_id, vuelo_id):
                raise ValidationError("El asiento ya está reservado para este vuelo")
    
    @staticmethod
    def _validar_pasajero_valido(pasajero_id: int):
        """Valida que el pasajero sea válido."""
        from pasajeros.repositories.pasajeros import PasajeroRepository
        pasajero = PasajeroRepository.obtener_por_id(pasajero_id)
        if not pasajero:
            raise ValidationError("Pasajero no encontrado")
    
    @staticmethod
    def _calcular_precio_final(vuelo_id: int, asiento_id: int = None) -> float:
        """Calcula el precio final de la reserva."""
        vuelo = VueloRepository.obtener_por_id(vuelo_id)
        if not vuelo:
            raise ValidationError("Vuelo no encontrado")
        
        precio_final = vuelo.precio_base
        
        # Aplicar recargos por clase de asiento si se especifica
        if asiento_id:
            asiento = AsientoRepository.obtener_por_id(asiento_id)
            if asiento:
                from decimal import Decimal
                if asiento.clase == 'primera':
                    precio_final *= Decimal('2.5')
                elif asiento.clase == 'business':
                    precio_final *= Decimal('1.8')
                elif asiento.clase == 'economica':
                    precio_final *= Decimal('1.0')
        
        return precio_final
    
    @staticmethod
    def _validar_puede_confirmar(reserva: Reserva):
        """Valida que la reserva pueda ser confirmada."""
        if reserva.estado != 'pendiente':
            raise ValidationError("Solo se pueden confirmar reservas pendientes")
        
        vuelo = VueloRepository.obtener_por_id(reserva.vuelo_id)
        if vuelo.fecha_salida <= timezone.now():
            raise ValidationError("No se puede confirmar una reserva para un vuelo que ya partió")
    
    @staticmethod
    def _validar_puede_cancelar(reserva: Reserva):
        """Valida que la reserva pueda ser cancelada."""
        if reserva.estado in ['cancelada', 'expirada']:
            raise ValidationError("La reserva ya está cancelada o expirada")
        
        vuelo = VueloRepository.obtener_por_id(reserva.vuelo_id)
        if vuelo.fecha_salida <= timezone.now():
            raise ValidationError("No se puede cancelar una reserva para un vuelo que ya partió")
    
    @staticmethod
    def _validar_puede_eliminar(reserva: Reserva):
        """Valida que la reserva pueda ser eliminada."""
        if reserva.estado == 'confirmada':
            raise ValidationError("No se puede eliminar una reserva confirmada")
    
    @staticmethod
    def _validar_datos_actualizacion(datos: dict):
        """Valida los datos de actualización."""
        if 'estado' in datos:
            estados_validos = ['pendiente', 'confirmada', 'cancelada', 'expirada']
            if datos['estado'] not in estados_validos:
                raise ValidationError("Estado de reserva no válido")
    
    @staticmethod
    def _procesar_reserva_creada(reserva: Reserva):
        """Procesa acciones adicionales después de crear una reserva."""
        # Aquí se pueden agregar acciones como:
        # - Enviar email de confirmación
        # - Actualizar estadísticas
        # - Notificar al sistema de pagos
        pass 