"""
Repositorio para la gestión de vuelos.

Este archivo implementa la capa de repositorios del patrón Vista-Servicio-Repositorio.
Los repositorios manejan el acceso a datos y las consultas a la base de datos.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from vuelos.models import Vuelo, Avion, Asiento


class VueloRepository:
    """Repositorio para la gestión de vuelos."""
    
    @staticmethod
    def crear(origen: str, destino: str, fecha_salida, fecha_llegada, 
              precio_base: float, avion_id: int, estado: str = 'programado') -> Vuelo:
        """
        Crea un nuevo vuelo.
        
        Args:
            origen (str): Ciudad de origen
            destino (str): Ciudad de destino
            fecha_salida: Fecha y hora de salida
            fecha_llegada: Fecha y hora de llegada
            precio_base (float): Precio base del vuelo
            avion_id (int): ID del avión
            estado (str): Estado del vuelo
            
        Returns:
            Vuelo: Vuelo creado
        """
        return Vuelo.objects.create(
            origen=origen,
            destino=destino,
            fecha_salida=fecha_salida,
            fecha_llegada=fecha_llegada,
            precio_base=precio_base,
            avion_id=avion_id,
            estado=estado
        )
    
    @staticmethod
    def obtener_por_id(vuelo_id: int) -> Vuelo | None:
        """
        Obtiene un vuelo por su ID.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            Vuelo: Vuelo encontrado o None
        """
        try:
            return Vuelo.objects.get(id=vuelo_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_con_detalles(vuelo_id: int) -> Vuelo | None:
        """
        Obtiene un vuelo con todas sus relaciones cargadas.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            Vuelo: Vuelo con relaciones
        """
        try:
            return Vuelo.objects.select_related('avion').get(id=vuelo_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def buscar_disponibles(filtros: dict = None) -> list[Vuelo]:
        """
        Busca vuelos disponibles con filtros.
        
        Args:
            filtros (dict): Filtros de búsqueda
            
        Returns:
            list[Vuelo]: Vuelos disponibles
        """
        queryset = Vuelo.objects.select_related('avion').filter(estado='programado')
        
        if filtros:
            if filtros.get('origen'):
                queryset = queryset.filter(origen__icontains=filtros['origen'])
            
            if filtros.get('destino'):
                queryset = queryset.filter(destino__icontains=filtros['destino'])
            
            if filtros.get('fecha_desde'):
                queryset = queryset.filter(fecha_salida__date__gte=filtros['fecha_desde'])
            
            if filtros.get('fecha_hasta'):
                queryset = queryset.filter(fecha_salida__date__lte=filtros['fecha_hasta'])
            
            if filtros.get('precio_min'):
                queryset = queryset.filter(precio_base__gte=filtros['precio_min'])
            
            if filtros.get('precio_max'):
                queryset = queryset.filter(precio_base__lte=filtros['precio_max'])
        
        return list(queryset.order_by('fecha_salida'))
    
    @staticmethod
    def buscar_por_avion_y_fecha(avion_id: int, fecha_salida) -> list[Vuelo]:
        """
        Busca vuelos por avión y fecha.
        
        Args:
            avion_id (int): ID del avión
            fecha_salida: Fecha de salida
            
        Returns:
            list[Vuelo]: Vuelos encontrados
        """
        return list(Vuelo.objects.filter(
            avion_id=avion_id,
            fecha_salida__date=fecha_salida.date()
        ).order_by('fecha_salida'))
    
    @staticmethod
    def obtener_proximos_vuelos(limite: int = 5) -> list[Vuelo]:
        """
        Obtiene los próximos vuelos.
        
        Args:
            limite (int): Número máximo de vuelos a obtener
            
        Returns:
            list[Vuelo]: Próximos vuelos
        """
        return list(Vuelo.objects.filter(
            fecha_salida__gt=timezone.now(),
            estado='programado'
        ).select_related('avion').order_by('fecha_salida')[:limite])
    
    @staticmethod
    def actualizar(vuelo: Vuelo, **datos_actualizacion) -> Vuelo:
        """
        Actualiza un vuelo.
        
        Args:
            vuelo (Vuelo): Vuelo a actualizar
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Vuelo: Vuelo actualizado
        """
        for campo, valor in datos_actualizacion.items():
            setattr(vuelo, campo, valor)
        vuelo.save()
        return vuelo
    
    @staticmethod
    def eliminar(vuelo_id: int) -> bool:
        """
        Elimina un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        try:
            vuelo = Vuelo.objects.get(id=vuelo_id)
            vuelo.delete()
            return True
        except ObjectDoesNotExist:
            return False


class AvionRepository:
    """Repositorio para la gestión de aviones."""
    
    @staticmethod
    def crear(modelo: str, capacidad: int, estado: str = 'activo') -> Avion:
        """
        Crea un nuevo avión.
        
        Args:
            modelo (str): Modelo del avión
            capacidad (int): Capacidad de pasajeros
            estado (str): Estado del avión
            
        Returns:
            Avion: Avión creado
        """
        return Avion.objects.create(
            modelo=modelo,
            capacidad=capacidad,
            estado=estado
        )
    
    @staticmethod
    def obtener_por_id(avion_id: int) -> Avion | None:
        """
        Obtiene un avión por su ID.
        
        Args:
            avion_id (int): ID del avión
            
        Returns:
            Avion: Avión encontrado o None
        """
        try:
            return Avion.objects.get(id=avion_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def buscar_activos() -> list[Avion]:
        """
        Busca aviones activos.
        
        Returns:
            list[Avion]: Aviones activos
        """
        return list(Avion.objects.filter(estado='activo').order_by('modelo'))
    
    @staticmethod
    def buscar_por_modelo(modelo: str) -> list[Avion]:
        """
        Busca aviones por modelo.
        
        Args:
            modelo (str): Modelo del avión
            
        Returns:
            list[Avion]: Aviones encontrados
        """
        return list(Avion.objects.filter(modelo__icontains=modelo).order_by('modelo'))
    
    @staticmethod
    def obtener_con_asientos(avion_id: int) -> Avion | None:
        """
        Obtiene un avión con sus asientos.
        
        Args:
            avion_id (int): ID del avión
            
        Returns:
            Avion: Avión con asientos
        """
        try:
            return Avion.objects.prefetch_related('asiento_set').get(id=avion_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def actualizar(avion: Avion, **datos_actualizacion) -> Avion:
        """
        Actualiza un avión.
        
        Args:
            avion (Avion): Avión a actualizar
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Avion: Avión actualizado
        """
        for campo, valor in datos_actualizacion.items():
            setattr(avion, campo, valor)
        avion.save()
        return avion


class AsientoRepository:
    """Repositorio para la gestión de asientos."""
    
    @staticmethod
    def crear(avion_id: int, numero: str, fila: int, columna: str, 
              clase: str = 'economica', estado: str = 'disponible') -> Asiento:
        """
        Crea un nuevo asiento.
        
        Args:
            avion_id (int): ID del avión
            numero (str): Número del asiento
            fila (int): Fila del asiento
            columna (str): Columna del asiento
            clase (str): Clase del asiento
            estado (str): Estado del asiento
            
        Returns:
            Asiento: Asiento creado
        """
        return Asiento.objects.create(
            avion_id=avion_id,
            numero=numero,
            fila=fila,
            columna=columna,
            clase=clase,
            estado=estado
        )
    
    @staticmethod
    def obtener_por_id(asiento_id: int) -> Asiento | None:
        """
        Obtiene un asiento por su ID.
        
        Args:
            asiento_id (int): ID del asiento
            
        Returns:
            Asiento: Asiento encontrado o None
        """
        try:
            return Asiento.objects.get(id=asiento_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_por_avion(avion_id: int) -> list[Asiento]:
        """
        Obtiene los asientos de un avión.
        
        Args:
            avion_id (int): ID del avión
            
        Returns:
            list[Asiento]: Asientos del avión
        """
        return list(Asiento.objects.filter(avion_id=avion_id).order_by('fila', 'columna'))
    
    @staticmethod
    def buscar_disponibles_por_vuelo(vuelo_id: int) -> list[Asiento]:
        """
        Busca asientos disponibles para un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            list[Asiento]: Asientos disponibles
        """
        vuelo = VueloRepository.obtener_por_id(vuelo_id)
        if not vuelo:
            return []
        
        # Obtener asientos del avión que no estén reservados para este vuelo
        asientos_avion = AsientoRepository.obtener_por_avion(vuelo.avion_id)
        asientos_reservados = set()
        
        # Obtener asientos ya reservados para este vuelo
        from reservas.models import Reserva
        reservas_vuelo = Reserva.objects.filter(vuelo_id=vuelo_id, estado__in=['confirmada', 'pendiente'])
        for reserva in reservas_vuelo:
            if reserva.asiento:
                asientos_reservados.add(reserva.asiento_id)
        
        # Filtrar asientos disponibles
        asientos_disponibles = [asiento for asiento in asientos_avion if asiento.id not in asientos_reservados]
        
        return asientos_disponibles
    
    @staticmethod
    def esta_reservado_para_vuelo(asiento_id: int, vuelo_id: int) -> bool:
        """
        Verifica si un asiento está reservado para un vuelo.
        
        Args:
            asiento_id (int): ID del asiento
            vuelo_id (int): ID del vuelo
            
        Returns:
            bool: True si está reservado
        """
        from reservas.models import Reserva
        return Reserva.objects.filter(
            asiento_id=asiento_id,
            vuelo_id=vuelo_id,
            estado__in=['confirmada', 'pendiente']
        ).exists()
    
    @staticmethod
    def actualizar_estado(asiento_id: int, nuevo_estado: str) -> bool:
        """
        Actualiza el estado de un asiento.
        
        Args:
            asiento_id (int): ID del asiento
            nuevo_estado (str): Nuevo estado
            
        Returns:
            bool: True si se actualizó correctamente
        """
        try:
            asiento = Asiento.objects.get(id=asiento_id)
            asiento.estado = nuevo_estado
            asiento.save()
            return True
        except ObjectDoesNotExist:
            return False 