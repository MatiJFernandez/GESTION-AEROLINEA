"""
Vistas de reportes para la API REST.

Este archivo define endpoints para generar reportes estadísticos.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta

from vuelos.models import Vuelo, Avion
from reservas.models import Reserva, Boleto
from pasajeros.models import Pasajero

from .permissions import IsAdminOrEmployee


class ReportesViewSet(viewsets.ViewSet):
    """
    ViewSet para generar reportes estadísticos.
    
    Requiere permisos de administrador o empleado.
    """
    permission_classes = [IsAdminOrEmployee]
    
    @action(detail=False, methods=['get'])
    def estadisticas_generales(self, request):
        """
        Retorna estadísticas generales del sistema.
        """
        total_vuelos = Vuelo.objects.count()
        total_pasajeros = Pasajero.objects.count()
        total_reservas = Reserva.objects.count()
        total_aviones = Avion.objects.count()
        
        reservas_confirmadas = Reserva.objects.filter(estado='confirmada').count()
        reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
        
        vuelos_programados = Vuelo.objects.filter(estado='programado').count()
        vuelos_en_vuelo = Vuelo.objects.filter(estado='en_vuelo').count()
        
        return Response({
            'total_vuelos': total_vuelos,
            'total_pasajeros': total_pasajeros,
            'total_reservas': total_reservas,
            'total_aviones': total_aviones,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_pendientes': reservas_pendientes,
            'vuelos_programados': vuelos_programados,
            'vuelos_en_vuelo': vuelos_en_vuelo,
        })
    
    @action(detail=False, methods=['get'])
    def reporte_vuelos(self, request):
        """
        Retorna reporte detallado de vuelos.
        """
        origen = request.query_params.get('origen', None)
        destino = request.query_params.get('destino', None)
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        queryset = Vuelo.objects.all()
        
        if origen:
            queryset = queryset.filter(origen__icontains=origen)
        if destino:
            queryset = queryset.filter(destino__icontains=destino)
        if fecha_inicio:
            queryset = queryset.filter(fecha_salida__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_salida__lte=fecha_fin)
        
        # Estadísticas
        total = queryset.count()
        por_estado = queryset.values('estado').annotate(total=Count('id'))
        
        # Ventas totales estimadas
        ventas_estimadas = sum([v.precio_base * v.avion.capacidad * 0.7 for v in queryset])
        
        return Response({
            'total_vuelos': total,
            'por_estado': list(por_estado),
            'ventas_estimadas': ventas_estimadas,
        })
    
    @action(detail=False, methods=['get'])
    def reporte_reservas(self, request):
        """
        Retorna reporte detallado de reservas.
        """
        mes = request.query_params.get('mes', None)
        año = request.query_params.get('año', None)
        
        queryset = Reserva.objects.all()
        
        if año:
            if mes:
                queryset = queryset.filter(
                    fecha_reserva__year=año,
                    fecha_reserva__month=mes
                )
            else:
                queryset = queryset.filter(fecha_reserva__year=año)
        
        total_reservas = queryset.count()
        por_estado = queryset.values('estado').annotate(total=Count('id'))
        
        total_ingresos = queryset.filter(estado='confirmada').aggregate(
            total=Sum('precio')
        )['total'] or 0
        
        # Reservas por vuelo
        reservas_por_vuelo = queryset.values('vuelo__origen', 'vuelo__destino').annotate(
            total=Count('id'),
            total_ingresos=Sum('precio')
        )[:10]
        
        return Response({
            'total_reservas': total_reservas,
            'por_estado': list(por_estado),
            'total_ingresos': total_ingresos,
            'reservas_por_vuelo': list(reservas_por_vuelo),
        })
    
    @action(detail=False, methods=['get'])
    def reporte_pasajeros(self, request):
        """
        Retorna reporte de pasajeros más frecuentes.
        """
        top_n = int(request.query_params.get('top', 10))
        
        # Pasajeros más frecuentes
        pasajeros_frecuentes = Pasajero.objects.annotate(
            total_reservas=Count('reservas')
        ).order_by('-total_reservas')[:top_n]
        
        results = [{
            'id': p.id,
            'nombre': p.get_nombre_completo(),
            'documento': p.documento,
            'total_reservas': p.total_reservas
        } for p in pasajeros_frecuentes]
        
        return Response({
            'pasajeros_frecuentes': results,
            'total_pasajeros': Pasajero.objects.count(),
        })
    
    @action(detail=False, methods=['get'])
    def reporte_ocupacion(self, request):
        """
        Retorna reporte de ocupación de vuelos.
        """
        vuelo_id = request.query_params.get('vuelo', None)
        
        if vuelo_id:
            vuelos = Vuelo.objects.filter(id=vuelo_id)
        else:
            vuelos = Vuelo.objects.all()
        
        resultados = []
        for vuelo in vuelos:
            asientos_total = vuelo.avion.capacidad
            reservas_count = vuelo.reservas.filter(estado='confirmada').count()
            ocupacion = (reservas_count / asientos_total * 100) if asientos_total > 0 else 0
            
            resultados.append({
                'vuelo_id': vuelo.id,
                'ruta': f"{vuelo.origen} → {vuelo.destino}",
                'asientos_totales': asientos_total,
                'reservas_confirmadas': reservas_count,
                'porcentaje_ocupacion': round(ocupacion, 2),
            })
        
        return Response({
            'ocupacion_vuelos': resultados,
        })

