"""
Vistas para la aplicación reservas.

Este archivo contiene todas las vistas relacionadas con:
- Gestión de reservas
- Creación de reservas
- Gestión de boletos
- Consulta de reservas
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from usuarios.decorators import reservation_owner_required, active_flight_required
from aerolinea.logging_config import log_reservation_action, log_user_action
from .models import Reserva, Boleto
from vuelos.models import Vuelo, Asiento
from pasajeros.models import Pasajero
from .forms import ReservaForm

def lista_reservas(request):
    """Vista para mostrar la lista de reservas"""
    # Optimización: incluir relaciones en una sola consulta
    reservas = Reserva.objects.select_related(
        'vuelo__avion', 'pasajero', 'asiento'
    ).all().order_by('-fecha_reserva')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        reservas = reservas.filter(estado=estado)
    
    context = {
        'reservas': reservas,
        'estado': estado,
    }
    
    return render(request, 'reservas/lista_reservas.html', context)

@login_required
def crear_reserva(request):
    """
    Vista para crear una nueva reserva.
    
    Proceso complejo que incluye selección de vuelo, asiento y pasajero.
    """
    from django.core.paginator import Paginator
    
    # Paso 1: Seleccionar vuelo
    vuelo_id = request.GET.get('vuelo_id')
    if vuelo_id:
        vuelo = get_object_or_404(Vuelo, id=vuelo_id, estado='programado')
    else:
        # Mostrar lista de vuelos disponibles con optimización
        vuelos = Vuelo.objects.select_related('avion').filter(
            estado='programado'
        ).order_by('fecha_salida')
        paginator = Paginator(vuelos, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'vuelos': page_obj,
            'paso': 'seleccionar_vuelo',
        }
        return render(request, 'reservas/seleccionar_vuelo.html', context)
    
    # Paso 2: Seleccionar asiento
    asiento_id = request.GET.get('asiento_id')
    if not asiento_id:
        # Mostrar asientos disponibles del vuelo
        asientos_disponibles = vuelo.avion.asientos.filter(estado='disponible')
        
        context = {
            'vuelo': vuelo,
            'asientos_disponibles': asientos_disponibles,
            'paso': 'seleccionar_asiento',
        }
        return render(request, 'reservas/seleccionar_asiento.html', context)
    
    # Paso 3: Seleccionar/crear pasajero
    pasajero_id = request.GET.get('pasajero_id')
    if not pasajero_id:
        # Mostrar formulario para seleccionar o crear pasajero
        pasajeros = Pasajero.objects.all().order_by('apellido', 'nombre')
        
        context = {
            'vuelo': vuelo,
            'asiento_id': asiento_id,
            'pasajeros': pasajeros,
            'paso': 'seleccionar_pasajero',
        }
        return render(request, 'reservas/seleccionar_pasajero.html', context)
    
    # Paso 4: Crear la reserva
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            from django.db import transaction
            from django.utils import timezone
            import uuid
            
            try:
                with transaction.atomic():
                    # Verificar que el vuelo existe y está activo
                    vuelo = Vuelo.objects.select_for_update().get(
                        id=vuelo.id, 
                        estado='programado'
                    )
                    
                    # Verificar que el asiento está disponible
                    asiento = Asiento.objects.select_for_update().get(
                        id=asiento_id,
                        estado='disponible',
                        avion=vuelo.avion
                    )
                    
                    # Verificar que el pasajero no tiene otra reserva en ese vuelo
                    pasajero = Pasajero.objects.get(id=pasajero_id)
                    reserva_existente = Reserva.objects.filter(
                        vuelo=vuelo,
                        pasajero=pasajero,
                        estado__in=['pendiente', 'confirmada']
                    ).first()
                    
                    if reserva_existente:
                        raise ValueError(f'El pasajero ya tiene una reserva activa en este vuelo: {reserva_existente.codigo_reserva}')
                    
                    # Verificar que el asiento no está reservado para este vuelo
                    asiento_reservado = Reserva.objects.filter(
                        vuelo=vuelo,
                        asiento=asiento,
                        estado__in=['pendiente', 'confirmada']
                    ).first()
                    
                    if asiento_reservado:
                        raise ValueError(f'El asiento {asiento.numero} ya está reservado para este vuelo')
                    
                    # Crear la reserva
                    reserva = form.save(commit=False)
                    reserva.vuelo = vuelo
                    reserva.asiento = asiento
                    reserva.pasajero = pasajero
                    
                    # Calcular precio si no se especifica
                    if not reserva.precio:
                        reserva.precio = vuelo.precio_base
                    
                    # Generar código único de reserva
                    reserva.codigo_reserva = f"RES-{uuid.uuid4().hex[:8].upper()}"
                    
                    # Establecer fecha de vencimiento (24 horas)
                    reserva.fecha_vencimiento = timezone.now() + timezone.timedelta(hours=24)
                    
                    # Guardar la reserva
                    reserva.save()
                    
                    # Actualizar estado del asiento
                    asiento.estado = 'reservado'
                    asiento.save()
                    
                    # Loggear la acción
                    log_reservation_action(
                        reservation=reserva,
                        action='Reserva creada',
                        user=request.user,
                        details=f'Vuelo: {vuelo.origen}→{vuelo.destino}, Asiento: {asiento.numero}'
                    )
                    
                    messages.success(request, f'Reserva {reserva.codigo_reserva} creada exitosamente.')
                    return redirect('reservas:detalle_reserva', reserva_id=reserva.id)
                    
            except Vuelo.DoesNotExist:
                messages.error(request, 'El vuelo seleccionado no está disponible.')
                return redirect('vuelos:lista_vuelos')
            except Asiento.DoesNotExist:
                messages.error(request, 'El asiento seleccionado no está disponible.')
                return redirect('vuelos:detalle_vuelo', vuelo_id=vuelo.id)
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('vuelos:detalle_vuelo', vuelo_id=vuelo.id)
            except Exception as e:
                messages.error(request, f'Error al crear la reserva: {str(e)}')
                return redirect('vuelos:detalle_vuelo', vuelo_id=vuelo.id)
    else:
        # Pre-llenar el formulario
        initial_data = {
            'vuelo': vuelo,
            'asiento': asiento_id,
            'pasajero': pasajero_id,
            'precio': vuelo.precio_base,
        }
        form = ReservaForm(initial=initial_data)
    
    context = {
        'form': form,
        'vuelo': vuelo,
        'asiento_id': asiento_id,
        'pasajero_id': pasajero_id,
        'paso': 'confirmar_reserva',
    }
    
    return render(request, 'reservas/crear_reserva.html', context)

def detalle_reserva(request, reserva_id):
    """Vista para mostrar los detalles de una reserva"""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    context = {
        'reserva': reserva,
    }
    
    return render(request, 'reservas/detalle_reserva.html', context)

@login_required
@reservation_owner_required
def editar_reserva(request, reserva_id):
    """Vista para editar una reserva"""
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('reservas:detalle_reserva', reserva_id=reserva.id)
    else:
        form = ReservaForm(instance=reserva)
    
    context = {
        'form': form,
        'reserva': reserva,
    }
    
    return render(request, 'reservas/editar_reserva.html', context)

@login_required
@reservation_owner_required
def cancelar_reserva(request, reserva_id):
    """
    Vista para cancelar una reserva.
    
    Incluye lógica de cancelación con validaciones y liberación de recursos.
    """
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == 'POST':
        if reserva.puede_cancelar():
            # Cancelar la reserva
            reserva.estado = 'cancelada'
            reserva.save()
            
            # Liberar el asiento
            reserva.asiento.estado = 'disponible'
            reserva.asiento.save()
            
            # Cancelar boleto si existe
            if hasattr(reserva, 'boleto'):
                reserva.boleto.estado = 'cancelado'
                reserva.boleto.save()
            
            # Calcular reembolso si aplica
            reembolso = 0
            if reserva.precio:
                # Política de reembolso: 80% si se cancela más de 24h antes
                from django.utils import timezone
                tiempo_restante = reserva.vuelo.fecha_salida - timezone.now()
                if tiempo_restante.total_seconds() > 86400:  # 24 horas
                    reembolso = reserva.precio * 0.8
                else:
                    reembolso = reserva.precio * 0.5
            
            messages.success(
                request, 
                f'Reserva cancelada exitosamente. Reembolso: ${reembolso:.2f}'
            )
        else:
            messages.error(request, 'No se puede cancelar esta reserva.')
        
        return redirect('reservas:detalle_reserva', reserva_id=reserva.id)
    
    # Calcular información de cancelación
    puede_cancelar = reserva.puede_cancelar()
    reembolso = 0
    
    if puede_cancelar and reserva.precio:
        from django.utils import timezone
        tiempo_restante = reserva.vuelo.fecha_salida - timezone.now()
        if tiempo_restante.total_seconds() > 86400:  # 24 horas
            reembolso = reserva.precio * 0.8
        else:
            reembolso = reserva.precio * 0.5
    
    context = {
        'reserva': reserva,
        'puede_cancelar': puede_cancelar,
        'reembolso': reembolso,
    }
    
    return render(request, 'reservas/cancelar_reserva.html', context)

@login_required
@reservation_owner_required
def confirmar_reserva(request, reserva_id):
    """
    Vista para confirmar una reserva.
    
    Incluye lógica para generar boleto automáticamente con transacciones.
    """
    from django.db import transaction
    from django.utils import timezone
    import uuid
    
    reserva = get_object_or_404(Reserva, id=reserva_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Verificar que la reserva existe y está pendiente
                reserva = Reserva.objects.select_for_update().get(
                    id=reserva_id,
                    estado='pendiente'
                )
                
                # Verificar que el vuelo sigue activo
                if reserva.vuelo.estado != 'programado':
                    raise ValueError('El vuelo ya no está disponible para confirmación.')
                
                # Verificar que el asiento sigue disponible
                if reserva.asiento.estado != 'reservado':
                    raise ValueError('El asiento ya no está disponible.')
                
                # Verificar que no ha expirado la reserva
                if timezone.now() > reserva.fecha_vencimiento:
                    raise ValueError('La reserva ha expirado.')
                
                # Confirmar la reserva
                reserva.estado = 'confirmada'
                reserva.save()
                
                # Marcar el asiento como ocupado
                reserva.asiento.estado = 'ocupado'
                reserva.asiento.save()
                
                # Loggear la acción
                log_reservation_action(
                    reservation=reserva,
                    action='Reserva confirmada',
                    user=request.user,
                    details=f'Boleto generado: {boleto.codigo_barra}'
                )
                
                # Crear boleto automáticamente
                boleto, created = Boleto.objects.get_or_create(
                    reserva=reserva,
                    defaults={
                        'codigo_barra': f"BOL-{uuid.uuid4().hex[:12].upper()}",
                        'estado': 'emitido',
                        'puerta_embarque': 'Por asignar',
                        'hora_embarque': reserva.vuelo.fecha_salida.replace(
                            hour=reserva.vuelo.fecha_salida.hour - 1,
                            minute=0,
                            second=0,
                            microsecond=0
                        )
                    }
                )
                
                if created:
                    messages.success(request, f'Reserva confirmada y boleto {boleto.codigo_barra} generado exitosamente.')
                else:
                    messages.success(request, 'Reserva confirmada exitosamente.')
                    
        except Reserva.DoesNotExist:
            messages.error(request, 'La reserva no está disponible para confirmación.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f'Error al confirmar la reserva: {str(e)}')
        
        return redirect('reservas:detalle_reserva', reserva_id=reserva_id)
    
    # Verificar si se puede confirmar
    puede_confirmar = (
        reserva.estado == 'pendiente' and
        reserva.vuelo.estado == 'programado' and
        timezone.now() <= reserva.fecha_vencimiento
    )
    
    context = {
        'reserva': reserva,
        'puede_confirmar': puede_confirmar,
        'tiempo_restante': reserva.fecha_vencimiento - timezone.now() if puede_confirmar else None,
    }
    
    return render(request, 'reservas/confirmar_reserva.html', context)

def lista_boletos(request):
    """Vista para mostrar la lista de boletos"""
    boletos = Boleto.objects.all().order_by('-fecha_emision')
    
    # Filtros
    estado = request.GET.get('estado')
    if estado:
        boletos = boletos.filter(estado=estado)
    
    context = {
        'boletos': boletos,
        'estado': estado,
    }
    
    return render(request, 'reservas/lista_boletos.html', context)

def detalle_boleto(request, boleto_id):
    """Vista para mostrar los detalles de un boleto"""
    boleto = get_object_or_404(Boleto, id=boleto_id)
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'reservas/detalle_boleto.html', context)

@login_required
def emitir_boleto(request, boleto_id):
    """Vista para emitir un boleto"""
    boleto = get_object_or_404(Boleto, id=boleto_id)
    
    if request.method == 'POST':
        if boleto.reserva.estado == 'confirmada':
            boleto.estado = 'emitido'
            boleto.save()
            messages.success(request, 'Boleto emitido exitosamente.')
        else:
            messages.error(request, 'Solo se pueden emitir boletos para reservas confirmadas.')
        
        return redirect('reservas:detalle_boleto', boleto_id=boleto.id)
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'reservas/emitir_boleto.html', context)

def imprimir_boleto(request, boleto_id):
    """Vista para imprimir un boleto"""
    boleto = get_object_or_404(Boleto, id=boleto_id)
    
    context = {
        'boleto': boleto,
    }
    
    return render(request, 'reservas/imprimir_boleto.html', context)

def buscar_reservas(request):
    """Vista para buscar reservas"""
    query = request.GET.get('q', '')
    reservas = []
    
    if query:
        reservas = Reserva.objects.filter(
            codigo_reserva__icontains=query
        ) | Reserva.objects.filter(
            pasajero__nombre__icontains=query
        ) | Reserva.objects.filter(
            pasajero__apellido__icontains=query
        )
    
    context = {
        'reservas': reservas,
        'query': query,
    }
    
    return render(request, 'reservas/buscar_reservas.html', context)

def reserva_por_codigo(request, codigo):
    """Vista para buscar una reserva por código"""
    try:
        reserva = Reserva.objects.get(codigo_reserva=codigo)
        return redirect('reservas:detalle_reserva', reserva_id=reserva.id)
    except Reserva.DoesNotExist:
        messages.error(request, f'No se encontró una reserva con el código {codigo}.')
        return redirect('reservas:buscar_reservas')

def verificar_disponibilidad(request):
    """Vista API para verificar disponibilidad de asientos"""
    vuelo_id = request.GET.get('vuelo_id')
    asiento_id = request.GET.get('asiento_id')
    
    if vuelo_id and asiento_id:
        try:
            vuelo = Vuelo.objects.get(id=vuelo_id)
            asiento = Asiento.objects.get(id=asiento_id, avion=vuelo.avion)
            
            # Verificar si el asiento está disponible
            disponible = asiento.estado == 'disponible'
            
            return JsonResponse({
                'disponible': disponible,
                'asiento': asiento.numero,
                'tipo': asiento.tipo,
            })
        except (Vuelo.DoesNotExist, Asiento.DoesNotExist):
            return JsonResponse({'error': 'Vuelo o asiento no encontrado'})
    
    return JsonResponse({'error': 'Parámetros incompletos'})

@login_required
def mi_historial(request):
    """Vista para mostrar el historial de reservas del usuario actual"""
    reservas = Reserva.objects.filter(
        pasajero__email=request.user.email
    ).order_by('-fecha_reserva')
    
    context = {
        'reservas': reservas,
    }
    
    return render(request, 'reservas/mi_historial.html', context)
