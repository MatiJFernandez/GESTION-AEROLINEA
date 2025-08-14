"""
Vistas para la aplicación vuelos.

Este archivo contiene todas las vistas relacionadas con:
- Página principal del sitio
- Gestión de vuelos
- Gestión de aviones
- Gestión de asientos

Implementa el patrón Vista-Servicio-Repositorio.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from usuarios.decorators import staff_required, active_flight_required
from .models import Vuelo, Avion, Asiento
from .services.vuelos import VueloService, AvionService, AsientoService

# Inicializar servicios
vuelo_service = VueloService()
avion_service = AvionService()
asiento_service = AsientoService()

def home(request):
    """
    Vista para la página principal del sitio.
    
    Muestra información general de la aerolínea y vuelos destacados.
    Implementa el patrón Vista-Servicio-Repositorio.
    """
    # Usar servicios para obtener datos
    vuelos_proximos = vuelo_service.buscar_vuelos_disponibles()[:5]
    
    # Obtener estadísticas básicas
    total_vuelos = Vuelo.objects.count()
    vuelos_activos = Vuelo.objects.filter(estado='programado').count()
    total_aviones = Avion.objects.count()
    
    context = {
        'vuelos_proximos': vuelos_proximos,
        'total_vuelos': total_vuelos,
        'vuelos_activos': vuelos_activos,
        'total_aviones': total_aviones,
    }
    
    return render(request, 'vuelos/home.html', context)


def lista_vuelos(request):
    """
    Vista para mostrar la lista de todos los vuelos disponibles.
    
    Permite filtrar por origen, destino, fecha y estado.
    Incluye paginación y ordenamiento.
    """
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    # Query optimizada con select_related para reducir consultas a la base de datos
    vuelos = Vuelo.objects.select_related('avion').all().order_by('fecha_salida')
    
    # Filtros avanzados
    origen = request.GET.get('origen')
    destino = request.GET.get('destino')
    estado = request.GET.get('estado')
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    precio_min = request.GET.get('precio_min')
    precio_max = request.GET.get('precio_max')
    
    # Aplicar filtros
    if origen:
        vuelos = vuelos.filter(origen__icontains=origen)
    if destino:
        vuelos = vuelos.filter(destino__icontains=destino)
    if estado:
        vuelos = vuelos.filter(estado=estado)
    if fecha_desde:
        vuelos = vuelos.filter(fecha_salida__date__gte=fecha_desde)
    if fecha_hasta:
        vuelos = vuelos.filter(fecha_salida__date__lte=fecha_hasta)
    if precio_min:
        vuelos = vuelos.filter(precio_base__gte=precio_min)
    if precio_max:
        vuelos = vuelos.filter(precio_base__lte=precio_max)
    
    # Ordenamiento
    orden = request.GET.get('orden', 'fecha_salida')
    if orden == 'precio':
        vuelos = vuelos.order_by('precio_base')
    elif orden == 'precio_desc':
        vuelos = vuelos.order_by('-precio_base')
    elif orden == 'duracion':
        vuelos = vuelos.order_by('duracion')
    else:
        vuelos = vuelos.order_by('fecha_salida')
    
    # Paginación
    paginator = Paginator(vuelos, 10)  # 10 vuelos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_vuelos = vuelos.count()
    vuelos_disponibles = vuelos.filter(estado='programado').count()
    
    context = {
        'page_obj': page_obj,
        'vuelos': page_obj,
        'origen': origen,
        'destino': destino,
        'estado': estado,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'orden': orden,
        'total_vuelos': total_vuelos,
        'vuelos_disponibles': vuelos_disponibles,
    }
    
    return render(request, 'vuelos/lista_vuelos.html', context)


def detalle_vuelo(request, vuelo_id):
    """
    Vista para mostrar los detalles de un vuelo específico.
    
    Incluye información del vuelo, asientos disponibles y opciones de reserva.
    """
    # Optimización: incluir avión en una sola consulta
    vuelo = get_object_or_404(
        Vuelo.objects.select_related('avion'),
        id=vuelo_id
    )
    
    # Obtener todos los asientos del avión del vuelo
    todos_asientos = vuelo.avion.asientos.all().order_by('fila', 'columna')
    
    # Obtener reservas existentes para este vuelo específico
    reservas_vuelo = vuelo.reservas.filter(
        estado__in=['pendiente', 'confirmada']
    ).select_related('asiento', 'pasajero')
    
    # Crear un set de asientos reservados para este vuelo
    asientos_reservados = set(reserva.asiento.id for reserva in reservas_vuelo)
    
    # Filtrar asientos disponibles (no reservados para este vuelo)
    asientos_disponibles = []
    asientos_ocupados = []
    asientos_reservados_otros = []
    
    for asiento in todos_asientos:
        if asiento.id in asientos_reservados:
            # Asiento reservado para este vuelo
            asientos_ocupados.append(asiento)
        elif asiento.estado == 'disponible':
            # Asiento disponible
            asientos_disponibles.append(asiento)
        else:
            # Asiento ocupado por otros vuelos
            asientos_reservados_otros.append(asiento)
    
    # Agrupar asientos disponibles por tipo
    asientos_por_tipo = {}
    for asiento in asientos_disponibles:
        tipo = asiento.tipo
        if tipo not in asientos_por_tipo:
            asientos_por_tipo[tipo] = []
        asientos_por_tipo[tipo].append(asiento)
    
    # Calcular estadísticas precisas
    total_asientos = len(todos_asientos)
    asientos_disponibles_count = len(asientos_disponibles)
    asientos_ocupados_count = len(asientos_ocupados)
    porcentaje_ocupacion = (asientos_ocupados_count / total_asientos) * 100 if total_asientos > 0 else 0
    
    # Verificar si el usuario puede hacer reservas
    puede_reservar = (
        request.user.is_authenticated and 
        vuelo.estado == 'programado' and 
        asientos_disponibles_count > 0
    )
    
    # Obtener información de precios por tipo de asiento
    from decimal import Decimal
    precios_por_tipo = {
        'primera': vuelo.precio_base * Decimal('2.5'),  # 150% más caro
        'premium': vuelo.precio_base * Decimal('1.8'),  # 80% más caro
        'economica': vuelo.precio_base,      # Precio base
    }
    
    context = {
        'vuelo': vuelo,
        'asientos_disponibles': asientos_disponibles,
        'asientos_ocupados': asientos_ocupados,
        'asientos_reservados_otros': asientos_reservados_otros,
        'asientos_por_tipo': asientos_por_tipo,
        'reservas_vuelo': reservas_vuelo,
        'total_asientos': total_asientos,
        'asientos_disponibles_count': asientos_disponibles_count,
        'asientos_ocupados_count': asientos_ocupados_count,
        'porcentaje_ocupacion': porcentaje_ocupacion,
        'puede_reservar': puede_reservar,
        'precios_por_tipo': precios_por_tipo,
    }
    
    return render(request, 'vuelos/detalle_vuelo.html', context)


def buscar_vuelos(request):
    """
    Vista para buscar vuelos con criterios específicos.
    
    Permite búsqueda avanzada por múltiples criterios.
    Incluye búsqueda por GET y POST.
    """
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    vuelos = Vuelo.objects.filter(estado='programado')
    
    if request.method == 'POST':
        # Búsqueda por POST (formulario)
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        fecha_desde = request.POST.get('fecha_desde')
        fecha_hasta = request.POST.get('fecha_hasta')
        pasajeros = request.POST.get('pasajeros', 1)
        tipo_asiento = request.POST.get('tipo_asiento')
        
        # Aplicar filtros
        if origen:
            vuelos = vuelos.filter(origen__icontains=origen)
        if destino:
            vuelos = vuelos.filter(destino__icontains=destino)
        if fecha_desde:
            vuelos = vuelos.filter(fecha_salida__date__gte=fecha_desde)
        if fecha_hasta:
            vuelos = vuelos.filter(fecha_salida__date__lte=fecha_hasta)
        
        # Filtrar por disponibilidad de asientos
        if pasajeros:
            vuelos = vuelos.filter(
                avion__asientos__estado='disponible'
            ).distinct()
        
        # Filtrar por tipo de asiento
        if tipo_asiento:
            vuelos = vuelos.filter(
                avion__asientos__tipo=tipo_asiento,
                avion__asientos__estado='disponible'
            ).distinct()
        
        context = {
            'vuelos': vuelos,
            'origen': origen,
            'destino': destino,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'pasajeros': pasajeros,
            'tipo_asiento': tipo_asiento,
            'resultados_encontrados': vuelos.count(),
        }
        
        return render(request, 'vuelos/resultados_busqueda.html', context)
    
    else:
        # Búsqueda por GET (parámetros en URL)
        origen = request.GET.get('origen')
        destino = request.GET.get('destino')
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        precio_min = request.GET.get('precio_min')
        precio_max = request.GET.get('precio_max')
        orden = request.GET.get('orden', 'fecha_salida')
        
        # Aplicar filtros
        if origen:
            vuelos = vuelos.filter(origen__icontains=origen)
        if destino:
            vuelos = vuelos.filter(destino__icontains=destino)
        if fecha_desde:
            vuelos = vuelos.filter(fecha_salida__date__gte=fecha_desde)
        if fecha_hasta:
            vuelos = vuelos.filter(fecha_salida__date__lte=fecha_hasta)
        if precio_min:
            vuelos = vuelos.filter(precio_base__gte=precio_min)
        if precio_max:
            vuelos = vuelos.filter(precio_base__lte=precio_max)
        
        # Ordenamiento
        if orden == 'precio':
            vuelos = vuelos.order_by('precio_base')
        elif orden == 'precio_desc':
            vuelos = vuelos.order_by('-precio_base')
        elif orden == 'duracion':
            vuelos = vuelos.order_by('duracion')
        else:
            vuelos = vuelos.order_by('fecha_salida')
        
        # Paginación para resultados
        paginator = Paginator(vuelos, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'vuelos': page_obj,
            'origen': origen,
            'destino': destino,
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'precio_min': precio_min,
            'precio_max': precio_max,
            'orden': orden,
            'resultados_encontrados': vuelos.count(),
        }
        
        return render(request, 'vuelos/buscar_vuelos.html', context)


@staff_required
def lista_aviones(request):
    """
    Vista para mostrar la lista de aviones (solo para administradores).
    
    Requiere permisos de staff para acceder.
    """
    aviones = Avion.objects.all().order_by('modelo')
    
    context = {
        'aviones': aviones,
    }
    
    return render(request, 'vuelos/lista_aviones.html', context)


@staff_required
def detalle_avion(request, avion_id):
    """
    Vista para mostrar los detalles de un avión específico.
    
    Incluye información del avión y sus asientos.
    """
    avion = get_object_or_404(Avion, id=avion_id)
    asientos = avion.asientos.all().order_by('fila', 'columna')
    
    context = {
        'avion': avion,
        'asientos': asientos,
    }
    
    return render(request, 'vuelos/detalle_avion.html', context)


def asientos_avion(request, avion_id):
    """
    Vista para mostrar la configuración de asientos de un avión.
    
    Útil para seleccionar asientos al hacer reservas.
    """
    avion = get_object_or_404(Avion, id=avion_id)
    asientos = avion.asientos.all().order_by('fila', 'columna')
    
    context = {
        'avion': avion,
        'asientos': asientos,
    }
    
    return render(request, 'vuelos/asientos_avion.html', context)


def verificar_disponibilidad(request, asiento_id):
    """
    Vista API para verificar la disponibilidad de un asiento específico.
    
    Retorna JSON con el estado del asiento y validaciones de negocio.
    """
    from django.utils import timezone
    
    asiento = get_object_or_404(Asiento, id=asiento_id)
    vuelo_id = request.GET.get('vuelo_id')
    
    # Verificar disponibilidad básica del asiento
    disponible_basico = asiento.estado == 'disponible'
    
    # Verificar disponibilidad para un vuelo específico
    disponible_vuelo = True
    reserva_existente = None
    
    if vuelo_id:
        try:
            vuelo = Vuelo.objects.get(id=vuelo_id)
            reserva_existente = Reserva.objects.filter(
                vuelo=vuelo,
                asiento=asiento,
                estado__in=['pendiente', 'confirmada']
            ).first()
            
            if reserva_existente:
                disponible_vuelo = False
                
        except Vuelo.DoesNotExist:
            disponible_vuelo = False
    
    # Verificar si el asiento está en mantenimiento
    en_mantenimiento = asiento.estado == 'mantenimiento'
    
    # Calcular precio del asiento si hay vuelo
    precio_asiento = None
    if vuelo_id:
        try:
            vuelo = Vuelo.objects.get(id=vuelo_id)
            from decimal import Decimal
            precios_por_tipo = {
                'primera': vuelo.precio_base * Decimal('2.5'),
                'premium': vuelo.precio_base * Decimal('1.8'),
                'economica': vuelo.precio_base,
            }
            precio_asiento = precios_por_tipo.get(asiento.tipo, vuelo.precio_base)
        except Vuelo.DoesNotExist:
            pass
    
    data = {
        'asiento_id': asiento.id,
        'numero': asiento.numero,
        'fila': asiento.fila,
        'columna': asiento.columna,
        'estado': asiento.estado,
        'tipo': asiento.tipo,
        'disponible_basico': disponible_basico,
        'disponible_vuelo': disponible_vuelo,
        'disponible': disponible_basico and disponible_vuelo,
        'en_mantenimiento': en_mantenimiento,
        'precio': precio_asiento,
        'reserva_existente': reserva_existente.codigo_reserva if reserva_existente else None,
        'timestamp': timezone.now().isoformat(),
    }
    
    return JsonResponse(data)


def test_translation(request):
    """
    Vista para probar las traducciones del sistema.
    
    Muestra diferentes textos traducidos y permite cambiar el idioma.
    """
    from django.utils import timezone
    
    context = {
        'current_date': timezone.now().date(),
        'current_time': timezone.now().time(),
    }
    
    return render(request, 'test_translation.html', context)
