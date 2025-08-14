"""
Repositorio para la gestión de reservas.

Este archivo implementa la capa de repositorios del patrón Vista-Servicio-Repositorio.
Los repositorios manejan el acceso a datos y las consultas a la base de datos.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import timezone
from reservas.models import Reserva


class ReservaRepository:
    """Repositorio para la gestión de reservas."""
    
    @staticmethod
    def crear(usuario_id: int, pasajero_id: int, vuelo_id: int, asiento_id: int = None,
              estado: str = 'pendiente', precio_final: float = None) -> Reserva:
        """
        Crea una nueva reserva.
        
        Args:
            usuario_id (int): ID del usuario que hace la reserva
            pasajero_id (int): ID del pasajero
            vuelo_id (int): ID del vuelo
            asiento_id (int): ID del asiento (opcional)
            estado (str): Estado de la reserva
            precio_final (float): Precio final de la reserva
            
        Returns:
            Reserva: Reserva creada
        """
        return Reserva.objects.create(
            usuario_id=usuario_id,
            pasajero_id=pasajero_id,
            vuelo_id=vuelo_id,
            asiento_id=asiento_id,
            estado=estado,
            precio_final=precio_final
        )
    
    @staticmethod
    def obtener_por_id(reserva_id: int) -> Reserva | None:
        """
        Obtiene una reserva por su ID.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva: Reserva encontrada o None
        """
        try:
            return Reserva.objects.get(id=reserva_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_con_detalles(reserva_id: int) -> Reserva | None:
        """
        Obtiene una reserva con todas sus relaciones cargadas.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            Reserva: Reserva con relaciones
        """
        try:
            return Reserva.objects.select_related(
                'pasajero', 'vuelo', 'asiento', 'usuario'
            ).get(id=reserva_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_por_usuario(usuario_id: int) -> list[Reserva]:
        """
        Obtiene las reservas de un usuario.
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            list[Reserva]: Reservas del usuario
        """
        return list(Reserva.objects.filter(usuario_id=usuario_id).select_related(
            'pasajero', 'vuelo', 'asiento'
        ).order_by('-fecha_creacion'))
    
    @staticmethod
    def obtener_por_pasajero(pasajero_id: int) -> list[Reserva]:
        """
        Obtiene las reservas de un pasajero.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            list[Reserva]: Reservas del pasajero
        """
        return list(Reserva.objects.filter(pasajero_id=pasajero_id).select_related(
            'vuelo', 'asiento', 'usuario'
        ).order_by('-fecha_creacion'))
    
    @staticmethod
    def obtener_por_vuelo(vuelo_id: int) -> list[Reserva]:
        """
        Obtiene las reservas de un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            list[Reserva]: Reservas del vuelo
        """
        return list(Reserva.objects.filter(vuelo_id=vuelo_id).select_related(
            'pasajero', 'asiento', 'usuario'
        ).order_by('fecha_creacion'))
    
    @staticmethod
    def buscar_por_criterios(criterios: dict) -> list[Reserva]:
        """
        Busca reservas por múltiples criterios.
        
        Args:
            criterios (dict): Criterios de búsqueda
            
        Returns:
            list[Reserva]: Reservas que cumplen los criterios
        """
        queryset = Reserva.objects.select_related(
            'pasajero', 'vuelo', 'asiento', 'usuario'
        )
        
        if criterios.get('usuario_id'):
            queryset = queryset.filter(usuario_id=criterios['usuario_id'])
        
        if criterios.get('pasajero_id'):
            queryset = queryset.filter(pasajero_id=criterios['pasajero_id'])
        
        if criterios.get('vuelo_id'):
            queryset = queryset.filter(vuelo_id=criterios['vuelo_id'])
        
        if criterios.get('estado'):
            queryset = queryset.filter(estado=criterios['estado'])
        
        if criterios.get('fecha_desde'):
            queryset = queryset.filter(fecha_creacion__date__gte=criterios['fecha_desde'])
        
        if criterios.get('fecha_hasta'):
            queryset = queryset.filter(fecha_creacion__date__lte=criterios['fecha_hasta'])
        
        if criterios.get('query'):
            query = criterios['query']
            queryset = queryset.filter(
                Q(pasajero__nombre__icontains=query) |
                Q(pasajero__apellido__icontains=query) |
                Q(vuelo__origen__icontains=query) |
                Q(vuelo__destino__icontains=query)
            )
        
        return list(queryset.order_by('-fecha_creacion'))
    
    @staticmethod
    def obtener_reservas_activas() -> list[Reserva]:
        """
        Obtiene las reservas activas (confirmadas).
        
        Returns:
            list[Reserva]: Reservas activas
        """
        return list(Reserva.objects.filter(estado='confirmada').select_related(
            'pasajero', 'vuelo', 'asiento', 'usuario'
        ).order_by('-fecha_creacion'))
    
    @staticmethod
    def obtener_reservas_expiradas() -> list[Reserva]:
        """
        Obtiene las reservas expiradas.
        
        Returns:
            list[Reserva]: Reservas expiradas
        """
        return list(Reserva.objects.filter(
            vuelo__fecha_salida__lt=timezone.now(),
            estado__in=['pendiente', 'confirmada']
        ).select_related('pasajero', 'vuelo', 'asiento', 'usuario'))
    
    @staticmethod
    def actualizar(reserva: Reserva, **datos_actualizacion) -> Reserva:
        """
        Actualiza una reserva.
        
        Args:
            reserva (Reserva): Reserva a actualizar
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Reserva: Reserva actualizada
        """
        for campo, valor in datos_actualizacion.items():
            setattr(reserva, campo, valor)
        reserva.save()
        return reserva
    
    @staticmethod
    def eliminar(reserva_id: int) -> bool:
        """
        Elimina una reserva.
        
        Args:
            reserva_id (int): ID de la reserva
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        try:
            reserva = Reserva.objects.get(id=reserva_id)
            reserva.delete()
            return True
        except ObjectDoesNotExist:
            return False
    
    @staticmethod
    def contar_por_estado() -> dict:
        """
        Cuenta las reservas por estado.
        
        Returns:
            dict: Conteo de reservas por estado
        """
        conteo = Reserva.objects.values('estado').annotate(
            total=models.Count('id')
        )
        return {item['estado']: item['total'] for item in conteo}
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """
        Obtiene estadísticas de reservas.
        
        Returns:
            dict: Estadísticas de reservas
        """
        return {
            'total': Reserva.objects.count(),
            'confirmadas': Reserva.objects.filter(estado='confirmada').count(),
            'pendientes': Reserva.objects.filter(estado='pendiente').count(),
            'canceladas': Reserva.objects.filter(estado='cancelada').count(),
            'expiradas': ReservaRepository.obtener_reservas_expiradas().__len__(),
        } 