"""
Vistas administrativas para reportes y dashboard.

Este módivo contiene vistas específicas para:
- Dashboard administrativo
- Reportes de pasajeros por vuelo
- Estadísticas de ocupación
- Exportación de datos
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Avg, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import csv
import json

from usuarios.decorators import staff_required
from .models import Vuelo, Avion, Asiento
from reservas.models import Reserva, Boleto
from pasajeros.models import Pasajero


@staff_required
def dashboard_admin(request):
    """
    Dashboard administrativo con estadísticas generales.
    
    Muestra:
    - Estadísticas de ocupación
    - Vuelos del día
    - Reservas recientes
    - Métricas clave
    """
    today = timezone.now().date()
    
    # Estadísticas generales
    total_vuelos = Vuelo.objects.count()
    vuelos_hoy = Vuelo.objects.filter(fecha_salida__date=today).count()
    vuelos_programados = Vuelo.objects.filter(estado='programado').count()
    
    # Estadísticas de reservas
    total_reservas = Reserva.objects.count()
    reservas_hoy = Reserva.objects.filter(fecha_reserva__date=today).count()
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    reservas_confirmadas = Reserva.objects.filter(estado='confirmada').count()
    
    # Estadísticas de ocupación
    total_asientos = Asiento.objects.count()
    asientos_ocupados = Asiento.objects.filter(estado='ocupado').count()
    asientos_disponibles = Asiento.objects.filter(estado='disponible').count()
    
    # Calcular porcentaje de ocupación
    ocupacion_porcentaje = (asientos_ocupados / total_asientos * 100) if total_asientos > 0 else 0
    
    # Vuelos del día
    vuelos_del_dia = Vuelo.objects.filter(
        fecha_salida__date=today
    ).select_related('avion').order_by('fecha_salida')
    
    # Reservas recientes (últimas 10)
    reservas_recientes = Reserva.objects.select_related(
        'vuelo', 'pasajero', 'asiento'
    ).order_by('-fecha_reserva')[:10]
    
    # Estadísticas por destino (top 5)
    destinos_populares = Vuelo.objects.values('destino').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Estadísticas de ingresos (últimos 30 días)
    fecha_limite = today - timedelta(days=30)
    ingresos_mes = Reserva.objects.filter(
        fecha_reserva__date__gte=fecha_limite,
        estado='confirmada'
    ).aggregate(total=Sum('precio'))['total'] or 0
    
    # Gráfico de ocupación por día (últimos 7 días)
    ocupacion_por_dia = []
    for i in range(7):
        fecha = today - timedelta(days=i)
        vuelos_dia = Vuelo.objects.filter(fecha_salida__date=fecha)
        total_asientos_dia = sum(vuelo.avion.capacidad for vuelo in vuelos_dia)
        asientos_ocupados_dia = sum(
            vuelo.reservas.filter(estado='confirmada').count() 
            for vuelo in vuelos_dia
        )
        ocupacion_porcentaje_dia = (
            asientos_ocupados_dia / total_asientos_dia * 100
        ) if total_asientos_dia > 0 else 0
        
        ocupacion_por_dia.append({
            'fecha': fecha.strftime('%d/%m'),
            'ocupacion': round(ocupacion_porcentaje_dia, 1)
        })
    
    ocupacion_por_dia.reverse()  # Ordenar cronológicamente
    
    context = {
        # Estadísticas generales
        'total_vuelos': total_vuelos,
        'vuelos_hoy': vuelos_hoy,
        'vuelos_programados': vuelos_programados,
        'total_reservas': total_reservas,
        'reservas_hoy': reservas_hoy,
        'reservas_pendientes': reservas_pendientes,
        'reservas_confirmadas': reservas_confirmadas,
        
        # Estadísticas de ocupación
        'total_asientos': total_asientos,
        'asientos_ocupados': asientos_ocupados,
        'asientos_disponibles': asientos_disponibles,
        'ocupacion_porcentaje': round(ocupacion_porcentaje, 1),
        
        # Datos para listas
        'vuelos_del_dia': vuelos_del_dia,
        'reservas_recientes': reservas_recientes,
        'destinos_populares': destinos_populares,
        
        # Métricas financieras
        'ingresos_mes': ingresos_mes,
        
        # Datos para gráficos
        'ocupacion_por_dia': json.dumps(ocupacion_por_dia),
        
        # Fecha actual
        'hoy': today,
    }
    
    return render(request, 'admin/dashboard.html', context)


@staff_required
def reporte_pasajeros_vuelo(request):
    """
    Reporte de pasajeros por vuelo con filtros.
    
    Permite:
    - Filtrar por fecha, destino, estado
    - Ver detalles de pasajeros
    - Exportar a CSV
    """
    # Obtener parámetros de filtro
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    destino = request.GET.get('destino')
    estado = request.GET.get('estado')
    exportar = request.GET.get('exportar')
    
    # Query base
    vuelos = Vuelo.objects.select_related('avion').prefetch_related(
        'reservas__pasajero',
        'reservas__asiento'
    ).order_by('fecha_salida')
    
    # Aplicar filtros
    if fecha_desde:
        vuelos = vuelos.filter(fecha_salida__date__gte=fecha_desde)
    if fecha_hasta:
        vuelos = vuelos.filter(fecha_salida__date__lte=fecha_hasta)
    if destino:
        vuelos = vuelos.filter(destino__icontains=destino)
    if estado:
        vuelos = vuelos.filter(estado=estado)
    
    # Calcular estadísticas por vuelo
    vuelos_con_pasajeros = []
    for vuelo in vuelos:
        reservas_confirmadas = vuelo.reservas.filter(estado='confirmada')
        reservas_pendientes = vuelo.reservas.filter(estado='pendiente')
        
        vuelos_con_pasajeros.append({
            'vuelo': vuelo,
            'total_pasajeros': reservas_confirmadas.count(),
            'pasajeros_pendientes': reservas_pendientes.count(),
            'ocupacion_porcentaje': (
                reservas_confirmadas.count() / vuelo.avion.capacidad * 100
            ) if vuelo.avion.capacidad > 0 else 0,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_pendientes': reservas_pendientes,
        })
    
    # Paginación
    paginator = Paginator(vuelos_con_pasajeros, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Exportar a CSV si se solicita
    if exportar == 'csv':
        return exportar_pasajeros_csv(vuelos_con_pasajeros)
    
    context = {
        'page_obj': page_obj,
        'vuelos_con_pasajeros': page_obj,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'destino': destino,
        'estado': estado,
        'total_vuelos': len(vuelos_con_pasajeros),
    }
    
    return render(request, 'admin/reporte_pasajeros.html', context)


@staff_required
def detalle_pasajeros_vuelo(request, vuelo_id):
    """
    Vista detallada de pasajeros para un vuelo específico.
    """
    vuelo = get_object_or_404(Vuelo, id=vuelo_id)
    
    # Obtener todas las reservas del vuelo
    reservas = vuelo.reservas.select_related(
        'pasajero', 'asiento'
    ).order_by('asiento__numero')
    
    # Agrupar por estado
    reservas_confirmadas = reservas.filter(estado='confirmada')
    reservas_pendientes = reservas.filter(estado='pendiente')
    reservas_canceladas = reservas.filter(estado='cancelada')
    
    # Estadísticas
    total_reservas = reservas.count()
    ocupacion_porcentaje = (
        reservas_confirmadas.count() / vuelo.avion.capacidad * 100
    ) if vuelo.avion.capacidad > 0 else 0
    
    context = {
        'vuelo': vuelo,
        'reservas_confirmadas': reservas_confirmadas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_canceladas': reservas_canceladas,
        'total_reservas': total_reservas,
        'ocupacion_porcentaje': round(ocupacion_porcentaje, 1),
    }
    
    return render(request, 'admin/detalle_pasajeros_vuelo.html', context)


@staff_required
def estadisticas_ocupacion(request):
    """
    Estadísticas detalladas de ocupación.
    """
    # Obtener parámetros
    periodo = request.GET.get('periodo', '7')  # días
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    
    # Calcular fechas
    if fecha_desde and fecha_hasta:
        fecha_inicio = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
    else:
        fecha_fin = timezone.now().date()
        fecha_inicio = fecha_fin - timedelta(days=int(periodo))
    
    # Obtener vuelos en el período
    vuelos_periodo = Vuelo.objects.filter(
        fecha_salida__date__range=[fecha_inicio, fecha_fin]
    ).select_related('avion')
    
    # Calcular estadísticas diarias
    estadisticas_diarias = []
    for fecha in (fecha_inicio + timedelta(n) for n in range((fecha_fin - fecha_inicio).days + 1)):
        vuelos_dia = vuelos_periodo.filter(fecha_salida__date=fecha)
        
        total_asientos = sum(vuelo.avion.capacidad for vuelo in vuelos_dia)
        asientos_ocupados = sum(
            vuelo.reservas.filter(estado='confirmada').count() 
            for vuelo in vuelos_dia
        )
        
        ocupacion_porcentaje = (
            asientos_ocupados / total_asientos * 100
        ) if total_asientos > 0 else 0
        
        estadisticas_diarias.append({
            'fecha': fecha,
            'vuelos': vuelos_dia.count(),
            'total_asientos': total_asientos,
            'asientos_ocupados': asientos_ocupados,
            'ocupacion_porcentaje': round(ocupacion_porcentaje, 1),
        })
    
    # Estadísticas por destino
    destinos_stats = {}
    for vuelo in vuelos_periodo:
        destino = vuelo.destino
        if destino not in destinos_stats:
            destinos_stats[destino] = {
                'vuelos': 0,
                'total_asientos': 0,
                'asientos_ocupados': 0,
            }
        
        destinos_stats[destino]['vuelos'] += 1
        destinos_stats[destino]['total_asientos'] += vuelo.avion.capacidad
        destinos_stats[destino]['asientos_ocupados'] += vuelo.reservas.filter(estado='confirmada').count()
    
    # Calcular porcentajes por destino
    for destino, stats in destinos_stats.items():
        stats['ocupacion_porcentaje'] = (
            stats['asientos_ocupados'] / stats['total_asientos'] * 100
        ) if stats['total_asientos'] > 0 else 0
    
    context = {
        'estadisticas_diarias': estadisticas_diarias,
        'destinos_stats': destinos_stats,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'periodo': periodo,
    }
    
    return render(request, 'admin/estadisticas_ocupacion.html', context)


def exportar_pasajeros_csv(vuelos_con_pasajeros):
    """
    Exportar reporte de pasajeros a CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="pasajeros_vuelos_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Vuelo', 'Origen', 'Destino', 'Fecha Salida', 'Avión', 'Capacidad',
        'Pasajeros Confirmados', 'Pasajeros Pendientes', 'Ocupación %'
    ])
    
    for item in vuelos_con_pasajeros:
        vuelo = item['vuelo']
        writer.writerow([
            vuelo.id,
            vuelo.origen,
            vuelo.destino,
            vuelo.fecha_salida.strftime('%d/%m/%Y %H:%M'),
            vuelo.avion.modelo,
            vuelo.avion.capacidad,
            item['total_pasajeros'],
            item['pasajeros_pendientes'],
            f"{item['ocupacion_porcentaje']:.1f}%"
        ])
    
    return response


@staff_required
def api_estadisticas(request):
    """
    API para obtener estadísticas en formato JSON.
    """
    today = timezone.now().date()
    
    # Estadísticas básicas
    stats = {
        'vuelos_hoy': Vuelo.objects.filter(fecha_salida__date=today).count(),
        'reservas_hoy': Reserva.objects.filter(fecha_reserva__date=today).count(),
        'ocupacion_porcentaje': 0,
        'ingresos_hoy': 0,
    }
    
    # Calcular ocupación
    total_asientos = Asiento.objects.count()
    asientos_ocupados = Asiento.objects.filter(estado='ocupado').count()
    if total_asientos > 0:
        stats['ocupacion_porcentaje'] = round(asientos_ocupados / total_asientos * 100, 1)
    
    # Calcular ingresos del día
    ingresos_hoy = Reserva.objects.filter(
        fecha_reserva__date=today,
        estado='confirmada'
    ).aggregate(total=Sum('precio'))['total'] or 0
    stats['ingresos_hoy'] = ingresos_hoy
    
    return JsonResponse(stats) 