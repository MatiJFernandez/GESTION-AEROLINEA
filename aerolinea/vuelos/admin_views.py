"""
Vistas personalizadas para el admin de Django.

Este archivo contiene vistas que se integran con el admin de Django
para proporcionar funcionalidades adicionales como dashboards,
estadísticas y reportes.
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Vuelo, Avion, Asiento
from reservas.models import Reserva, Boleto
from pasajeros.models import Pasajero
from usuarios.models import Usuario


@staff_member_required
def dashboard_admin(request):
    """
    Dashboard principal del admin con estadísticas del sistema.
    
    Muestra:
    - Resumen de vuelos, reservas, pasajeros
    - Gráficos de ocupación
    - Alertas y notificaciones
    """
    
    # Obtener estadísticas generales
    total_vuelos = Vuelo.objects.count()
    vuelos_activos = Vuelo.objects.filter(estado='programado').count()
    vuelos_en_vuelo = Vuelo.objects.filter(estado='en_vuelo').count()
    vuelos_completados = Vuelo.objects.filter(estado='aterrizado').count()
    
    total_reservas = Reserva.objects.count()
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    reservas_confirmadas = Reserva.objects.filter(estado='confirmada').count()
    
    total_pasajeros = Pasajero.objects.count()
    total_usuarios = Usuario.objects.count()
    
    # Estadísticas de aviones
    total_aviones = Avion.objects.count()
    aviones_activos = Avion.objects.filter(estado='activo').count()
    aviones_mantenimiento = Avion.objects.filter(estado='mantenimiento').count()
    
    # Ocupación de vuelos próximos
    vuelos_proximos = Vuelo.objects.filter(
        fecha_salida__gte=timezone.now(),
        estado='programado'
    ).order_by('fecha_salida')[:10]
    
    # Calcular ocupación para cada vuelo próximo
    for vuelo in vuelos_proximos:
        asientos_ocupados = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'completada']
        ).count()
        vuelo.ocupacion_porcentaje = (asientos_ocupados / vuelo.avion.capacidad) * 100 if vuelo.avion.capacidad > 0 else 0
        vuelo.asientos_ocupados = asientos_ocupados
        vuelo.asientos_disponibles = vuelo.avion.capacidad - asientos_ocupados
    
    # Alertas del sistema
    alertas = []
    
    # Vuelos con poca ocupación
    vuelos_baja_ocupacion = []
    for vuelo in vuelos_proximos:
        if vuelo.ocupacion_porcentaje < 30 and vuelo.fecha_salida.date() <= (timezone.now().date() + timedelta(days=7)):
            vuelos_baja_ocupacion.append(vuelo)
    
    if vuelos_baja_ocupacion:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'{len(vuelos_baja_ocupacion)} vuelos próximos tienen baja ocupación (< 30%)',
            'vuelos': vuelos_baja_ocupacion
        })
    
    # Aviones en mantenimiento
    if aviones_mantenimiento > 0:
        alertas.append({
            'tipo': 'info',
            'mensaje': f'{aviones_mantenimiento} aviones están en mantenimiento',
            'aviones': Avion.objects.filter(estado='mantenimiento')
        })
    
    # Reservas pendientes de pago
    if reservas_pendientes > 0:
        alertas.append({
            'tipo': 'warning',
            'mensaje': f'{reservas_pendientes} reservas están pendientes de pago',
            'reservas': Reserva.objects.filter(estado='pendiente')[:5]
        })
    
    context = {
        'total_vuelos': total_vuelos,
        'vuelos_activos': vuelos_activos,
        'vuelos_en_vuelo': vuelos_en_vuelo,
        'vuelos_completados': vuelos_completados,
        'total_reservas': total_reservas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_confirmadas': reservas_confirmadas,
        'total_pasajeros': total_pasajeros,
        'total_usuarios': total_usuarios,
        'total_aviones': total_aviones,
        'aviones_activos': aviones_activos,
        'aviones_mantenimiento': aviones_mantenimiento,
        'vuelos_proximos': vuelos_proximos,
        'alertas': alertas,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_member_required
def estadisticas_ocupacion(request):
    """
    Vista para mostrar estadísticas detalladas de ocupación de vuelos.
    
    Incluye:
    - Gráficos de ocupación por ruta
    - Tendencias temporales
    - Análisis de rentabilidad
    """
    
    # Obtener vuelos del último mes
    fecha_inicio = timezone.now() - timedelta(days=30)
    vuelos_recientes = Vuelo.objects.filter(
        fecha_salida__gte=fecha_inicio
    ).order_by('fecha_salida')
    
    # Estadísticas por ruta
    estadisticas_rutas = {}
    for vuelo in vuelos_recientes:
        ruta = f"{vuelo.origen} → {vuelo.destino}"
        
        if ruta not in estadisticas_rutas:
            estadisticas_rutas[ruta] = {
                'total_vuelos': 0,
                'total_asientos': 0,
                'asientos_ocupados': 0,
                'ingresos_totales': 0,
                'ocupacion_promedio': 0
            }
        
        estadisticas_rutas[ruta]['total_vuelos'] += 1
        estadisticas_rutas[ruta]['total_asientos'] += vuelo.avion.capacidad
        
        # Calcular asientos ocupados
        asientos_ocupados = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'completada']
        ).count()
        estadisticas_rutas[ruta]['asientos_ocupados'] += asientos_ocupados
        
        # Calcular ingresos
        ingresos_vuelo = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'completada']
        ).aggregate(total=Sum('precio'))['total'] or 0
        estadisticas_rutas[ruta]['ingresos_totales'] += ingresos_vuelo
    
    # Calcular ocupación promedio por ruta
    for ruta, stats in estadisticas_rutas.items():
        if stats['total_asientos'] > 0:
            stats['ocupacion_promedio'] = (stats['asientos_ocupados'] / stats['total_asientos']) * 100
    
    # Ordenar rutas por ocupación
    rutas_ordenadas = sorted(
        estadisticas_rutas.items(),
        key=lambda x: x[1]['ocupacion_promedio'],
        reverse=True
    )
    
    # Estadísticas temporales (últimos 7 días)
    ultimos_7_dias = []
    for i in range(7):
        fecha = timezone.now().date() - timedelta(days=i)
        vuelos_dia = Vuelo.objects.filter(fecha_salida__date=fecha)
        
        total_asientos = sum(v.avion.capacidad for v in vuelos_dia)
        asientos_ocupados = sum(
            Reserva.objects.filter(
                vuelo=v,
                estado__in=['confirmada', 'completada']
            ).count() for v in vuelos_dia
        )
        
        ocupacion = (asientos_ocupados / total_asientos * 100) if total_asientos > 0 else 0
        
        ultimos_7_dias.append({
            'fecha': fecha,
            'ocupacion': round(ocupacion, 1),
            'total_vuelos': vuelos_dia.count()
        })
    
    ultimos_7_dias.reverse()  # Ordenar cronológicamente
    
    context = {
        'estadisticas_rutas': rutas_ordenadas,
        'ultimos_7_dias': ultimos_7_dias,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': timezone.now().date(),
    }
    
    return render(request, 'admin/estadisticas_ocupacion.html', context)


@staff_member_required
def reporte_pasajeros(request):
    """
    Vista para generar reportes de pasajeros.
    
    Incluye:
    - Lista de pasajeros por vuelo
    - Estadísticas de pasajeros frecuentes
    - Análisis de preferencias
    """
    
    # Obtener vuelos próximos
    vuelos_proximos = Vuelo.objects.filter(
        fecha_salida__gte=timezone.now(),
        estado='programado'
    ).order_by('fecha_salida')
    
    # Agrupar pasajeros por vuelo
    pasajeros_por_vuelo = {}
    for vuelo in vuelos_proximos:
        reservas = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'completada']
        ).select_related('pasajero')
        
        pasajeros_por_vuelo[vuelo] = {
            'reservas': reservas,
            'total_pasajeros': reservas.count(),
            'asientos_disponibles': vuelo.avion.capacidad - reservas.count()
        }
    
    # Pasajeros más frecuentes
    pasajeros_frecuentes = Pasajero.objects.annotate(
        total_reservas=Count('reservas')
    ).filter(
        total_reservas__gt=0
    ).order_by('-total_reservas')[:10]
    
    # Estadísticas por tipo de asiento
    estadisticas_asientos = {}
    for vuelo in vuelos_proximos:
        reservas = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'completada']
        ).select_related('asiento')
        
        for reserva in reservas:
            tipo_asiento = reserva.asiento.tipo
            if tipo_asiento not in estadisticas_asientos:
                estadisticas_asientos[tipo_asiento] = 0
            estadisticas_asientos[tipo_asiento] += 1
    
    context = {
        'pasajeros_por_vuelo': pasajeros_por_vuelo,
        'pasajeros_frecuentes': pasajeros_frecuentes,
        'estadisticas_asientos': estadisticas_asientos,
    }
    
    return render(request, 'admin/reporte_pasajeros.html', context)


@staff_member_required
def detalle_pasajeros_vuelo(request, vuelo_id):
    """
    Vista para mostrar el detalle de pasajeros de un vuelo específico.
    
    Args:
        vuelo_id: ID del vuelo
    """
    
    try:
        vuelo = Vuelo.objects.get(id=vuelo_id)
    except Vuelo.DoesNotExist:
        messages.error(request, 'Vuelo no encontrado')
        return redirect('admin:vuelos_vuelo_changelist')
    
    # Obtener reservas confirmadas
    reservas = Reserva.objects.filter(
        vuelo=vuelo,
        estado__in=['confirmada', 'completada']
    ).select_related('pasajero', 'asiento').order_by('asiento__fila', 'asiento__columna')
    
    # Agrupar por fila para mostrar en formato de avión
    asientos_por_fila = {}
    for reserva in reservas:
        fila = reserva.asiento.fila
        if fila not in asientos_por_fila:
            asientos_por_fila[fila] = {}
        asientos_por_fila[fila][reserva.asiento.columna] = reserva
    
    # Obtener configuración del avión
    avion = vuelo.avion
    asientos_disponibles = avion.capacidad - reservas.count()
    
    context = {
        'vuelo': vuelo,
        'avion': avion,
        'reservas': reservas,
        'asientos_por_fila': asientos_por_fila,
        'asientos_disponibles': asientos_disponibles,
        'ocupacion_porcentaje': (reservas.count() / avion.capacidad) * 100 if avion.capacidad > 0 else 0,
    }
    
    return render(request, 'admin/detalle_pasajeros_vuelo.html', context)


# API endpoints para AJAX
@staff_member_required
@require_http_methods(["GET"])
def api_estadisticas_vuelos(request):
    """
    API endpoint para obtener estadísticas de vuelos en tiempo real.
    """
    
    # Estadísticas básicas
    total_vuelos = Vuelo.objects.count()
    vuelos_activos = Vuelo.objects.filter(estado='programado').count()
    vuelos_en_vuelo = Vuelo.objects.filter(estado='en_vuelo').count()
    
    # Ocupación actual
    vuelos_proximos = Vuelo.objects.filter(
        fecha_salida__gte=timezone.now(),
        estado='programado'
    )[:5]
    
    ocupacion_vuelos = []
    for vuelo in vuelos_proximos:
        asientos_ocupados = Reserva.objects.filter(
            vuelo=vuelo,
            estado__in=['confirmada', 'completada']
        ).count()
        
        ocupacion_vuelos.append({
            'id': vuelo.id,
            'origen': vuelo.origen,
            'destino': vuelo.destino,
            'fecha_salida': vuelo.fecha_salida.strftime('%d/%m/%Y %H:%M'),
            'ocupacion': asientos_ocupados,
            'capacidad': vuelo.avion.capacidad,
            'porcentaje': round((asientos_ocupados / vuelo.avion.capacidad) * 100, 1) if vuelo.avion.capacidad > 0 else 0
        })
    
    data = {
        'total_vuelos': total_vuelos,
        'vuelos_activos': vuelos_activos,
        'vuelos_en_vuelo': vuelos_en_vuelo,
        'ocupacion_vuelos': ocupacion_vuelos,
        'timestamp': timezone.now().isoformat()
    }
    
    return JsonResponse(data)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def api_actualizar_estado_vuelo(request):
    """
    API endpoint para actualizar el estado de un vuelo.
    """
    
    try:
        data = json.loads(request.body)
        vuelo_id = data.get('vuelo_id')
        nuevo_estado = data.get('nuevo_estado')
        
        if not vuelo_id or not nuevo_estado:
            return JsonResponse({'error': 'Datos incompletos'}, status=400)
        
        vuelo = Vuelo.objects.get(id=vuelo_id)
        vuelo.estado = nuevo_estado
        vuelo.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Estado del vuelo {vuelo} actualizado a {nuevo_estado}'
        })
        
    except Vuelo.DoesNotExist:
        return JsonResponse({'error': 'Vuelo no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 