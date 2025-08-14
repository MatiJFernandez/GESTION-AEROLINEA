"""
Vistas para la aplicación usuarios.

Este archivo contiene todas las vistas relacionadas con:
- Autenticación de usuarios
- Registro de usuarios
- Gestión de perfiles
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import Usuario
from .forms import UsuarioRegistroForm, UsuarioPerfilForm, LoginForm

# Traducción
from django.utils.translation import activate, get_language, deactivate


class HomeView(View):
    """Vista para la página principal"""
    
    def get(self, request):
        return render(request, 'usuarios/home.html')


class LogoutView(View):
    """Vista para cerrar sesión"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'Sesión cerrada exitosamente')
        return redirect('usuarios:login')


class RegisterView(View):
    """Vista para registro de usuarios"""
    
    def get(self, request):
        form = UsuarioRegistroForm()
        return render(
            request,
            'usuarios/registro.html',
            {"form": form}
        )

    def post(self, request):
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data["username"])
            user = Usuario.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                telefono=form.cleaned_data.get('telefono', '')
            )

            subject = "Registro exitoso"
            message = render_to_string(
                'usuarios/mails/welcome.html',
                {'email': user.email}
            )
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)

            messages.success(
                request,
                "Usuario registrado correctamente"
            )
            return redirect('usuarios:login')
        
        return render(
            request,
            'usuarios/registro.html',
            {"form": form}
        )


class LoginView(View):
    """Vista para inicio de sesión"""
    
    def get(self, request):
        form = LoginForm()
        return render(
            request,
            'usuarios/login.html',
            {"form": form}
        )

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request, 
                username=username, 
                password=password
            )

            if user is not None: 
                login(request, user)
                messages.success(request, "Sesión iniciada")
                return redirect("vuelos:home")
            else:
                messages.error(request, "El usuario o contraseña no coinciden")
                
        return render(
            request, 
            "usuarios/login.html", 
            {'form': form}
        )


class ProfileView(View):
    """Vista para editar perfil de usuario"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        form = UsuarioPerfilForm(instance=request.user)
        return render(
            request,
            'usuarios/perfil.html',
            {"form": form}
        )

    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        form = UsuarioPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente")
            return redirect('usuarios:perfil')
        
        return render(
            request,
            'usuarios/perfil.html',
            {"form": form}
        )


# Mantener las vistas de función para compatibilidad (opcional)
def login_view(request):
    """Vista para inicio de sesión (compatibilidad)"""
    return LoginView().get(request) if request.method == 'GET' else LoginView().post(request)

def register_view(request):
    """Vista para registro de usuarios (compatibilidad)"""
    return RegisterView().get(request) if request.method == 'GET' else RegisterView().post(request)

def logout_view(request):
    """Vista para cerrar sesión (compatibilidad)"""
    return LogoutView().get(request)

def profile_view(request):
    """Vista para editar perfil (compatibilidad)"""
    return ProfileView().get(request) if request.method == 'GET' else ProfileView().post(request)


class EditarPerfilView(View):
    """Vista para editar el perfil del usuario"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        form = UsuarioPerfilForm(instance=request.user)
        return render(request, 'usuarios/editar_perfil.html', {'form': form})
    
    def post(self, request):
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('usuarios:login')
            
        form = UsuarioPerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('usuarios:perfil')
        
        return render(request, 'usuarios/editar_perfil.html', {'form': form})
