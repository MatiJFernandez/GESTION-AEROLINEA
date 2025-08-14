"""
Repositorio para la gestión de pasajeros.

Este archivo implementa la capa de repositorios del patrón Vista-Servicio-Repositorio.
Los repositorios manejan el acceso a datos y las consultas a la base de datos.
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from pasajeros.models import Pasajero


class PasajeroRepository:
    """Repositorio para la gestión de pasajeros."""
    
    @staticmethod
    def crear(nombre: str, apellido: str, tipo_documento: str, numero_documento: str, 
              fecha_nacimiento, email: str = None, telefono: str = None) -> Pasajero:
        """
        Crea un nuevo pasajero.
        
        Args:
            nombre (str): Nombre del pasajero
            apellido (str): Apellido del pasajero
            tipo_documento (str): Tipo de documento
            numero_documento (str): Número de documento
            fecha_nacimiento: Fecha de nacimiento
            email (str): Email del pasajero (opcional)
            telefono (str): Teléfono del pasajero (opcional)
            
        Returns:
            Pasajero: Pasajero creado
        """
        return Pasajero.objects.create(
            nombre=nombre,
            apellido=apellido,
            tipo_documento=tipo_documento,
            numero_documento=numero_documento,
            fecha_nacimiento=fecha_nacimiento,
            email=email,
            telefono=telefono
        )
    
    @staticmethod
    def obtener_por_id(pasajero_id: int) -> Pasajero | None:
        """
        Obtiene un pasajero por su ID.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            Pasajero: Pasajero encontrado o None
        """
        try:
            return Pasajero.objects.get(id=pasajero_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def obtener_con_reservas(pasajero_id: int) -> Pasajero | None:
        """
        Obtiene un pasajero con sus reservas cargadas.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            Pasajero: Pasajero con reservas
        """
        try:
            return Pasajero.objects.prefetch_related('reserva_set__vuelo').get(id=pasajero_id)
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def buscar_por_documento(tipo_documento: str, numero_documento: str) -> Pasajero | None:
        """
        Busca un pasajero por tipo y número de documento.
        
        Args:
            tipo_documento (str): Tipo de documento
            numero_documento (str): Número de documento
            
        Returns:
            Pasajero: Pasajero encontrado o None
        """
        try:
            return Pasajero.objects.get(
                tipo_documento=tipo_documento,
                numero_documento=numero_documento
            )
        except ObjectDoesNotExist:
            return None
    
    @staticmethod
    def buscar_por_nombre(nombre: str, apellido: str = None) -> list[Pasajero]:
        """
        Busca pasajeros por nombre y/o apellido.
        
        Args:
            nombre (str): Nombre del pasajero
            apellido (str): Apellido del pasajero (opcional)
            
        Returns:
            list[Pasajero]: Pasajeros que coinciden
        """
        queryset = Pasajero.objects.all()
        
        if nombre:
            queryset = queryset.filter(
                Q(nombre__icontains=nombre) | Q(apellido__icontains=nombre)
            )
        
        if apellido:
            queryset = queryset.filter(apellido__icontains=apellido)
        
        return list(queryset.order_by('apellido', 'nombre'))
    
    @staticmethod
    def buscar_por_criterios(criterios: dict) -> list[Pasajero]:
        """
        Busca pasajeros por múltiples criterios.
        
        Args:
            criterios (dict): Criterios de búsqueda
            
        Returns:
            list[Pasajero]: Pasajeros que cumplen los criterios
        """
        queryset = Pasajero.objects.all()
        
        if criterios.get('query'):
            query = criterios['query']
            queryset = queryset.filter(
                Q(nombre__icontains=query) |
                Q(apellido__icontains=query) |
                Q(numero_documento__icontains=query) |
                Q(email__icontains=query)
            )
        
        if criterios.get('tipo_documento'):
            queryset = queryset.filter(tipo_documento=criterios['tipo_documento'])
        
        if criterios.get('es_mayor_edad') is not None:
            from datetime import date
            hoy = date.today()
            if criterios['es_mayor_edad']:
                queryset = queryset.filter(fecha_nacimiento__lte=hoy.replace(year=hoy.year-18))
            else:
                queryset = queryset.filter(fecha_nacimiento__gt=hoy.replace(year=hoy.year-18))
        
        return list(queryset.order_by('apellido', 'nombre'))
    
    @staticmethod
    def obtener_todos() -> list[Pasajero]:
        """
        Obtiene todos los pasajeros ordenados.
        
        Returns:
            list[Pasajero]: Todos los pasajeros
        """
        return list(Pasajero.objects.all().order_by('apellido', 'nombre'))
    
    @staticmethod
    def actualizar(pasajero: Pasajero, **datos_actualizacion) -> Pasajero:
        """
        Actualiza un pasajero.
        
        Args:
            pasajero (Pasajero): Pasajero a actualizar
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Pasajero: Pasajero actualizado
        """
        for campo, valor in datos_actualizacion.items():
            setattr(pasajero, campo, valor)
        pasajero.save()
        return pasajero
    
    @staticmethod
    def eliminar(pasajero_id: int) -> bool:
        """
        Elimina un pasajero.
        
        Args:
            pasajero_id (int): ID del pasajero
            
        Returns:
            bool: True si se eliminó, False si no existe
        """
        try:
            pasajero = Pasajero.objects.get(id=pasajero_id)
            pasajero.delete()
            return True
        except ObjectDoesNotExist:
            return False
    
    @staticmethod
    def contar_total() -> int:
        """
        Cuenta el total de pasajeros.
        
        Returns:
            int: Total de pasajeros
        """
        return Pasajero.objects.count()
    
    @staticmethod
    def obtener_estadisticas() -> dict:
        """
        Obtiene estadísticas de pasajeros.
        
        Returns:
            dict: Estadísticas de pasajeros
        """
        from datetime import date
        
        hoy = date.today()
        mayor_edad = hoy.replace(year=hoy.year-18)
        
        return {
            'total': Pasajero.objects.count(),
            'mayores_edad': Pasajero.objects.filter(fecha_nacimiento__lte=mayor_edad).count(),
            'menores_edad': Pasajero.objects.filter(fecha_nacimiento__gt=mayor_edad).count(),
            'con_email': Pasajero.objects.exclude(email='').count(),
            'con_telefono': Pasajero.objects.exclude(telefono='').count(),
        } 