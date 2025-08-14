"""
Servicio para la gestión de vuelos.

Este archivo implementa la capa de servicios del patrón Vista-Servicio-Repositorio.
Los servicios contienen la lógica de negocio y orquestan las operaciones.
"""

from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import List
from vuelos.models import Vuelo, Avion, Asiento
from vuelos.repositories.vuelos import VueloRepository, AvionRepository, AsientoRepository


class VueloService:
    """Servicio para la gestión de vuelos."""
    
    @staticmethod
    def crear_vuelo(origen: str, destino: str, fecha_salida, fecha_llegada,
                    precio_base: float, avion_id: int, estado: str = 'programado') -> Vuelo:
        """
        Crea un nuevo vuelo con validaciones de negocio.
        
        Args:
            origen (str): Ciudad de origen
            destino (str): Ciudad de destino
            fecha_salida: Fecha y hora de salida
            fecha_llegada: Fecha y hora de llegada
            precio_base (float): Precio base del vuelo
            avion_id (int): ID del avión
            estado (str): Estado del vuelo
            
        Returns:
            Vuelo: El vuelo creado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones de negocio
        VueloService._validar_datos_vuelo(origen, destino, fecha_salida, fecha_llegada, precio_base)
        VueloService._validar_disponibilidad_avion(avion_id, fecha_salida)
        
        # Crear vuelo
        vuelo = VueloRepository.crear(
            origen=origen,
            destino=destino,
            fecha_salida=fecha_salida,
            fecha_llegada=fecha_llegada,
            precio_base=precio_base,
            avion_id=avion_id,
            estado=estado
        )
        
        # Lógica adicional post-creación
        VueloService._procesar_vuelo_creado(vuelo)
        
        return vuelo
    
    @staticmethod
    def obtener_vuelo(vuelo_id: int) -> Vuelo | None:
        """
        Obtiene un vuelo por su ID.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            Vuelo: Vuelo encontrado o None
        """
        return VueloRepository.obtener_por_id(vuelo_id)
    
    @staticmethod
    def obtener_vuelo_con_detalles(vuelo_id: int) -> Vuelo | None:
        """
        Obtiene un vuelo con todos sus detalles.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            Vuelo: Vuelo con detalles
        """
        return VueloRepository.obtener_con_detalles(vuelo_id)
    
    @staticmethod
    def buscar_vuelos_disponibles(filtros: dict = None) -> List[Vuelo]:
        """
        Busca vuelos disponibles con filtros.
        
        Args:
            filtros (dict): Filtros de búsqueda
            
        Returns:
            List[Vuelo]: Vuelos disponibles
        """
        return VueloRepository.buscar_disponibles(filtros)
    
    @staticmethod
    def obtener_proximos_vuelos(limite: int = 5) -> List[Vuelo]:
        """
        Obtiene los próximos vuelos.
        
        Args:
            limite (int): Número máximo de vuelos a obtener
            
        Returns:
            List[Vuelo]: Próximos vuelos
        """
        return VueloRepository.obtener_proximos_vuelos(limite)
    
    @staticmethod
    def actualizar_estado_vuelo(vuelo_id: int, nuevo_estado: str) -> Vuelo | None:
        """
        Actualiza el estado de un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            nuevo_estado (str): Nuevo estado
            
        Returns:
            Vuelo: Vuelo actualizado
            
        Raises:
            ValidationError: Si el estado no es válido
        """
        # Validar que el vuelo existe
        vuelo = VueloRepository.obtener_por_id(vuelo_id)
        if not vuelo:
            raise ValidationError("Vuelo no encontrado")
        
        # Validar transición de estado
        VueloService._validar_transicion_estado(vuelo.estado, nuevo_estado)
        
        # Actualizar vuelo
        return VueloRepository.actualizar(vuelo, estado=nuevo_estado)
    
    @staticmethod
    def actualizar_vuelo(vuelo_id: int, **datos_actualizacion) -> Vuelo | None:
        """
        Actualiza un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            **datos_actualizacion: Datos a actualizar
            
        Returns:
            Vuelo: Vuelo actualizado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validar que el vuelo existe
        vuelo = VueloRepository.obtener_por_id(vuelo_id)
        if not vuelo:
            raise ValidationError("Vuelo no encontrado")
        
        # Validar datos de actualización
        VueloService._validar_datos_actualizacion(datos_actualizacion)
        
        # Actualizar vuelo
        return VueloRepository.actualizar(vuelo, **datos_actualizacion)
    
    @staticmethod
    def eliminar_vuelo(vuelo_id: int) -> bool:
        """
        Elimina un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            bool: True si se eliminó correctamente
            
        Raises:
            ValidationError: Si el vuelo no puede ser eliminado
        """
        # Validar que el vuelo existe
        vuelo = VueloRepository.obtener_por_id(vuelo_id)
        if not vuelo:
            raise ValidationError("Vuelo no encontrado")
        
        # Validar que no tenga reservas activas
        VueloService._validar_sin_reservas_activas(vuelo)
        
        # Eliminar vuelo
        return VueloRepository.eliminar(vuelo_id)
    
    @staticmethod
    def _validar_datos_vuelo(origen: str, destino: str, fecha_salida, fecha_llegada, precio_base: float):
        """Valida los datos del vuelo."""
        # Validar campos obligatorios
        if not origen:
            raise ValidationError("El origen es obligatorio")
        if not destino:
            raise ValidationError("El destino es obligatorio")
        if not fecha_salida:
            raise ValidationError("La fecha de salida es obligatoria")
        if not fecha_llegada:
            raise ValidationError("La fecha de llegada es obligatoria")
        if precio_base <= 0:
            raise ValidationError("El precio base debe ser mayor a 0")
        
        # Validar fechas
        if fecha_salida <= timezone.now():
            raise ValidationError("La fecha de salida debe ser futura")
        
        if fecha_llegada <= fecha_salida:
            raise ValidationError("La fecha de llegada debe ser posterior a la fecha de salida")
        
        # Validar origen y destino diferentes
        if origen.lower() == destino.lower():
            raise ValidationError("El origen y destino no pueden ser iguales")
    
    @staticmethod
    def _validar_disponibilidad_avion(avion_id: int, fecha_salida):
        """Valida la disponibilidad del avión."""
        # Verificar que el avión existe y está activo
        avion = AvionRepository.obtener_por_id(avion_id)
        if not avion:
            raise ValidationError("Avión no encontrado")
        
        if avion.estado != 'activo':
            raise ValidationError("El avión no está disponible")
        
        # Verificar que no haya otros vuelos programados para el mismo avión en la misma fecha
        vuelos_existentes = VueloRepository.buscar_por_avion_y_fecha(avion_id, fecha_salida)
        if vuelos_existentes:
            raise ValidationError("El avión ya tiene vuelos programados para esa fecha")
    
    @staticmethod
    def _validar_transicion_estado(estado_actual: str, nuevo_estado: str):
        """Valida la transición de estado."""
        transiciones_validas = {
            'programado': ['en_curso', 'cancelado'],
            'en_curso': ['completado', 'cancelado'],
            'completado': [],
            'cancelado': []
        }
        
        if nuevo_estado not in transiciones_validas.get(estado_actual, []):
            raise ValidationError(f"No se puede cambiar de '{estado_actual}' a '{nuevo_estado}'")
    
    @staticmethod
    def _validar_datos_actualizacion(datos: dict):
        """Valida los datos de actualización."""
        if 'fecha_salida' in datos:
            if datos['fecha_salida'] <= timezone.now():
                raise ValidationError("La fecha de salida debe ser futura")
        
        if 'precio_base' in datos:
            if datos['precio_base'] <= 0:
                raise ValidationError("El precio base debe ser mayor a 0")
    
    @staticmethod
    def _validar_sin_reservas_activas(vuelo: Vuelo):
        """Valida que el vuelo no tenga reservas activas."""
        from reservas.repositories.reservas import ReservaRepository
        reservas_activas = ReservaRepository.buscar_por_criterios({
            'vuelo_id': vuelo.id,
            'estado': 'confirmada'
        })
        if reservas_activas:
            raise ValidationError("No se puede eliminar un vuelo con reservas activas")
    
    @staticmethod
    def _procesar_vuelo_creado(vuelo: Vuelo):
        """Procesa acciones adicionales después de crear un vuelo."""
        # Aquí se pueden agregar acciones como:
        # - Notificar a pasajeros registrados
        # - Actualizar estadísticas
        # - Generar documentos de vuelo
        pass


class AvionService:
    """Servicio para la gestión de aviones."""
    
    @staticmethod
    def crear_avion(modelo: str, capacidad: int, estado: str = 'activo') -> Avion:
        """
        Crea un nuevo avión con validaciones de negocio.
        
        Args:
            modelo (str): Modelo del avión
            capacidad (int): Capacidad de pasajeros
            estado (str): Estado del avión
            
        Returns:
            Avion: El avión creado
            
        Raises:
            ValidationError: Si los datos no son válidos
        """
        # Validaciones de negocio
        AvionService._validar_datos_avion(modelo, capacidad)
        
        # Crear avión
        avion = AvionRepository.crear(
            modelo=modelo,
            capacidad=capacidad,
            estado=estado
        )
        
        # Lógica adicional post-creación
        AvionService._procesar_avion_creado(avion)
        
        return avion
    
    @staticmethod
    def obtener_avion(avion_id: int) -> Avion | None:
        """
        Obtiene un avión por su ID.
        
        Args:
            avion_id (int): ID del avión
            
        Returns:
            Avion: Avión encontrado o None
        """
        return AvionRepository.obtener_por_id(avion_id)
    
    @staticmethod
    def obtener_aviones_activos() -> List[Avion]:
        """
        Obtiene los aviones activos.
        
        Returns:
            List[Avion]: Aviones activos
        """
        return AvionRepository.buscar_activos()
    
    @staticmethod
    def buscar_por_modelo(modelo: str) -> List[Avion]:
        """
        Busca aviones por modelo.
        
        Args:
            modelo (str): Modelo del avión
            
        Returns:
            List[Avion]: Aviones encontrados
        """
        return AvionRepository.buscar_por_modelo(modelo)
    
    @staticmethod
    def actualizar_estado_avion(avion_id: int, nuevo_estado: str) -> Avion | None:
        """
        Actualiza el estado de un avión.
        
        Args:
            avion_id (int): ID del avión
            nuevo_estado (str): Nuevo estado
            
        Returns:
            Avion: Avión actualizado
            
        Raises:
            ValidationError: Si el estado no es válido
        """
        # Validar que el avión existe
        avion = AvionRepository.obtener_por_id(avion_id)
        if not avion:
            raise ValidationError("Avión no encontrado")
        
        # Validar estado
        estados_validos = ['activo', 'mantenimiento', 'retirado']
        if nuevo_estado not in estados_validos:
            raise ValidationError("Estado de avión no válido")
        
        # Actualizar avión
        return AvionRepository.actualizar(avion, estado=nuevo_estado)
    
    @staticmethod
    def _validar_datos_avion(modelo: str, capacidad: int):
        """Valida los datos del avión."""
        if not modelo:
            raise ValidationError("El modelo es obligatorio")
        
        if capacidad <= 0:
            raise ValidationError("La capacidad debe ser mayor a 0")
        
        if capacidad > 1000:
            raise ValidationError("La capacidad no puede ser mayor a 1000")
    
    @staticmethod
    def _procesar_avion_creado(avion: Avion):
        """Procesa acciones adicionales después de crear un avión."""
        # Aquí se pueden agregar acciones como:
        # - Crear asientos automáticamente
        # - Registrar en sistema de mantenimiento
        # - Generar documentación técnica
        pass


class AsientoService:
    """Servicio para la gestión de asientos."""
    
    @staticmethod
    def crear_asientos_para_avion(avion_id: int) -> List[Asiento]:
        """
        Crea asientos automáticamente para un avión.
        
        Args:
            avion_id (int): ID del avión
            
        Returns:
            List[Asiento]: Asientos creados
        """
        avion = AvionRepository.obtener_por_id(avion_id)
        if not avion:
            raise ValidationError("Avión no encontrado")
        
        asientos_creados = []
        
        # Crear asientos según la capacidad del avión
        filas = (avion.capacidad // 6) + 1  # 6 asientos por fila
        columnas = ['A', 'B', 'C', 'D', 'E', 'F']
        
        for fila in range(1, filas + 1):
            for columna in columnas:
                if len(asientos_creados) >= avion.capacidad:
                    break
                
                numero = f"{fila}{columna}"
                clase = AsientoService._determinar_clase(fila, avion.capacidad)
                
                asiento = AsientoRepository.crear(
                    avion_id=avion_id,
                    numero=numero,
                    fila=fila,
                    columna=columna,
                    clase=clase
                )
                asientos_creados.append(asiento)
        
        return asientos_creados
    
    @staticmethod
    def obtener_asientos_disponibles(vuelo_id: int) -> List[Asiento]:
        """
        Obtiene los asientos disponibles para un vuelo.
        
        Args:
            vuelo_id (int): ID del vuelo
            
        Returns:
            List[Asiento]: Asientos disponibles
        """
        return AsientoRepository.buscar_disponibles_por_vuelo(vuelo_id)
    
    @staticmethod
    def _determinar_clase(fila: int, capacidad_total: int) -> str:
        """Determina la clase del asiento según la fila."""
        if fila <= 2:
            return 'primera'
        elif fila <= 6:
            return 'business'
        else:
            return 'economica' 