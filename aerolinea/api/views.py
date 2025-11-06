"""
Vistas para la API REST.

Este archivo define los viewsets y vistas para los endpoints de la API.

Documentación automática disponible en:
- Swagger UI: /swagger/
- ReDoc: /redoc/
- Schema JSON: /swagger.json
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone

from vuelos.models import Vuelo, Avion, Asiento
from vuelos.serializers import VueloSerializer, VueloListSerializer, AvionSerializer, AsientoSerializer

from pasajeros.models import Pasajero
from pasajeros.serializers import PasajeroSerializer, PasajeroListSerializer

from reservas.models import Reserva, Boleto
from reservas.serializers import ReservaSerializer, ReservaListSerializer, BoletoSerializer

from usuarios.models import Usuario
from usuarios.serializers import UsuarioSerializer, UsuarioListSerializer, UsuarioCreateSerializer, UsuarioUpdateSerializer

from .permissions import IsAdminOrReadOnly, IsAdminOrEmployee, IsAdmin


class AvionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Avion.
    
    Permite listar, crear, recuperar, actualizar y eliminar aviones.
    """
    queryset = Avion.objects.all()
    serializer_class = AvionSerializer
    permission_classes = [IsAdminOrEmployee]


class AsientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Asiento.
    
    Permite listar, crear, recuperar, actualizar y eliminar asientos.
    """
    queryset = Asiento.objects.all()
    serializer_class = AsientoSerializer
    permission_classes = [IsAdminOrEmployee]
    
    def get_queryset(self):
        """
        Permite filtrar asientos por avión y estado.
        
        Ejemplos:
        - /api/asientos/?avion=1
        - /api/asientos/?estado=disponible
        """
        queryset = super().get_queryset()
        avion_id = self.request.query_params.get('avion', None)
        estado = self.request.query_params.get('estado', None)
        
        if avion_id:
            queryset = queryset.filter(avion_id=avion_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset


class VueloViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Vuelo.
    
    Permite listar, crear, recuperar, actualizar y eliminar vuelos.
    """
    queryset = Vuelo.objects.all()
    serializer_class = VueloSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return VueloListSerializer
        return VueloSerializer
    
    def get_queryset(self):
        """
        Permite filtrar vuelos por origen, destino, estado y fecha.
        
        Ejemplos:
        - /api/vuelos/?origen=Buenos Aires
        - /api/vuelos/?destino=Miami
        - /api/vuelos/?estado=programado
        - /api/vuelos/?fecha_min=2024-01-01
        """
        queryset = super().get_queryset()
        origen = self.request.query_params.get('origen', None)
        destino = self.request.query_params.get('destino', None)
        estado = self.request.query_params.get('estado', None)
        fecha_min = self.request.query_params.get('fecha_min', None)
        fecha_max = self.request.query_params.get('fecha_max', None)
        
        if origen:
            queryset = queryset.filter(origen__icontains=origen)
        if destino:
            queryset = queryset.filter(destino__icontains=destino)
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_min:
            queryset = queryset.filter(fecha_salida__gte=fecha_min)
        if fecha_max:
            queryset = queryset.filter(fecha_salida__lte=fecha_max)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def asientos_disponibles(self, request, pk=None):
        """
        Retorna los asientos disponibles para un vuelo específico.
        
        Este endpoint lista todos los asientos con estado 'disponible' del avión
        asociado al vuelo.
        
        Parámetros:
            pk: ID del vuelo
        
        Returns:
            Lista de asientos disponibles con sus características
        """
        vuelo = self.get_object()
        asientos_disponibles = Asiento.objects.filter(
            avion=vuelo.avion,
            estado='disponible'
        )
        serializer = AsientoSerializer(asientos_disponibles, many=True)
        return Response(serializer.data)


class PasajeroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Pasajero.
    
    Permite listar, crear, recuperar, actualizar y eliminar pasajeros.
    """
    queryset = Pasajero.objects.all()
    serializer_class = PasajeroSerializer
    permission_classes = [IsAdminOrEmployee]
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return PasajeroListSerializer
        return PasajeroSerializer
    
    def get_queryset(self):
        """
        Permite filtrar pasajeros por documento, nombre o apellido.
        
        Ejemplos:
        - /api/pasajeros/?documento=12345678
        - /api/pasajeros/?nombre=Juan
        - /api/pasajeros/?apellido=Pérez
        """
        queryset = super().get_queryset()
        documento = self.request.query_params.get('documento', None)
        nombre = self.request.query_params.get('nombre', None)
        apellido = self.request.query_params.get('apellido', None)
        
        if documento:
            queryset = queryset.filter(documento__icontains=documento)
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        if apellido:
            queryset = queryset.filter(apellido__icontains=apellido)
        
        return queryset


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Reserva.
    
    Permite listar, crear, recuperar, actualizar y eliminar reservas.
    """
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]  # Usuarios autenticados pueden crear sus propias reservas
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return ReservaListSerializer
        return ReservaSerializer
    
    def get_queryset(self):
        """
        Permite filtrar reservas por estado, pasajero, vuelo o código.
        
        Ejemplos:
        - /api/reservas/?estado=confirmada
        - /api/reservas/?pasajero=1
        - /api/reservas/?vuelo=2
        - /api/reservas/?codigo=ABC123
        """
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado', None)
        pasajero = self.request.query_params.get('pasajero', None)
        vuelo = self.request.query_params.get('vuelo', None)
        codigo = self.request.query_params.get('codigo', None)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        if pasajero:
            queryset = queryset.filter(pasajero_id=pasajero)
        if vuelo:
            queryset = queryset.filter(vuelo_id=vuelo)
        if codigo:
            queryset = queryset.filter(codigo_reserva__icontains=codigo)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """
        Confirma una reserva pendiente.
        
        Cambia el estado de la reserva de 'pendiente' a 'confirmada'.
        Solo funciona si la reserva está en estado pendiente.
        """
        reserva = self.get_object()
        if reserva.estado == 'pendiente':
            reserva.estado = 'confirmada'
            reserva.save()
            serializer = self.get_serializer(reserva)
            return Response(serializer.data)
        return Response(
            {'error': 'La reserva debe estar en estado pendiente'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        Cancela una reserva.
        
        Verifica si la reserva puede ser cancelada según sus reglas de negocio
        y cambia su estado a 'cancelada'.
        """
        reserva = self.get_object()
        if reserva.puede_cancelar():
            reserva.estado = 'cancelada'
            reserva.save()
            serializer = self.get_serializer(reserva)
            return Response(serializer.data)
        return Response(
            {'error': 'Esta reserva no puede ser cancelada'},
            status=status.HTTP_400_BAD_REQUEST
        )


class BoletoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Boleto.
    
    Permite listar, crear, recuperar, actualizar y eliminar boletos.
    """
    queryset = Boleto.objects.all()
    serializer_class = BoletoSerializer
    permission_classes = [IsAdminOrEmployee]
    
    @action(detail=True, methods=['post'])
    def usar(self, request, pk=None):
        """
        Marca un boleto como usado.
        
        Este endpoint se usa cuando un pasajero aborda el vuelo.
        Cambia el estado del boleto de 'emitido' a 'usado'.
        
        Returns:
            Datos del boleto actualizado con estado 'usado'
        """
        boleto = self.get_object()
        boleto.marcar_como_usado()
        serializer = self.get_serializer(boleto)
        return Response(serializer.data)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el modelo Usuario.
    
    Permite listar, crear, recuperar, actualizar y eliminar usuarios.
    Solo usuarios admin pueden acceder.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == 'list':
            return UsuarioListSerializer
        elif self.action == 'create':
            return UsuarioCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UsuarioUpdateSerializer
        return UsuarioSerializer
