"""
Vistas para la aplicación pasajeros.

Este archivo implementa la capa de vistas del patrón Vista-Servicio-Repositorio.
Las vistas manejan las peticiones HTTP y delegan la lógica de negocio a los servicios.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import models
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from .models import Pasajero
from .forms import PasajeroForm
from .services.pasajeros import PasajeroService

class PasajeroList(View):
    """Vista para mostrar la lista de pasajeros"""
    
    def __init__(self):
        self.pasajero_service = PasajeroService()
    
    def get(self, request):
        # Obtener criterios de búsqueda
        criterios = {}
        query = request.GET.get('q')
        if query:
            criterios['query'] = query
        
        # Usar servicio para obtener pasajeros
        pasajeros = self.pasajero_service.buscar_pasajeros(criterios)
        
        context = {
            'pasajeros': pasajeros,
            'query': query,
        }
        
        return render(request, 'pasajeros/lista_pasajeros.html', context)

class PasajeroCreate(View):
    """
    Vista para registrar un nuevo pasajero.
    
    Incluye validaciones adicionales y verificación de documento.
    """
    
    def __init__(self):
        self.pasajero_service = PasajeroService()
    
    def get(self, request):
        form = PasajeroForm()
        context = {
            'form': form,
            'tipos_documento': [
                ('DNI', 'Documento Nacional de Identidad'),
                ('PASAPORTE', 'Pasaporte'),
                ('CEDULA', 'Cédula de Identidad'),
            ]
        }
        return render(request, 'pasajeros/registro_pasajero.html', context)

    def post(self, request):
        form = PasajeroForm(request.POST)
        if form.is_valid():
            try:
                # Usar servicio para crear pasajero
                datos_pasajero = form.cleaned_data
                pasajero = self.pasajero_service.crear_pasajero(datos_pasajero)
                
                # Crear mensaje de éxito con información adicional
                mensaje = f'Pasajero {pasajero.get_nombre_completo()} registrado exitosamente.'
                if pasajero.es_mayor_de_edad():
                    mensaje += ' Es mayor de edad.'
                else:
                    mensaje += ' Es menor de edad.'
                
                messages.success(request, mensaje)
                
                # Redirigir según el contexto
                if request.user.is_authenticated:
                    return redirect('pasajeros:detalle_pasajero', pasajero_id=pasajero.id)
                else:
                    return redirect('usuarios:login')
                    
            except ValidationError as e:
                messages.error(request, str(e))
        
        context = {
            'form': form,
            'tipos_documento': [
                ('DNI', 'Documento Nacional de Identidad'),
                ('PASAPORTE', 'Pasaporte'),
                ('CEDULA', 'Cédula de Identidad'),
            ]
        }
        return render(request, 'pasajeros/registro_pasajero.html', context)

class PasajeroDetail(View):
    """
    Vista para mostrar los detalles de un pasajero.
    
    Incluye información personal, historial de reservas y estadísticas.
    """
    
    def get(self, request, pasajero_id):
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        
        # Obtener historial de reservas del pasajero
        reservas = pasajero.reservas.all().order_by('-fecha_reserva')
        
        # Calcular estadísticas
        total_reservas = reservas.count()
        reservas_confirmadas = reservas.filter(estado='confirmada').count()
        reservas_canceladas = reservas.filter(estado='cancelada').count()
        reservas_completadas = reservas.filter(estado='completada').count()
        
        # Obtener vuelos frecuentes
        vuelos_frecuentes = pasajero.reservas.values('vuelo__origen', 'vuelo__destino').annotate(
            count=models.Count('id')
        ).order_by('-count')[:5]
        
        # Verificar permisos de edición
        puede_editar = request.user.is_authenticated and (
            request.user.is_staff or 
            request.user.email == pasajero.email
        )
        
        context = {
            'pasajero': pasajero,
            'reservas': reservas[:10],  # Últimas 10 reservas
            'total_reservas': total_reservas,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_canceladas': reservas_canceladas,
            'reservas_completadas': reservas_completadas,
            'vuelos_frecuentes': vuelos_frecuentes,
            'puede_editar': puede_editar,
        }
        
        return render(request, 'pasajeros/detalle_pasajero.html', context)

class PasajeroUpdate(View):
    """Vista para editar un pasajero"""
    
    def get(self, request, pasajero_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        form = PasajeroForm(instance=pasajero)
        
        context = {
            'form': form,
            'pasajero': pasajero,
        }
        
        return render(request, 'pasajeros/editar_pasajero.html', context)

    def post(self, request, pasajero_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        form = PasajeroForm(request.POST, instance=pasajero)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Pasajero actualizado exitosamente.')
            return redirect('pasajeros:detalle_pasajero', pasajero_id=pasajero.id)
        
        context = {
            'form': form,
            'pasajero': pasajero,
        }
        
        return render(request, 'pasajeros/editar_pasajero.html', context)

class PasajeroDelete(View):
    """Vista para eliminar un pasajero"""
    
    def get(self, request, pasajero_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        
        context = {
            'pasajero': pasajero,
        }
        
        return render(request, 'pasajeros/eliminar_pasajero.html', context)

    def post(self, request, pasajero_id):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        pasajero = get_object_or_404(Pasajero, id=pasajero_id)
        nombre = pasajero.get_nombre_completo()
        pasajero.delete()
        messages.success(request, f'Pasajero {nombre} eliminado exitosamente.')
        return redirect('pasajeros:lista_pasajeros')

class PasajeroSearch(View):
    """
    Vista para buscar pasajeros.
    
    Permite búsqueda avanzada con múltiples criterios.
    """
    
    def get(self, request):
        from django.core.paginator import Paginator
        from django.db.models import Q
        
        query = request.GET.get('q', '')
        tipo_busqueda = request.GET.get('tipo', 'nombre')
        pasajeros = Pasajero.objects.all()
        
        if query:
            if tipo_busqueda == 'nombre':
                pasajeros = pasajeros.filter(
                    Q(nombre__icontains=query) | Q(apellido__icontains=query)
                )
            elif tipo_busqueda == 'documento':
                pasajeros = pasajeros.filter(documento__icontains=query)
            elif tipo_busqueda == 'email':
                pasajeros = pasajeros.filter(email__icontains=query)
            else:
                # Búsqueda general
                pasajeros = pasajeros.filter(
                    Q(nombre__icontains=query) |
                    Q(apellido__icontains=query) |
                    Q(documento__icontains=query) |
                    Q(email__icontains=query)
                )
        
        # Ordenamiento
        orden = request.GET.get('orden', 'apellido')
        if orden == 'nombre':
            pasajeros = pasajeros.order_by('nombre', 'apellido')
        elif orden == 'documento':
            pasajeros = pasajeros.order_by('documento')
        elif orden == 'fecha_nacimiento':
            pasajeros = pasajeros.order_by('fecha_nacimiento')
        else:
            pasajeros = pasajeros.order_by('apellido', 'nombre')
        
        # Paginación
        paginator = Paginator(pasajeros, 15)  # 15 pasajeros por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'pasajeros': page_obj,
            'query': query,
            'tipo_busqueda': tipo_busqueda,
            'orden': orden,
            'resultados_encontrados': pasajeros.count(),
        }
        
        return render(request, 'pasajeros/buscar_pasajeros.html', context)

class VerificarDocumento(View):
    """Vista API para verificar si un documento ya existe"""
    
    def get(self, request):
        documento = request.GET.get('documento')
        
        if documento:
            existe = Pasajero.objects.filter(documento=documento).exists()
            return JsonResponse({'existe': existe})
        
        return JsonResponse({'error': 'Documento no proporcionado'})

# Mantener las vistas de función para compatibilidad (opcional)
def lista_pasajeros(request):
    """Vista para mostrar la lista de pasajeros (compatibilidad)"""
    return PasajeroList().get(request)

def registro_pasajero(request):
    """Vista para registrar un nuevo pasajero (compatibilidad)"""
    view = PasajeroCreate()
    if request.method == 'POST':
        return view.post(request)
    return view.get(request)

def detalle_pasajero(request, pasajero_id):
    """Vista para mostrar los detalles de un pasajero (compatibilidad)"""
    return PasajeroDetail().get(request, pasajero_id)

@login_required
def editar_pasajero(request, pasajero_id):
    """Vista para editar un pasajero (compatibilidad)"""
    view = PasajeroUpdate()
    if request.method == 'POST':
        return view.post(request, pasajero_id)
    return view.get(request, pasajero_id)

@login_required
def eliminar_pasajero(request, pasajero_id):
    """Vista para eliminar un pasajero (compatibilidad)"""
    view = PasajeroDelete()
    if request.method == 'POST':
        return view.post(request, pasajero_id)
    return view.get(request, pasajero_id)

def buscar_pasajeros(request):
    """Vista para buscar pasajeros (compatibilidad)"""
    return PasajeroSearch().get(request)

def verificar_documento(request):
    """Vista API para verificar si un documento ya existe (compatibilidad)"""
    return VerificarDocumento().get(request)
