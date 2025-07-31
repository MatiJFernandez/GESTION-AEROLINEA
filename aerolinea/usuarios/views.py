"""
Vistas para la aplicación usuarios.

Este archivo contiene todas las vistas relacionadas con:
- Autenticación (login, logout, registro)
- Gestión de perfiles de usuario
- Cambio de contraseña
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Usuario
from .forms import UsuarioRegistroForm, UsuarioPerfilForm

def login_view(request):
    """
    Vista para el login de usuarios.
    
    Incluye redirección inteligente y validaciones adicionales.
    """
    # Redirigir si ya está autenticado
    if request.user.is_authenticated:
        return redirect('vuelos:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Configurar sesión según "recordarme"
            if not remember_me:
                request.session.set_expiry(0)  # Sesión expira al cerrar navegador
            
            messages.success(request, f'¡Bienvenido, {user.get_full_name()}!')
            
            # Redirigir a la página anterior o página principal
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            else:
                return redirect('vuelos:home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    context = {
        'next': request.GET.get('next'),
    }
    
    return render(request, 'usuarios/login.html', context)

def logout_view(request):
    """Vista para el logout de usuarios"""
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('vuelos:home')

def registro(request):
    """
    Vista para el registro de nuevos usuarios.
    
    Incluye validaciones adicionales y configuración de roles.
    """
    # Redirigir si ya está autenticado
    if request.user.is_authenticated:
        return redirect('vuelos:home')
    
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Asignar rol por defecto (cliente)
            if not user.rol:
                user.rol = 'cliente'
            
            user.save()
            
            # Autenticar al usuario
            login(request, user)
            
            messages.success(request, f'¡Registro exitoso! Bienvenido, {user.get_full_name()}.')
            
            # Redirigir según el rol
            if user.rol == 'admin':
                return redirect('admin:index')
            else:
                return redirect('vuelos:home')
    else:
        form = UsuarioRegistroForm()
    
    context = {
        'form': form,
        'roles_disponibles': [
            ('cliente', 'Cliente'),
            ('empleado', 'Empleado'),
        ]
    }
    
    return render(request, 'usuarios/registro.html', context)

@login_required
def perfil(request):
    """
    Vista para mostrar el perfil del usuario.
    
    Incluye información personal, estadísticas y opciones de gestión.
    """
    user = request.user
    
    # Obtener estadísticas del usuario
    from reservas.models import Reserva
    from pasajeros.models import Pasajero
    
    # Reservas del usuario (si es pasajero)
    reservas_usuario = []
    try:
        pasajero = Pasajero.objects.get(email=user.email)
        reservas_usuario = pasajero.reservas.all().order_by('-fecha_reserva')[:5]
    except Pasajero.DoesNotExist:
        pass
    
    # Estadísticas
    total_reservas = len(reservas_usuario)
    reservas_activas = sum(1 for r in reservas_usuario if r.estado in ['pendiente', 'confirmada'])
    
    context = {
        'user': user,
        'reservas_usuario': reservas_usuario,
        'total_reservas': total_reservas,
        'reservas_activas': reservas_activas,
    }
    
    return render(request, 'usuarios/perfil.html', context)

@login_required
def editar_perfil(request):
    """Vista para editar el perfil del usuario"""
    if request.method == 'POST':
        form = UsuarioPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
    else:
        form = UsuarioPerfilForm(instance=request.user)
    
    return render(request, 'usuarios/editar_perfil.html', {'form': form})

@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Contraseña cambiada exitosamente.')
            return redirect('usuarios:perfil')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'usuarios/cambiar_password.html', {'form': form})
