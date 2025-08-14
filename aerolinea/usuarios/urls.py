"""
URLs para la aplicación usuarios.

Este archivo define todas las rutas relacionadas con:
- Autenticación (login, logout, registro)
- Gestión de perfiles de usuario
- Cambio de contraseña
- Recuperación de contraseña
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Namespace para la aplicación usuarios
app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path(
        route='login/', 
        view=views.LoginView.as_view(), 
        name='login'
    ),
    path(
        route='logout/', 
        view=views.LogoutView.as_view(), 
        name='logout'
    ),
    path(
        route='registro/', 
        view=views.RegisterView.as_view(), 
        name='registro'
    ),
    
    # Gestión de perfil
    path(
        route='perfil/', 
        view=views.ProfileView.as_view(), 
        name='perfil'
    ),
    path(
        route='editar-perfil/', 
        view=views.EditarPerfilView.as_view(), 
        name='editar_perfil'
    ),
    
    # URLs de compatibilidad (mantener las vistas de función)
    path('login-func/', views.login_view, name='login_func'),
    path('logout-func/', views.logout_view, name='logout_func'),
    path('registro-func/', views.register_view, name='registro_func'),
    path('perfil-func/', views.profile_view, name='perfil_func'),
    
    # Recuperación de contraseña
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='usuarios/password_reset.html',
             email_template_name='usuarios/password_reset_email.html',
             subject_template_name='usuarios/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='usuarios/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='usuarios/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='usuarios/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
] 